# Facebook 粉絲專頁爬蟲工具

這是一個基於 Selenium 和 BeautifulSoup 的 Facebook 粉絲專頁貼文爬蟲工具，具有友好的 PyQt5 圖形使用者界面。

## 功能特色

- 🔐 **自動登入 Facebook** - 支援模擬人類打字行為避免偵測
- 🍪 **智慧登入狀態** - 自動保存Cookie，7天內無需重複登入
- 📱 **多粉絲專頁支援** - 可同時爬取多個粉絲專頁的貼文
- 🎯 **精準資料擷取** - 爬取貼文內容、按讚數、留言數、分享數、發布時間等
- 🧹 **智慧資料清理** - 自動清理日期格式，移除多餘字符和分享資訊
- 📖 **完整內容展開** - 自動點擊「查看更多」按鈕，獲取完整貼文內容
- 🖥️ **友善圖形界面** - 使用 PyQt5 製作的現代化界面
- 📊 **即時進度顯示** - 爬取過程中可查看即時進度和狀態
- 💾 **CSV 格式輸出** - 結果自動儲存為 CSV 格式，方便後續分析
- 🔄 **邊抓取邊保存** - 每抓取一定數量貼文自動保存，避免資料丟失
- 🛡️ **強化錯誤處理** - 先進的彈窗關閉機制，提高爬取穩定性
- ⚡ **防偵測機制** - 內建多種反偵測技術，提高爬取成功率

## 系統需求

- Python 3.7 或更高版本
- Windows 10/11 (已測試)
- Microsoft Edge 或 Google Chrome 瀏覽器

## 安裝步驟

### 📚 詳細安裝指南

**🚀 首次使用？請先閱讀我們的詳細設置指南：**
- **[📋 詳細設置指南 (DETAILED_SETUP_GUIDE.md)](./DETAILED_SETUP_GUIDE.md)** 
  - 從 Python 安裝開始的完整流程
  - **特別包含 macOS 版本的詳細設置**
  - Windows、macOS、Linux 三平台支援
  - 常見問題排除和進階設定

### 快速安裝（已有Python環境）

### 1. 建立虛擬環境（推薦）

```bash
# Windows
python -m venv facebook_scraper_env
facebook_scraper_env\Scripts\activate

# macOS/Linux
python3 -m venv facebook_scraper_env
source facebook_scraper_env/bin/activate
```

### 2. 安裝 Python 套件

```bash
pip install -r requirements.txt
```

### 3. 安裝瀏覽器驅動程式

#### 選項 A：使用 Microsoft Edge (推薦)
- 確保您的電腦已安裝 Microsoft Edge 瀏覽器
- Edge WebDriver 通常會自動管理，無需額外安裝

#### 選項 B：使用 Google Chrome
- 下載對應版本的 ChromeDriver：https://chromedriver.chromium.org/
- 將 chromedriver.exe 放置在專案的 `chromedriver-win64` 資料夾中
- 或將 ChromeDriver 加入系統 PATH

## 使用方法

### 啟動圖形界面

```bash
python facebook_scraper_gui.py
```

### 操作步驟

1. **輸入 Facebook 登入資訊**
   - 在「Email」欄位輸入您的 Facebook 帳號
   - 在「密碼」欄位輸入您的 Facebook 密碼

2. **選擇瀏覽器**
   - 推薦使用「Microsoft Edge」，因為時間戳擷取更準確
   - 也可選擇「Google Chrome」

3. **設定爬取目標**
   - 在「粉絲專頁網址」區域輸入要爬取的粉絲專頁網址
   - 每行輸入一個網址，例如：
     ```
     https://www.facebook.com/cnn
     https://www.facebook.com/bbc
     https://www.facebook.com/nytimes
     ```

4. **設定爬取數量**
   - 在「每個專頁爬取貼文數量」設定想要爬取的貼文數量（1-1000篇）

5. **開始爬取**
   - 點擊「開始爬取」按鈕
   - 程式會自動開啟瀏覽器、登入 Facebook 並開始爬取
   - 您可以在「執行日誌」區域查看即時狀態

6. **儲存結果**
   - 爬取完成後，點擊「儲存結果」按鈕
   - 選擇儲存位置和檔案名稱
   - 結果將以 CSV 格式儲存

### 測試「查看更多」優化功能 🧪

專門的測試腳本用於驗證新的智慧滾動和按鈕處理功能：

#### Windows:
```cmd
python test_see_more_optimization.py
```

#### macOS:
```bash
python3 test_see_more_optimization.py
```

**測試腳本特色：**
- 🧪 專門測試「查看更多」按鈕處理效果
- 📊 提供詳細的內容完整性分析  
- 📈 統計長貼文比例和平均內容長度
- 💡 給出優化建議和評估結果
- ⏱️ 顯示處理速度和效率統計

