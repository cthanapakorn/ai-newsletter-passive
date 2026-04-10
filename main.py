import os
import yfinance as yf
import feedparser
import google.generativeai as genai

# ==========================================
# 1. ฟังก์ชันดึงข้อมูลหุ้น (US Market)
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
# 2. ฟังก์ชันกวาดข่าวการเงินและเทคโนโลยี
# ==========================================
def get_market_news(rss_url, limit=10):
    news_feed = feedparser.parse(rss_url)
    return [{"Title": entry.title, "Link": entry.link} for entry in news_feed.entries[:limit]]

# ==========================================
# 3. ให้ AI สร้างหน้าเว็บ (Web Developer AI)
# ==========================================
def generate_html_dashboard(stock_data, news_data, api_key):
    print("\n[ กำลังให้ AI เขียนโค้ดหน้าเว็บ... ]")
    genai.configure(api_key=api_key)
    
    # ใช้โมเดลรุ่นใหม่ล่าสุด (รวดเร็วและฉลาดขึ้น)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    raw_data = f"ข้อมูลหุ้นล่าสุด: {stock_data}\n\nพาดหัวข่าววันนี้:\n"
    for idx, news in enumerate(news_data, 1):
        raw_data += f"{idx}. {news['Title']}\n"
        
    prompt = f"""
    {raw_data}
    ---
    คำสั่ง: คุณคือนักพัฒนาเว็บไซต์และนักวิเคราะห์การลงทุน สร้างไฟล์ HTML5 แบบ Single Page สำหรับ 'AI Wealth Dashboard'
    
    โครงสร้างและดีไซน์ (ต้องมี):
    1. ใช้ CSS ในแท็ก <style> ให้ดูทันสมัย สะอาดตา โทนสีแบบ Financial Dashboard (เช่น โทนสีเข้ม) รองรับการดูบนมือถือ (Responsive)
    2. Header: แสดงชื่อ "AI Wealth Newsletter" พร้อมวันที่อัปเดต
    3. Section 1 (Market Overview): สร้างการ์ดแสดงราคาหุ้นและปันผลของ AAPL, MSFT, NVDA, TSLA
    4. Section 2 (Executive Summary): สรุปภาพรวมตลาดและผลกระทบต่อหุ้นเทคโนโลยี จากข่าวที่ให้ไป
    5. Section 3 (Disclaimer): คำเตือนการลงทุน
    
    สำคัญมาก: ส่งกลับมาเฉพาะโค้ด HTML เริ่มต้นที่ <html> และจบที่ </html> ห้ามมีเครื่องหมาย Markdown ```html ครอบ
    """
    
    response = model.generate_content(prompt)
    
    # ทำความสะอาดโค้ดเผื่อ AI เผลอใส่ Markdown มาให้
    html_code = response.text.replace("```html", "").replace("```", "").strip()
    return html_code

# ==========================================
# 4. ระบบควบคุมหลัก (Main Execution)
# ==========================================
if __name__ == "__main__":
    # ระบบจะดึงกุญแจลับจาก GitHub Secrets (หรือ Environment Variables บนเครื่อง)
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    
    if not GEMINI_API_KEY:
        print("❌ Error: ไม่พบ GEMINI_API_KEY ในระบบ")
        print("คำแนะนำ: หากรันบน GitHub ให้ไปเพิ่มรหัสผ่านที่แท็บ Settings > Secrets and variables > Actions")
    else:
        print("🚀 เริ่มระบบดึงข้อมูลตลาด...")
        
        # 1. กำหนดรายชื่อหุ้นที่ต้องการติดตาม
        stocks = get_stock_data(["AAPL", "MSFT", "NVDA", "TSLA"])
        
        # 2. กำหนดแหล่งข่าว RSS Feed (Yahoo Finance)
        news = get_market_news("[https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL,MSFT,NVDA,TSLA,QQQ](https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL,MSFT,NVDA,TSLA,QQQ)")
        
        # 3. ให้ AI สร้าง HTML
        html_content = generate_html_dashboard(stocks, news, GEMINI_API_KEY)
        
        # 4. บันทึกเป็นไฟล์ index.html
        with open("index.html", "w", encoding="utf-8") as file:
            file.write(html_content)
            
        print("✅ สร้างไฟล์ index.html สำเร็จ พร้อมโชว์บนหน้าเว็บ!")
