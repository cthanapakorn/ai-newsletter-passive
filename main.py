import os
import yfinance as yf
import feedparser
import google.generativeai as genai
from datetime import datetime
import webbrowser

# ==========================================
# 1. ฟังก์ชันดึงข้อมูลหุ้น (แก้บั๊กตัวเลขเพี้ยน)
# ==========================================
def get_stock_data(tickers):
    stock_data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            
            if not hist.empty:
                last_price = round(hist['Close'].iloc[-1], 2)
            else:
                last_price = "N/A"
                
            info = stock.info
            dy = info.get('dividendYield')
            if dy is not None:
                div_yield = f"{dy * 100:.2f}%"
            else:
                div_yield = "N/A"
                
            stock_data.append({"Symbol": ticker, "Price": last_price, "Yield": div_yield})
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            stock_data.append({"Symbol": ticker, "Price": "Error", "Yield": "Error"})
            
    return stock_data

# ==========================================
# 2. ฟังก์ชันกวาดข่าว
# ==========================================
def get_market_news(rss_url, limit=10):
    try:
        news_feed = feedparser.parse(rss_url)
        return [{"Title": entry.title, "Link": entry.link} for entry in news_feed.entries[:limit]]
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

# ==========================================
# 3. ให้ AI สร้างหน้าเว็บ (บังคับข้อมูลเป๊ะๆ)
# ==========================================
def generate_html_dashboard(stock_data, news_data, api_key):
    print("\n[ กำลังให้ AI จัดหน้าเว็บ... อาจใช้เวลา 15-20 วินาที ]")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # ดึงวันที่ปัจจุบัน
    today_date = datetime.now().strftime("%d/%m/%Y")
    
    raw_data = f"วันที่ปัจจุบัน: {today_date}\nข้อมูลหุ้นล่าสุด: {stock_data}\n\nพาดหัวข่าววันนี้:\n"
    for idx, news in enumerate(news_data, 1):
        raw_data += f"{idx}. {news['Title']}\n"
        
    prompt = f"""
    {raw_data}
    ---
    คำสั่ง: คุณคือนักพัฒนาเว็บไซต์ สร้างไฟล์ HTML5 แบบ Single Page สำหรับ 'AI Wealth Dashboard'
    
    โครงสร้างและดีไซน์:
    1. ใช้ CSS (<style>) ตกแต่งให้ดูเป็น Financial Dashboard ระดับโปร (เช่น พื้นหลังสีเข้ม ตัวหนังสือสีสว่าง)
    2. Header: แสดงชื่อ "AI Wealth Newsletter" และระบุ 'วันที่อัปเดต' ตามข้อมูลที่ให้ไป
    3. Section 1: ตารางหรือการ์ดแสดงราคาหุ้นและปันผลของ AAPL, MSFT, NVDA, TSLA
    4. Section 2: บทสรุปผู้บริหาร สรุปข่าวและผลกระทบ
    
    ⚠️ กฎเหล็กที่ห้ามฝ่าฝืน:
    - ห้ามสร้างหรือแต่งตัวเลขราคาหุ้นและปันผลขึ้นมาเองเด็ดขาด! ให้ใช้ตัวเลขจาก 'ข้อมูลหุ้นล่าสุด' ที่ส่งให้เท่านั้น
    - ห้ามใช้เครื่องหมาย Markdown ```html ครอบโค้ด ให้ตอบกลับมาเป็นโค้ด HTML ล้วนๆ เริ่มที่ <html>
    """
    
    response = model.generate_content(prompt)
    return response.text.replace("```html", "").replace("```", "").strip()

# ==========================================
# 4. ระบบควบคุมหลัก (รันและเปิดเว็บอัตโนมัติ)
# ==========================================
if __name__ == "__main__":
    # ใส่ API Key ของคุณเรียบร้อยแล้ว
    GEMINI_API_KEY = "AIzaSyAkufv0PaTlyIUXUo3mFfIdOa-YLKrn6TY" 
    
    print("🚀 เริ่มดูดข้อมูลตลาด...")
    stocks = get_stock_data(["AAPL", "MSFT", "NVDA", "TSLA"])
    news = get_market_news("[https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL,MSFT,NVDA,TSLA,QQQ](https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL,MSFT,NVDA,TSLA,QQQ)")
    
    html_content = generate_html_dashboard(stocks, news, GEMINI_API_KEY)
    
    # บันทึกเป็นไฟล์ index.html
    file_path = os.path.abspath("index.html")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_content)
        
    print("✅ สร้างไฟล์เสร็จแล้ว! กำลังเปิดหน้าเว็บให้คุณดู...")
    
    # สั่งเปิดหน้าเว็บผ่าน Browser ทันที
    webbrowser.open(f"file://{file_path}")