### 程式化使用（進階用戶）

如果您想要直接使用爬蟲類別：

```python
from facebook_fan_page_scraper import FacebookPageScraper

# 初始化爬蟲
scraper = FacebookPageScraper("your_email@example.com", "your_password")

# 設定自動保存回調函數（可選）
def save_callback(message):
    print(f"💾 {message}")

scraper.save_callback = save_callback

try:
    # 初始化瀏覽器
    scraper.initialize_driver()
    
    # 登入 Facebook
    scraper.login()
    
    # 前往粉絲專頁
    scraper.navigate_to_page("https://www.facebook.com/cnn")
    
    # 爬取 10 篇貼文（會自動分批保存，智慧處理「查看更多」）
    posts = scraper.scrape_posts(10)
    
    # 儲存最終結果（自動合併部分檔案）
    scraper.save_to_csv("cnn_posts.csv")
    
finally:
    # 關閉瀏覽器
    scraper.close()
```

## 爬取資料格式

爬取的 CSV 檔案包含以下欄位：

| 欄位名稱   | 說明         |
| ---------- | ------------ |
| post_text  | 貼文內容文字 |
| likes      | 按讚數       |
| comments   | 留言數       |
| shares     | 分享數       |
| post_time  | 貼文發布時間 |
| post_url   | 貼文連結     |
| scraped_at | 爬取時間戳記 |

## 注意事項

### 使用限制
- 此工具僅適用於爬取**公開**的 Facebook 粉絲專頁
- 請遵守 Facebook 的使用條款和相關法律法規
- 建議使用 VPN 以提高爬取成功率
- 避免頻繁大量爬取，以免觸發 Facebook 的反爬蟲機制

### 自動保存功能
- 程式會每抓取 5 篇貼文自動保存一次（可在程式碼中調整間隔）
- 爬取過程中會產生多個部分檔案，避免因錯誤導致資料丟失
- 爬取完成後可選擇合併所有部分檔案為單一檔案
- 部分檔案可作為備份保留，或選擇自動清理

### 智慧登入功能
- 程式會自動保存登入狀態（Cookie），有效期為7天
- 同一帳號下次執行時無需重新輸入密碼，直接快速登入
- Cookie檔案會自動檢查有效性，過期或帳號不符時會自動清理
- 提供安全可靠的登入狀態管理，提升使用體驗

### 內容展開功能（最新優化！🚀）

#### 智慧「查看更多」處理系統
- **精確文字匹配**：只點擊確切的「查看更多」文字標籤（支援中英文）
- **智慧內容合併**：點擊展開後自動重新抓取，確保保存完整內容而非截斷版本
- **四階段處理流程**：初始掃描 → 滾動處理 → 深度檢查 → 最終清理
- **內容品質驗證**：自動驗證新內容確實比舊內容更完整
- **零重複處理**：避免重複點擊，提高處理效率

#### 實際效果
- **處理前**：「今天天氣真好，我們去了公園...查看更多」（45字符）
- **處理後**：「今天天氣真好，我們去了公園散步，看到了很多美麗的花朵...」（78字符）

📋 **詳細技術說明**：[智慧合併機制說明.md](./智慧合併機制說明.md)
- **智慧滾動策略**：採用非常緩慢的持續滾動（100px步長），確保每個「查看更多」都被發現
- **零遺漏保證**：緩慢滾動策略配合智慧合併機制，確保完整內容展開
- **多重檢測機制**：支援多種語言：「查看更多」、「See More」、「See more」
- **內容品質保證**：每次點擊後重新抓取並智慧合併，確保內容完整性
- **詳細日誌追蹤**：實時顯示點擊統計，讓您了解處理進度
- **自動ESC防護**：點擊後自動發送ESC鍵，防止意外彈出貼文詳情視窗
- **四階段處理**：初始加載 → 智慧滾動 → 深度檢查 → 最終清理
- 確保爬取**完整**的貼文內容，解決內容截斷問題

### 強化彈窗處理
- **快速響應**：縮短等待時間，進入頁面後立即檢查彈窗
- **多重關閉機制**：結合按鈕點擊、body點擊、ESC鍵、JavaScript強制關閉
- **智慧偵測**：使用JavaScript檢查剩餘遮蔽層數量
- **預防性處理**：即使未找到明顯彈窗也執行預防性關閉操作

### 常見問題

**Q: 登入失敗怎麼辦？**
- 確認帳號密碼正確
- 檢查是否需要通過兩步驟驗證
- 嘗試先在瀏覽器中手動登入 Facebook

