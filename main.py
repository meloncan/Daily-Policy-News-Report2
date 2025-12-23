import os
import re
import requests
import pandas as pd
import smtplib
import markdown
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import unquote
from mistralai import Mistral

DATA_GO_KR_KEY = os.environ.get("DATA_GO_KR_KEY")
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

if not all([DATA_GO_KR_KEY, MISTRAL_API_KEY, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL]):
    raise ValueError("환경 변수가 설정되지 않았습니다.")

client = Mistral(api_key=MISTRAL_API_KEY)

def fetch_policy_news():
    today = datetime.now()
    end_date = today.strftime("%Y%m%d")
    start_date = (today - timedelta(days=7)).strftime("%Y%m%d")

    url = "https://apis.data.go.kr/1371000/policyNewsService/policyNewsList"
    params = {
        "serviceKey": unquote(DATA_GO_KR_KEY),
        "startDate": start_date,
        "endDate": end_date,
        "numOfRows": 50
    }

    response = requests.get(url, params=params, timeout=30)
    root = ET.fromstring(response.text)
    items = root.findall(".//item") or [el for el in root.iter() if el.tag.endswith("item")]

    data = []
    for item in items:
        content_tag = item.find("DataContents")
        content = content_tag.text if content_tag is not None else ""
        clean_content = re.sub(r'<[^>]+>', '', content).strip() if content else ""
        data.append({
            "Title": item.findtext("Title"),
            "ApproveDate": item.findtext("ApproveDate"),
            "Content": clean_content
        })

    return pd.DataFrame(data)

def generate_report(df):
    context_list = []
    for idx, row in df.head(10).iterrows():
        prompt = f"기사 제목: {row['Title']}\n기사 내용: {row['Content'][:1500]}"
        resp = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        context_list.append(resp.choices[0].message.content)

    report_prompt = "\n".join(context_list)
    resp = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": report_prompt}]
    )
    return resp.choices[0].message.content

def send_email(report_md):
    html_content = markdown.markdown(report_md)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[주간 정책 보고서] {datetime.now().strftime('%Y-%m-%d')}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

if __name__ == "__main__":
    df = fetch_policy_news()
    if not df.empty:
        report = generate_report(df)
        send_email(report)
