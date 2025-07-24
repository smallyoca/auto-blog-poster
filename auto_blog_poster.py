import os
import openai
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 從環境變數讀取 OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("請設定環境變數 OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# Blogger API 權限範圍
SCOPES = ['https://www.googleapis.com/auth/blogger']

# Blogger Blog ID 從環境變數讀取，確保安全
BLOG_ID = os.getenv("BLOG_ID")
if not BLOG_ID:
    raise ValueError("請設定環境變數 BLOG_ID")

def get_blogger_service():
    creds = None

    # token.json 用於存授權後的 token
    # 建議你先在本機執行一次程式完成授權後，再把 token.json 放到安全的位置

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # 若無有效憑證，執行授權流程 (只建議本機測試時用)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # 把 token 保存到本地檔案
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    service = build('blogger', 'v3', credentials=creds)
    return service

def generate_article(tool_name):
    prompt = f"""請幫我寫一篇SEO優化的文章，標題為「【AI工具推薦】{tool_name} 使用教學與評測」。文章要包含以下段落：
1. 什麼是 {tool_name}？
2. 優點與缺點
3. 使用教學步驟
4. 適合的使用者群
5. 總結推薦

文章語氣專業且易懂，約500字。"""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=800,
    )
    return response['choices'][0]['message']['content']

def post_article(title, content):
    service = get_blogger_service()
    posts = service.posts()
    body = {
        "title": title,
        "content": content
    }
    post = posts.insert(blogId=BLOG_ID, body=body).execute()
    print(f"成功發文：{post['url']}")

if __name__ == "__main__":
    # 這裡填入你要產文的 AI 工具清單
    tools = ["ChatGPT", "DALL·E 2", "Midjourney", "Copy.ai"]

    for tool in tools:
        print(f"開始產生文章：{tool}")
        article = generate_article(tool)
        title = f"【AI工具推薦】{tool} 使用教學與評測"
        post_article(title, article)