**Q: 爬取過程中瀏覽器被關閉？**
- 這可能是 Facebook 的反爬蟲機制
- 建議降低爬取頻率或使用 VPN
- 嘗試更換不同的網路環境

**Q: 無法爬取到資料？**
- 確認粉絲專頁網址正確
- 確認專頁是公開可見的
- 檢查網路連線狀況

## 🔍 技術背景與替代方案分析

### 為什麼不使用 Facebook Graph API？

**🚫 官方 API 限制**：
- **無法取得公開粉絲專頁貼文**：自2018年Cambridge Analytica事件後，Facebook大幅限縮Graph API權限
- **需要企業驗證**：取得頁面貼文權限需要通過複雜的企業審核流程
- **資料存取限制**：即使通過審核，也無法取得歷史貼文和完整互動數據
- **成本考量**：企業級API使用需要付費，且有嚴格的使用配額限制

**📊 實際測試結果**：
```
Graph API 可取得：❌ 無法取得粉絲專頁公開貼文
本工具可取得：✅ 完整貼文內容、互動數據、時間戳記
```

### 為什麼現有的爬蟲套件都無法使用？

**📦 主流套件現況**：

1. **facebook-scraper (python)**
   - ❌ 2023年後無法正常運作
   - ❌ Facebook更新反爬蟲機制後失效

2. **facebook-sdk**
   - ❌ 官方SDK，受限於Graph API權限問題
   - ❌ 無法取得公開粉絲專頁內容

3. **selenium-facebook-scraper**
   - ❌ 大部分已過時，無法應對新版Facebook介面
   - ❌ 缺乏現代化的反偵測機制

4. **beautifulsoup + requests**
   - ❌ 無法處理Facebook的動態載入內容
   - ❌ 無法處理登入驗證和反爬蟲機制

**🔄 Facebook持續更新的挑戰**：
- **介面結構變更**：Facebook定期更新HTML結構，破壞現有爬蟲
- **反爬蟲技術升級**：加強偵測自動化行為，封鎖爬蟲程式
- **動態載入機制**：採用React和複雜的JavaScript動態載入
- **安全機制強化**：加入更多驗證步驟和安全檢查

### 🛠️ 為什麼需要自己開發Selenium解決方案？

**✅ 現代化自動化工具的優勢**：

1. **Selenium WebDriver**
   - ✅ 模擬真實瀏覽器行為，難以被偵測
   - ✅ 支援JavaScript動態內容載入
   - ✅ 可處理複雜的互動操作（點擊、滾動、輸入）

2. **BeautifulSoup 精確解析**
   - ✅ 強大的HTML解析能力
   - ✅ 靈活的選擇器支援
   - ✅ 可應對複雜的網頁結構

3. **反偵測技術整合**
   - ✅ User-Agent偽裝
   - ✅ 行為模擬（人類打字速度、隨機等待）
   - ✅ WebDriver痕跡移除

**🎯 本工具的核心優勢**：
```python
# 官方API無法做到的事情
posts = scraper.scrape_posts(100)  # ✅ 取得100篇公開貼文
完整內容 = posts[0]['post_text']    # ✅ 包含完整文字內容
互動數據 = posts[0]['likes']        # ✅ 即時按讚數、留言數、分享數
時間資訊 = posts[0]['post_time']    # ✅ 精確的發布時間
```

**🔧 持續維護與更新**：
- 本專案會持續監控Facebook介面變更
- 及時更新選擇器和爬取策略
- 社群回饋機制，快速修復問題

## 免責聲明

此工具僅供學習和研究目的使用。使用者應當：

1. 遵守 Facebook 的服務條款
2. 遵守當地法律法規
3. 尊重他人的智慧財產權
4. 不得將爬取的資料用於商業用途或其他不當目的

開發者不對使用此工具可能產生的任何法律責任承擔責任。

## 技術參考

本專案參考了以下文章的技術方案：
- [Scraping Facebook in 2025: Combining Selenium and BeautifulSoup for Effective Data Extraction](https://medium.com/@AbdelRhman_Sabry/scraping-facebook-in-2025-combining-selenium-and-beautifulsoup-for-effective-data-extraction-95bc8d705889)

## 版本資訊

- **版本**: 1.2.0
- **更新日期**: 2025年1月
- **相容性**: Python 3.7+, Windows 10/11
- **最新功能**: 
  - 🍪 智慧Cookie登入系統
  - 📖 智慧「查看更多」內容展開（可見性檢查 + ESC防護）
  - 🧹 智慧日期格式清理
  - 🛡️ 強化彈窗處理機制（快速響應 + 多重關閉）
  - 🚀 效能優化：縮短等待時間，提升爬取速度 