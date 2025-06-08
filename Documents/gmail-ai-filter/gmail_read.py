from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pandas as pd

# Gmail API 권한 범위
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# 중요도 분류 함수
def classify_importance(subject, snippet):
    text = (subject + " " + snippet).lower()

    if any(word in text for word in [
        'unsubscribe', 'promotion', 'sale', 'deal', 'discount','shopping', 'exclusive', '혜택', '광고', '특가', '이벤트'
    ]):
        return 1  # 광고

    if any(word in text for word in [
        'welcome', '가입', 'thank you', 'thanks for joining', 'signed up', '회원가입'
    ]):
        return 2  # 가입 관련

    if any(word in text for word in [
        'order', 'purchase', '배송', 'order number', 'receipt', '구매', 'shipped', 'your item', '결제'
    ]):
        return 3  # 구매

    if any(word in text for word in [
        'meeting', 'invite', '일정', '참석', '공지', 'conference', 'calendar', 'schedule'
    ]):
        return 4  # 일정 관련

    if any(word in text for word in [
        'submit', '제출', 'action required', 'feedback', 'survey', '응답', 'form', 'required'
    ]):
        return 5  # 응답 요청

    return 3  # 기본값 (일반 메일)

def main():
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=creds)

    data = []
    next_page_token = None
    total_count = 0
    target_count = 2000

    while total_count < target_count:
        results = service.users().messages().list(
            userId='me',
            maxResults=500,
            pageToken=next_page_token
        ).execute()

        messages = results.get('messages', [])
        next_page_token = results.get('nextPageToken')

        for msg in messages:
            if total_count >= target_count:
                break

            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = msg_data['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(제목 없음)')
            snippet = msg_data.get('snippet', '')

            label = classify_importance(subject, snippet)

            data.append({
                'subject': subject,
                'snippet': snippet,
                'importance': label
            })

            total_count += 1

        if not next_page_token:
            break  # 더 이상 데이터가 없음

    # 저장
    df = pd.DataFrame(data)
    df = df[df['snippet'].notnull() & (df['snippet'].str.strip() != '')]
    df["text"] = df["subject"].fillna('') + " " + df["snippet"].fillna('')
    df_final = df[["text", "importance"]]
    df_final.to_csv("data.csv", index=False, encoding="utf-8-sig")
    print(f"✅ 저장 완료: data.csv ({len(df_final)}개)")


if __name__ == '__main__':
    main()
