from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import joblib
# Gmail API 권한 범위
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


# 사전 학습된 모델과 벡터라이저 로드
model = joblib.load("importance_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

def classify_importance(subject, snippet):
    text = subject + " " + snippet
    vector = vectorizer.transform([text])
    prediction = model.predict(vector)[0]
    return int(prediction)


def main():
    # OAuth 인증 시작
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)

    # Gmail API 클라이언트 생성
    service = build('gmail', 'v1', credentials=creds)

    # 최근 메일 5개 가져오기
    results = service.users().messages().list(userId='me', maxResults=5).execute()
    messages = results.get('messages', [])

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()

        # 제목 찾기
        headers = msg_data['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(제목 없음)')

        # 본문 요약 가져오기
        snippet = msg_data.get('snippet', '')

        print(f"[제목] {subject}")
        print(f"[내용 요약] {snippet}")
        print("=" * 60)
        # 중요도 분류
        importance = classify_importance(subject, snippet)
        print(f"[중요도] ⭐️ {importance}")


if __name__ == '__main__':
    main()