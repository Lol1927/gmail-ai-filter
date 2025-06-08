from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from bs4 import BeautifulSoup
import pandas as pd

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def classify_importance(subject, body):
    text = (subject + " " + body).lower()

    if any(word in text for word in [
        'unsubscribe', 'promotion', 'sale', 'deal', 'discount', 'exclusive', '혜택', '광고', '특가', '이벤트'
    ]):
        return 1  # 광고, 스팸

    if any(word in text for word in [
        'welcome', '가입', 'thank you', 'thanks for joining', 'signed up', '회원가입'
    ]):
        return 2  # 가입 환영

    if any(word in text for word in [
        'order', 'purchase', '배송', 'order number', 'receipt', '구매', 'shipped', 'your item', '결제'
    ]):
        return 3  # 구매, 주문 관련

    if any(word in text for word in [
        'meeting', 'invite', '일정', '참석', '공지', 'conference', 'calendar', 'schedule'
    ]):
        return 4  # 회의, 공지

    if any(word in text for word in [
        'submit', '제출', 'action required', 'feedback', 'survey', '응답', 'form', 'required'
    ]):
        return 5  # 응답 필요

    if any(word in text for word in [
        'reset', 'password', 'security alert', 'login from new device', '계정', '보안', '경고'
    ]):
        return 4  # 계정/보안 관련 → 보통 주의 필요

    return 3  # 기본값


def extract_body(payload):
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
            elif part['mimeType'] == 'text/html':
                data = part['body'].get('data')
                if data:
                    html = base64.urlsafe_b64decode(data).decode('utf-8')
                    soup = BeautifulSoup(html, 'html.parser')
                    return soup.get_text()
    elif payload['mimeType'] == 'text/plain':
        data = payload['body'].get('data')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8')
    return ''

def main():
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=creds)

    results = service.users().messages().list(userId='me', maxResults=50).execute()
    messages = results.get('messages', [])

    dataset = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(제목 없음)')
        body = extract_body(msg_data['payload'])

        label = classify_importance(subject, body)

        dataset.append({
            'subject': subject,
            'body': body,
            'importance': label
        })

    df = pd.DataFrame(dataset)
    df.to_csv("gmail_training_data.csv", index=False, encoding='utf-8-sig')
    print("✅ gmail_training_data.csv 파일로 저장 완료!")

if __name__ == '__main__':
    main()
