# 📰 Weekly Policy Report Automation

공공데이터포털 정책 뉴스를 자동 수집하여  
AI 요약 → 주간 정책 보고서 작성 → 이메일 발송까지  
**GitHub Actions로 매주 자동 실행**하는 프로젝트입니다.

## 📁 프로젝트 구조

```
.
├─ main.py
├─ requirements.txt
└─ .github/
   └─ workflows/
      └─ policy_report.yml
```

## ⚙️ 사전 준비

- Python 3.9 이상
- GitHub Repository
- 공공데이터포털 API Key (Decoding)
- Mistral AI API Key
- Gmail 앱 비밀번호

## 🔐 GitHub Secrets 설정

Repository → Settings → Secrets and variables → Actions

| Name | Description |
|----|----|
| DATA_GO_KR_KEY | 공공데이터포털 Decoding 키 |
| MISTRAL_API_KEY | Mistral API 키 |
| SENDER_EMAIL | 발신 Gmail |
| SENDER_PASSWORD | Gmail 앱 비밀번호 |
| RECEIVER_EMAIL | 수신 이메일 |

## ▶️ 실행 방법

- Actions 탭 → **Weekly Policy Report** → Run workflow
- 또는 매주 월요일 오전 9시(KST) 자동 실행

## 📌 참고

- 요약 대상 뉴스는 최대 10건
- 보고서는 Markdown 기반으로 생성 후 HTML 메일로 발송됩니다
- 모든 실행은 GitHub Actions 서버에서 이루어집니다
