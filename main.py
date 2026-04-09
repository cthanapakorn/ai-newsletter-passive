import os
import yfinance as yf
import feedparser
import pandas as pd
import google.generativeai as genai
import requests

# ==========================================
# 1. ฟังก์ชันดึงข้อมูลราคาหุ้นและเงินปันผล
# ==========================================
def get_stock_data(tickers):
    stock_data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            last_price = round(hist['Close'].iloc[0], 2) if not hist.empty else "N/A"
            info = stock.info
            div_yield = f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else "N/A"
            stock_data.append({"Symbol": ticker, "Price": last_price, "Yield": div_yield})
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
    return stock_data

# ==========================================
# 2. ฟังก์ชันกวาดพาดหัวข่าวล่าสุด
# ==========================================
def get_market_news(rss_url, limit=10):
    news_feed = feedparser.parse(rss_url)
    return [{"Title": entry.title, "Link": entry.link} for entry in news_feed.entries[:limit]]

# ==========================================
# 3. ฟังก์ชันสมองกล AI เขียน Newsletter
# ==========================================
def generate_newsletter(stock_data, news_data, api_key):
    print("\n[ กำลังส่งข้อมูลให้ AI วิเคราะห์... อาจใช้เวลา 10-20 วินาที ]")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    raw_data = f"ข้อมูลหุ้นล่าสุด: {stock_data}\n\nพาดหัวข่าววันนี้:\n"
    for idx, news in enumerate(news_data, 1):
        raw_data += f"{idx}. {news['Title']}\n"
        
    prompt = f"""
    {raw_data}
    ---
    คำสั่ง: คุณคือนักวิเคราะห์การลงทุนระดับโลก หน้าที่ของคุณคืออ่านข้อมูลหุ้นและพาดหัวข่าวด้านบน แล้วเขียน Newsletter สรุปสถานการณ์ตลาดรายวัน
    
    โครงสร้างบทความ:
    1. หัวข้อที่ดึงดูดความสนใจ (ภาษาไทย)
    2. สรุปภาพรวมตลาดวันนี้ (อิงจากข่าว)
    3. ผลกระทบต่อหุ้นเทคโนโลยี (โฟกัสที่ Apple, Microsoft, NVIDIA, Tesla)
    4. คำเตือน (Disclaimer) ว่านี่ไม่ใช่คำแนะนำในการลงทุน
    
    ข้อกำหนด: เขียนด้วยภาษาที่อ่านง่าย เป็นมืออาชีพ น่าเชื่อถือ และวิเคราะห์เฉพาะข้อมูลที่ให้ไปเท่านั้น ห้ามแต่งข้อมูลขึ้นเอง จัดรูปแบบให้อ่านง่ายเมื่อแสดงผลบน LINE
    """
    
    response = model.generate_content(prompt)
    return response.text

# ==========================================
# 4. ฟังก์ชันส่งข้อความเข้า LINE
# ==========================================
def send_line_notify(message, token):
    print("\n[ กำลังส่งข้อความเข้า LINE... ]")
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {token}'}
    data = {'message': f'\n{message}'}
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print("✅ ส่งข้อความเข้า LINE สำเร็จ!")
    else:
        print(f"❌ เกิดข้อผิดพลาดในการส่ง LINE: {response.status_code}")

# ==========================================
# 5. ระบบควบคุมการทำงานหลัก (Main Execution)
# ==========================================
if __name__ == "__main__":
    # ดึงกุญแจลับจากระบบ Environment Variables (ปลอดภัย 100%)
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    LINE_TOKEN = os.environ.get("LINE_TOKEN")
    
    if not GEMINI_API_KEY:
        print("❌ Error: ไม่พบ GEMINI_API_KEY ในระบบ กรุณาตรวจสอบการตั้งค่า Secrets บน GitHub หรือในคอมพิวเตอร์ของคุณ")
    else:
        print("🚀 เริ่มการดึงข้อมูลตลาด...")
        stocks = get_stock_data(["AAPL", "MSFT", "NVDA", "TSLA"])
        news = get_market_news("https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL,MSFT,NVDA,TSLA,QQQ")
        
        # ส่งให้ AI จัดการ
        newsletter_content = generate_newsletter(stocks, news, GEMINI_API_KEY)
        
        # แสดงผลบนหน้าจอ (Terminal / Console)
        print("\n" + "="*50)
        print("📰 AI NEWSLETTER ประจำวันนี้")
        print("="*50 + "\n")
        print(newsletter_content)

        # ส่งเข้า LINE ถ้ามีการตั้งค่า Token ไว้
        if LINE_TOKEN:
            send_line_notify(newsletter_content, LINE_TOKEN)
        else:
            print("\n⚠️ ไม่พบ LINE_TOKEN ข้ามการส่งข้อความเข้าแอป LINE")
