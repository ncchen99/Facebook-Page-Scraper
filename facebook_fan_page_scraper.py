import time
import random
import csv
import json
import pickle
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
import os
import threading


class FacebookPageScraper:
    def __init__(self, email, password, use_edge=True):
        """
        初始化Facebook粉絲專頁爬蟲
        :param email: Facebook登入帳號
        :param password: Facebook登入密碼  
        :param use_edge: 是否使用Edge瀏覽器（推薦，因為時間戳更容易擷取）
        """
        self.email = email
        self.password = password
        self.use_edge = use_edge
        self.driver = None
        self.scraped_posts = []
        self.stop_scraping = False
        self.auto_save_interval = 5  # 每抓取5篇貼文自動保存一次
        self.partial_files = []  # 儲存部分檔案的列表
        self.save_callback = None  # 保存狀態回調函數
        self.cookie_file = "facebook_cookies.pkl"  # Cookie檔案路徑
        self.cookie_expiry_days = 7  # Cookie有效期限（天）

    def initialize_driver(self):
        """初始化網頁瀏覽器驅動"""
        try:
            if self.use_edge:
                options = EdgeOptions()
                # 反偵測設定
                options.add_argument(
                    "--disable-blink-features=AutomationControlled")
                options.add_experimental_option(
                    "excludeSwitches", ["enable-automation"])
                options.add_experimental_option(
                    "useAutomationExtension", False)
                options.add_argument(
                    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59")

                self.driver = webdriver.Edge(options=options)
            else:
                options = ChromeOptions()
                options.add_argument(
                    "--disable-blink-features=AutomationControlled")
                options.add_experimental_option(
                    "excludeSwitches", ["enable-automation"])
                options.add_experimental_option(
                    "useAutomationExtension", False)
                options.add_argument(
                    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

                # 檢查是否有chromedriver
                chromedriver_path = os.path.join(
                    os.getcwd(), "chromedriver-win64", "chromedriver.exe")
                if os.path.exists(chromedriver_path):
                    self.driver = webdriver.Chrome(
                        executable_path=chromedriver_path, options=options)
                else:
                    self.driver = webdriver.Chrome(options=options)

            # 移除webdriver痕跡
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return True

        except Exception as e:
            print(f"瀏覽器初始化失敗: {e}")
            return False

    def simulate_human_typing(self, element, text):
        """模擬人類打字模式"""
        for char in text:
            if self.stop_scraping:
                break
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
            if random.random() < 0.1:
                time.sleep(random.uniform(0.3, 0.7))

    def login(self):
        """登入Facebook（支援Cookie快速登入）"""
        try:
            # 先嘗試使用Cookie登入
            print("嘗試使用已保存的登入狀態...")
            if self.load_cookies():
                # 重新載入頁面以應用cookies
                self.driver.refresh()
                time.sleep(3)

                # 檢查是否成功登入
                if self.is_logged_in():
                    print("✅ 使用Cookie登入成功！")
                    print("🔧 Cookie登入後檢查彈窗...")
                    time.sleep(1)  # 短暫等待
                    self.close_overlay_dialogs()
                    return True
                else:
                    print("Cookie登入失敗，嘗試傳統登入...")

            # 傳統登入流程
            print("正在前往Facebook登入頁面...")
            self.driver.get("https://www.facebook.com/login")

            # 等待並填入email
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            self.simulate_human_typing(email_input, self.email)

            # 等待並填入密碼
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "pass"))
            )
            self.simulate_human_typing(password_input, self.password)

            # 點擊登入按鈕
            login_button = self.driver.find_element(
                By.XPATH, "//button[@type='submit']")
            ActionChains(self.driver)\
                .move_to_element(login_button)\
                .pause(random.uniform(0.2, 0.4))\
                .click()\
                .perform()

            print("登入中，請稍等...")
            time.sleep(15)

            # 檢查是否成功登入
            if "facebook.com" in self.driver.current_url and "login" not in self.driver.current_url:
                print("✅ 帳號密碼登入成功！")

                # 保存cookies供下次使用
                self.save_cookies()

                # 立即處理登入後的彈窗
                print("🔧 處理登入後可能的彈窗...")
                time.sleep(1)  # 短暫等待
                self.close_overlay_dialogs()

                return True
            else:
                print("❌ 登入失敗，請檢查帳號密碼")
                return False

        except Exception as e:
            print(f"❌ 登入過程發生錯誤: {e}")
            return False

    def save_cookies(self):
        """保存當前的cookies到檔案"""
        try:
            cookies = self.driver.get_cookies()
            cookie_data = {
                'cookies': cookies,
                'saved_time': datetime.now().isoformat(),
                'email': self.email  # 保存帳號以便驗證
            }

            with open(self.cookie_file, 'wb') as f:
                pickle.dump(cookie_data, f)

            print(f"✅ Cookies已保存到: {self.cookie_file}")
            if self.save_callback:
                self.save_callback(f"已保存登入狀態，下次可快速登入")

            return True

        except Exception as e:
            print(f"保存cookies時發生錯誤: {e}")
            return False

    def load_cookies(self):
        """從檔案載入cookies"""
        try:
            if not os.path.exists(self.cookie_file):
                print("找不到cookies檔案")
                return False

            with open(self.cookie_file, 'rb') as f:
                cookie_data = pickle.load(f)

            # 檢查cookies是否過期
            saved_time = datetime.fromisoformat(cookie_data['saved_time'])
            if datetime.now() - saved_time > timedelta(days=self.cookie_expiry_days):
                print("Cookies已過期，需要重新登入")
                os.remove(self.cookie_file)  # 刪除過期的cookies
                return False

            # 檢查帳號是否匹配
            if cookie_data.get('email') != self.email:
                print("Cookies帳號不匹配當前帳號")
                return False

            # 先訪問Facebook主頁
            self.driver.get("https://www.facebook.com")
            time.sleep(2)

            # 載入cookies
            for cookie in cookie_data['cookies']:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"載入單個cookie失敗: {e}")
                    continue

            print("✅ Cookies載入成功")
            return True

        except Exception as e:
            print(f"載入cookies時發生錯誤: {e}")
            # 如果載入失敗，刪除問題cookies檔案
            if os.path.exists(self.cookie_file):
                os.remove(self.cookie_file)
            return False

    def is_logged_in(self):
        """檢查是否已經登入"""
        try:
            # 檢查頁面上是否有登入成功的標誌
            self.driver.get("https://www.facebook.com")
            time.sleep(3)

            # 如果頁面包含登入表單，說明未登入
            login_elements = self.driver.find_elements(By.NAME, "email")
            if login_elements:
                return False

            # 檢查是否有用戶菜單或其他登入成功的標誌
            user_menu = self.driver.find_elements(
                By.CSS_SELECTOR, "[data-testid='blue_bar_profile_link']")
            if user_menu:
                return True

            # 檢查網址是否還在login頁面
            if "login" in self.driver.current_url:
                return False

            return True

        except Exception as e:
            print(f"檢查登入狀態時發生錯誤: {e}")
            return False

    def parse_facebook_time(self, time_string):
        """將Facebook各種時間格式轉換為統一格式 YYYY-MM-DD HH:MM"""
        if not time_string or time_string == "未知時間":
            return "未知時間"

        try:
            from datetime import datetime, timedelta
            import re

            current_time = datetime.now()
            time_string = time_string.strip()

            # 處理相對時間格式
            # 匹配「X小時」、「X分鐘」等格式
            relative_pattern = r'(\d+)\s*(小時|分鐘|秒)'
            relative_match = re.search(relative_pattern, time_string)
            if relative_match:
                number = int(relative_match.group(1))
                unit = relative_match.group(2)

                if unit == "小時":
                    target_time = current_time - timedelta(hours=number)
                elif unit == "分鐘":
                    target_time = current_time - timedelta(minutes=number)
                elif unit == "秒":
                    target_time = current_time - timedelta(seconds=number)

                return target_time.strftime("%Y-%m-%d %H:%M")

            # 處理「昨天」格式
            if "昨天" in time_string:
                # 提取時間部分，例如「昨天上午11:21」
                time_pattern = r'(上午|下午)?(\d{1,2}):(\d{2})'
                time_match = re.search(time_pattern, time_string)

                yesterday = current_time - timedelta(days=1)

                if time_match:
                    period = time_match.group(1)  # 上午/下午
                    hour = int(time_match.group(2))
                    minute = int(time_match.group(3))

                    # 處理12小時制
                    if period == "下午" and hour != 12:
                        hour += 12
                    elif period == "上午" and hour == 12:
                        hour = 0

                    target_time = yesterday.replace(
                        hour=hour, minute=minute, second=0, microsecond=0)
                else:
                    # 如果沒有具體時間，設為昨天同一時刻
                    target_time = yesterday

                return target_time.strftime("%Y-%m-%d %H:%M")

            # 處理「X月X日」格式（當年）
            month_day_pattern = r'(\d{1,2})月(\d{1,2})日(?:\s*(上午|下午)?(\d{1,2}):(\d{2}))?'
            month_day_match = re.search(month_day_pattern, time_string)
            if month_day_match:
                month = int(month_day_match.group(1))
                day = int(month_day_match.group(2))
                period = month_day_match.group(3)  # 上午/下午
                hour = int(month_day_match.group(
                    4)) if month_day_match.group(4) else 0
                minute = int(month_day_match.group(
                    5)) if month_day_match.group(5) else 0

                # 處理12小時制
                if period == "下午" and hour != 12:
                    hour += 12
                elif period == "上午" and hour == 12:
                    hour = 0

                # 判斷年份（如果月份大於當前月份，可能是去年）
                year = current_time.year
                if month > current_time.month or (month == current_time.month and day > current_time.day):
                    year = current_time.year - 1

                target_time = datetime(year, month, day, hour, minute)
                return target_time.strftime("%Y-%m-%d %H:%M")

            # 處理「YYYY年X月X日」格式
            full_date_pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日(?:\s*(上午|下午)?(\d{1,2}):(\d{2}))?'
            full_date_match = re.search(full_date_pattern, time_string)
            if full_date_match:
                year = int(full_date_match.group(1))
                month = int(full_date_match.group(2))
                day = int(full_date_match.group(3))
                period = full_date_match.group(4)  # 上午/下午
                hour = int(full_date_match.group(
                    5)) if full_date_match.group(5) else 0
                minute = int(full_date_match.group(
                    6)) if full_date_match.group(6) else 0

                # 處理12小時制
                if period == "下午" and hour != 12:
                    hour += 12
                elif period == "上午" and hour == 12:
                    hour = 0

                target_time = datetime(year, month, day, hour, minute)
                return target_time.strftime("%Y-%m-%d %H:%M")

            # 處理純時間格式「上午11:21」或「下午2:30」（當日）
            time_only_pattern = r'(上午|下午)(\d{1,2}):(\d{2})'
            time_only_match = re.search(time_only_pattern, time_string)
            if time_only_match:
                period = time_only_match.group(1)
                hour = int(time_only_match.group(2))
                minute = int(time_only_match.group(3))

                # 處理12小時制
                if period == "下午" and hour != 12:
                    hour += 12
                elif period == "上午" and hour == 12:
                    hour = 0

                target_time = current_time.replace(
                    hour=hour, minute=minute, second=0, microsecond=0)
                return target_time.strftime("%Y-%m-%d %H:%M")

            # 如果都不匹配，返回原始字串
            print(f"⚠️ 無法解析時間格式: {time_string}")
            return time_string

        except Exception as e:
            print(f"解析時間時發生錯誤: {e}, 原始時間: {time_string}")
            return time_string

    def clean_date_string(self, date_text):
        """清理日期字串，移除多餘字符和分享對象資訊，然後統一格式"""
        if not date_text:
            return "未知時間"

        try:
            # 移除分享對象及之後的內容
            if "分享對象：" in date_text:
                date_text = date_text.split("分享對象：")[0]
            if "·" in date_text:
                date_text = date_text.split("·")[0]

            # 移除多餘的短橫線和空格
            cleaned = re.sub(r'-+', '', date_text)  # 移除所有短橫線
            cleaned = re.sub(r'\s+', ' ', cleaned)  # 將多個空格合併為一個
            cleaned = cleaned.strip()  # 移除首尾空格

            # 如果清理後的字串太短，返回原始字串
            if len(cleaned) < 3:
                return date_text.strip()

            # 使用新的時間解析函數統一格式
            standardized_time = self.parse_facebook_time(cleaned)
            return standardized_time

        except Exception as e:
            print(f"清理日期字串時發生錯誤: {e}")
            return date_text if date_text else "未知時間"

    def close_overlay_dialogs(self):
        """關閉登入後可能出現的遮蔽彈窗"""
        try:
            print("🔍 檢查是否有遮蔽彈窗需要關閉...")

            # 縮短等待時間，更快速檢查
            time.sleep(1.5)

            # 可能的關閉按鈕選擇器
            close_selectors = [
                "div[aria-label='關閉']",
                "div[aria-label='Close']",
                "button[aria-label='關閉']",
                "button[aria-label='Close']",
                "div[role='button'][aria-label='關閉']",
                "div[role='button'][aria-label='Close']",
                "[data-testid='close-button']",
                "div.x92rtbv.x10slt7e.x1c4vz4f.x2lah0s",  # Facebook常見的關閉按鈕樣式
                "svg[aria-label='關閉']",
                "svg[aria-label='Close']"
            ]

            closed_count = 0

            for selector in close_selectors:
                try:
                    # 使用更短的等待時間
                    close_buttons = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, selector))
                    )

                    for button in close_buttons:
                        if button.is_displayed() and button.is_enabled():
                            print(f"✅ 發現並點擊關閉按鈕: {selector}")
                            ActionChains(self.driver)\
                                .move_to_element(button)\
                                .pause(0.3)\
                                .click()\
                                .perform()
                            closed_count += 1
                            time.sleep(0.5)  # 縮短等待時間
                            break
                    else:
                        continue
                    break

                except:
                    # 如果找不到該選擇器就繼續嘗試下一個
                    continue

            # 更強效的彈窗關閉機制
            try:
                # 方法1：直接點擊body元素（更可靠的方式）
                body = self.driver.find_element(By.TAG_NAME, "body")
                ActionChains(self.driver).move_to_element(
                    body).click().perform()
                time.sleep(0.5)
                print("🖱️ 已點擊body元素，嘗試關閉彈窗")

                # 方法2：使用JavaScript點擊空白區域
                self.driver.execute_script("""
                    // 點擊空白區域
                    document.body.click();
                    
                    // 發送多個ESC鍵事件
                    for(let i = 0; i < 3; i++) {
                        document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
                        document.dispatchEvent(new KeyboardEvent('keyup', {key: 'Escape', bubbles: true}));
                    }
                    
                    // 嘗試關閉可能存在的modal
                    var modals = document.querySelectorAll('[role="dialog"], [data-testid="modal"], .modal');
                    modals.forEach(function(modal) {
                        if(modal.style) {
                            modal.style.display = 'none';
                        }
                    });
                """)
                time.sleep(0.5)
                print("🔧 已執行JavaScript彈窗關閉腳本")

                # 方法3：ActionChains發送ESC鍵
                for i in range(2):
                    try:
                        ActionChains(self.driver).send_keys(
                            Keys.ESCAPE).perform()
                        time.sleep(0.3)
                    except:
                        pass

                print("⌨️ 已嘗試多種方式關閉彈窗")

            except Exception as e:
                print(f"⚠️ 彈窗關閉操作失敗: {e}")
                pass

            # 快速檢查是否還有遮蔽層
            try:
                overlay_count = self.driver.execute_script("""
                    var overlays = document.querySelectorAll('[role="dialog"], [data-testid="modal"], .modal, .overlay');
                    var visibleCount = 0;
                    overlays.forEach(function(overlay) {
                        var style = window.getComputedStyle(overlay);
                        if(style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
                            visibleCount++;
                        }
                    });
                    return visibleCount;
                """)

                if overlay_count > 0:
                    print(f"⚠️ 仍檢測到 {overlay_count} 個可能的遮蔽層")
                else:
                    print("✅ 未檢測到明顯的遮蔽層")

            except:
                pass

            if closed_count > 0:
                print(f"✅ 成功關閉了 {closed_count} 個彈窗")
            else:
                print("ℹ️ 未發現明顯彈窗，已執行預防性關閉操作")

            print("✅ 彈窗檢查完成")

        except Exception as e:
            print(f"❌ 關閉遮蔽彈窗時發生錯誤: {e}")

    def navigate_to_page(self, page_url):
        """前往指定的粉絲專頁"""
        try:
            print(f"🌐 正在前往粉絲專頁: {page_url}")
            self.driver.get(page_url)
            time.sleep(2)  # 縮短基本等待時間

            # 立即檢查並關閉可能的彈窗（不等待太久）
            print("🔧 立即檢查頁面彈窗...")
            self.close_overlay_dialogs()

            # 再次確認頁面載入
            time.sleep(1)

            return True
        except Exception as e:
            print(f"❌ 前往粉絲專頁失敗: {e}")
            return False

    def slow_scroll(self, step=100):
        """非常緩慢滾動頁面以載入更多貼文"""
        self.driver.execute_script(f"window.scrollBy(0, {step});")
        time.sleep(0.8)  # 較短的滾動間隔

    def fast_scroll_with_realtime_extract(self, total_distance=1000, step=100, all_posts=None):
        """快速滾動並實時抓取貼文內容（適應Facebook的即時載入機制）"""
        print(f"🔄 開始快速滾動 {total_distance}px（步長 {step}px），實時抓取貼文內容...")

        total_clicked = 0
        current_posts = all_posts if all_posts else []

        steps = total_distance // step
        for i in range(steps):
            if self.stop_scraping:
                break

            # 滾動一步
            self.driver.execute_script(f"window.scrollBy(0, {step});")
            time.sleep(0.3)  # 快速等待載入

            # 每步都點擊「查看更多」並實時抓取內容
            new_clicks, current_posts = self.quick_click_see_more(
                current_posts)
            total_clicked += new_clicks

            # 如果沒有點擊，也要每步抓取當前可見的貼文內容
            if new_clicks == 0 and i % 1 == 0:  # 沒點擊時每步都抓取
                fresh_posts = self.extract_posts_with_bs()
                # 智慧合併，保留最完整的內容
                current_posts = self.smart_merge_posts(
                    current_posts, fresh_posts)

            # 短暫間隔，保持高效率
            time.sleep(random.uniform(0.2, 0.4))

        if total_clicked > 0:
            print(
                f"✅ 本輪滾動總共處理了 {total_clicked} 個「查看更多」文字標籤，實時更新了 {len(current_posts)} 篇貼文")

        return total_clicked, current_posts

    # 向後兼容性別名
    def slow_scroll_with_see_more(self, total_distance=1000, step=100, all_posts=None):
        """向後兼容性方法，實際調用fast_scroll_with_realtime_extract"""
        return self.fast_scroll_with_realtime_extract(total_distance, step, all_posts)

    def quick_click_see_more(self, current_posts=None):
        """快速點擊「查看更多」按鈕並抓取更新內容"""
        try:
            script = """
            var clicked = 0;
            var allElements = document.querySelectorAll('span, div, a');
            
            for(var i = 0; i < allElements.length && clicked < 20; i++) {
                var element = allElements[i];
                var text = (element.innerText || element.textContent || '').trim();
                
                if(text === '查看更多' || text === 'See More' || text === 'See more') {
                    try {
                        var rect = element.getBoundingClientRect();
                        var isVisible = rect.width > 0 && rect.height > 0 && 
                                      rect.top >= 0 && rect.bottom <= window.innerHeight;
                        
                        if(isVisible) {
                            element.click();
                            clicked++;
                        }
                    } catch(e) {}
                }
            }
            return clicked;
            """

            clicked_count = self.driver.execute_script(script)

            # 如果有點擊，等待0.5秒後抓取更新內容
            if clicked_count > 0:
                time.sleep(0.5)
                fresh_posts = self.extract_posts_with_bs()
                if current_posts is not None:
                    # 智慧合併以獲得最新的完整內容
                    updated_posts = self.smart_merge_posts(
                        current_posts, fresh_posts)
                    return clicked_count, updated_posts
                else:
                    return clicked_count, fresh_posts

            return clicked_count, current_posts if current_posts is not None else []

        except Exception as e:
            return 0, current_posts if current_posts is not None else []

    def smart_click_see_more_buttons(self, all_posts=None):
        """簡化版：直接點擊所有可見的「查看更多」文字標籤，並立即抓取更新內容"""
        try:
            clicked_count = 0
            updated_posts = all_posts if all_posts else []

            # 最簡化的JavaScript：找到「查看更多」就直接點擊
            script = """
            var clicked = 0;
            
            // 尋找所有文字元素
            var allElements = document.querySelectorAll('span, div, a');
            
            for(var i = 0; i < allElements.length && clicked < 50; i++) {
                var element = allElements[i];
                var text = (element.innerText || element.textContent || '').trim();
                
                // 精確匹配「查看更多」文字
                if(text === '查看更多' || text === 'See More' || text === 'See more') {
                    try {
                        // 檢查元素是否可見
                        var rect = element.getBoundingClientRect();
                        var isVisible = rect.width > 0 && rect.height > 0;
                        
                        if(isVisible) {
                            // 直接點擊
                            element.click();
                            console.log('成功點擊查看更多:', text);
                            clicked++;
                        }
                    } catch(e) {
                        console.log('點擊失敗:', e);
                    }
                }
            }
            
            return clicked;
            """

            # 執行JavaScript腳本
            clicked_count = self.driver.execute_script(script)

            if clicked_count > 0:
                print(f"✅ 點擊了 {clicked_count} 個「查看更多」文字標籤")

                # 等待更長時間並進行多次驗證
                print("⏳ 等待內容完全展開並驗證...")

                # 進行多輪等待和驗證
                best_posts = None
                for attempt in range(3):  # 最多3次驗證
                    time.sleep(1.5)  # 每次等待1.5秒

                    current_posts = self.extract_posts_with_bs()

                    # 計算當前這批內容中有多少仍包含「查看更多」
                    truncated_count = sum(1 for post in current_posts
                                          if '查看更多' in post.get('post_text', '') or
                                          'See More' in post.get('post_text', '') or
                                          'See more' in post.get('post_text', ''))

                    print(
                        f"🔍 第 {attempt + 1} 次驗證：{len(current_posts)} 篇貼文，{truncated_count} 篇仍截斷")

                    # 如果這次的結果更好（截斷內容更少），就保存
                    if best_posts is None or truncated_count < sum(1 for post in best_posts
                                                                   if '查看更多' in post.get('post_text', '') or
                                                                   'See More' in post.get('post_text', '') or
                                                                   'See more' in post.get('post_text', '')):
                        best_posts = current_posts
                        if truncated_count == 0:
                            print(f"✅ 第 {attempt + 1} 次驗證：所有內容已完全展開！")
                            break

                new_posts = best_posts if best_posts else self.extract_posts_with_bs()

                # 進行智慧合併
                if all_posts is not None:
                    updated_posts = self.smart_merge_posts(
                        all_posts, new_posts)
                    print(f"📊 合併完成：{len(updated_posts)} 篇貼文")
                else:
                    updated_posts = new_posts

            return clicked_count, updated_posts

        except Exception as e:
            print(f"❌ 點擊「查看更多」文字標籤時發生錯誤: {e}")
            return 0, updated_posts

    def click_see_more_buttons(self):
        """點擊頁面上可見的「查看更多」按鈕來展開完整內容（保留舊方法以便向後兼容）"""
        clicks, _ = self.smart_click_see_more_buttons()
        return clicks

    def extract_posts_with_bs(self):
        """使用BeautifulSoup擷取貼文資料"""
        try:
            # 注意：「查看更多」按鈕的點擊現在在滾動過程中進行，這裡不再重複執行
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            posts_data = []

            # 尋找貼文容器
            posts = soup.find_all("div", {"class": "x1n2onr6 x1ja2u2z"})

            for post in posts:
                if self.stop_scraping:
                    break

                try:
                    # 擷取貼文文字內容
                    message_elements = post.find_all(
                        "div", {"data-ad-preview": "message"})
                    post_text = " ".join([msg.get_text(strip=True)
                                         for msg in message_elements])

                    # 擷取按讚數
                    likes_element = post.select_one(
                        "span.xt0b8zv.x1jx94hy.xrbpyxo.xl423tq > span > span")
                    likes = likes_element.get_text(
                        strip=True) if likes_element else "0"

                    # 擷取留言數
                    comments_element = post.select(
                        "div > div > span > div > div > div > span > span.html-span")
                    comments = comments_element[0].text if comments_element else "0"

                    # 擷取分享數
                    shares_element = post.select(
                        "div > div > span > div > div > div > span > span.html-span")
                    shares = shares_element[1].text if len(
                        shares_element) > 1 else "0"

                    # 擷取貼文時間 - 使用 dir="ltr" 標籤，第二個元素是時間
                    post_time = "未知時間"
                    try:
                        # 找到所有 dir="ltr" 的元素
                        ltr_elements = post.find_all(attrs={"dir": "ltr"})
                        if len(ltr_elements) >= 2:
                            # 第二個 dir="ltr" 元素通常是時間
                            time_element = ltr_elements[1]
                            candidate_time = time_element.get_text(strip=True)
                            # 驗證是否為合理的時間格式
                            if candidate_time and len(candidate_time) < 100:
                                post_time = self.clean_date_string(
                                    candidate_time)

                        # 如果通過 dir="ltr" 沒找到合適的時間，使用備用方案
                        if post_time == "未知時間":
                            time_selectors = [
                                "a[role='link'] span[dir='ltr']",
                                "div.xu06os2.x1ok221b > span > div > span > span > a > span",
                                "span[dir='ltr']",
                                "time",
                                "[data-testid='story-subtitle'] span"
                            ]

                            for selector in time_selectors:
                                try:
                                    time_elem = post.select_one(selector)
                                    if time_elem:
                                        candidate_time = time_elem.get_text(
                                            strip=True)
                                        # 檢查是否像時間格式（包含數字且不太長）
                                        if candidate_time and len(candidate_time) < 50 and any(char.isdigit() for char in candidate_time):
                                            post_time = self.clean_date_string(
                                                candidate_time)
                                            break
                                except:
                                    continue
                    except Exception as e:
                        print(f"擷取時間時發生錯誤: {e}")
                        post_time = "未知時間"

                    # 擷取貼文連結
                    link_element = post.select_one(
                        "div.xu06os2.x1ok221b > span > div > span > span > a")
                    post_url = link_element.get('href') if link_element else ""
                    if post_url and not post_url.startswith('http'):
                        post_url = "https://www.facebook.com" + post_url

                    # 只加入有內容的貼文
                    if post_text.strip() or likes != "0" or comments != "0":
                        posts_data.append({
                            "post_text": post_text,
                            "likes": likes,
                            "comments": comments,
                            "shares": shares,
                            "post_time": post_time,
                            "post_url": post_url,
                            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })

                except Exception as e:
                    print(f"擷取單一貼文時發生錯誤: {e}")
                    continue

            return posts_data

        except Exception as e:
            print(f"擷取貼文資料時發生錯誤: {e}")
            return []

    def remove_duplicates(self, data_list):
        """移除重複的貼文"""
        seen = set()
        unique_data = []
        for data in data_list:
            # 使用貼文文字和時間作為唯一識別
            # 支援字典和物件兩種格式
            if isinstance(data, dict):
                identifier = (data.get('post_text', ''),
                              data.get('post_time', ''))
            else:
                identifier = (getattr(data, 'post_text', ''),
                              getattr(data, 'post_time', ''))

            if identifier not in seen and identifier != ('', '') and identifier != ('未知時間', ''):
                seen.add(identifier)
                unique_data.append(data)
        return unique_data

    def smart_merge_posts(self, old_posts, new_posts):
        """智慧合併貼文：如果舊貼文包含「查看更多」，用新內容替換"""
        if not old_posts:
            return self.remove_duplicates(new_posts)

        if not new_posts:
            return old_posts

        print(f"🔄 智慧合併貼文：舊 {len(old_posts)} 篇 + 新 {len(new_posts)} 篇")

        # 建立新貼文的快速查找字典（使用前150字符和時間作為key）
        new_posts_dict = {}
        for post in new_posts:
            text_key = post.get('post_text', '')[:150].strip()
            time_key = post.get('post_time', '')
            combined_key = (text_key, time_key)
            if text_key:
                new_posts_dict[combined_key] = post

        merged_posts = []
        replaced_count = 0

        # 檢查每個舊貼文
        for old_post in old_posts:
            old_text = old_post.get('post_text', '').strip()
            old_text_key = old_text[:150].strip()
            old_time_key = old_post.get('post_time', '')
            old_combined_key = (old_text_key, old_time_key)

            # 檢查舊貼文是否包含「查看更多」（表示內容被截斷）
            has_see_more = (
                '查看更多' in old_text or
                'See More' in old_text or
                'See more' in old_text
            )

            if has_see_more and old_combined_key in new_posts_dict:
                # 用新的完整內容替換舊的截斷內容
                new_post = new_posts_dict[old_combined_key]
                new_text = new_post.get('post_text', '').strip()

                # 檢查新內容是否也包含「查看更多」
                new_has_see_more = (
                    '查看更多' in new_text or
                    'See More' in new_text or
                    'See more' in new_text
                )

                # 如果新文章包含「查看更多」，保留舊內容不進行更新
                if new_has_see_more:
                    print(f"⚠️ 新文章仍包含「查看更多」，保留舊內容不更新")
                    merged_posts.append(old_post)
                    # 從新貼文字典中移除，避免重複添加
                    del new_posts_dict[old_combined_key]
                elif len(new_text) > len(old_text):
                    print(f"✅ 替換截斷內容：{len(old_text)} → {len(new_text)} 字符")
                    merged_posts.append(new_post)
                    replaced_count += 1
                    # 從新貼文字典中移除，避免重複添加
                    del new_posts_dict[old_combined_key]
                else:
                    # 新內容沒有改善，保留舊內容
                    merged_posts.append(old_post)
            else:
                # 舊貼文沒有「查看更多」或沒有對應的新內容，保留原樣
                merged_posts.append(old_post)
                # 如果新貼文中有相同的，移除以避免重複
                if old_combined_key in new_posts_dict:
                    del new_posts_dict[old_combined_key]

        # 添加剩餘的新貼文
        for remaining_post in new_posts_dict.values():
            merged_posts.append(remaining_post)

        # 最終去重
        final_posts = self.remove_duplicates(merged_posts)

        if replaced_count > 0:
            print(f"🔄 成功替換了 {replaced_count} 個截斷貼文為完整內容")

        return final_posts

    def scrape_posts(self, max_posts, progress_callback=None):
        """爬取指定數量的貼文，使用智慧滾動策略確保所有「查看更多」都被點擊"""
        all_posts = []
        scroll_attempts = 0
        max_scroll_attempts = 50  # 最大滾動次數
        batch_number = 1
        last_save_count = 0
        total_see_more_clicks = 0  # 統計總點擊數量

        print(
            f"🚀 開始高效爬取貼文，目標: {max_posts} 篇（每 {self.auto_save_interval} 篇自動保存）")
        print("⚡ 採用快速滾動策略，實時抓取並展開貼文內容")

        # 初始加載並抓取
        print("🔍 初始加載：抓取當前頁面貼文...")
        all_posts = self.extract_posts_with_bs()
        initial_clicks, all_posts = self.quick_click_see_more(all_posts)
        total_see_more_clicks += initial_clicks
        if initial_clicks > 0:
            print(f"✅ 初始加載點擊了 {initial_clicks} 個「查看更多」，已更新內容")

        while scroll_attempts < max_scroll_attempts and not self.stop_scraping:
            # 計算當前完整貼文數量（不包含「查看更多」的貼文）
            complete_posts = [
                post for post in all_posts
                if not ('查看更多' in post.get('post_text', '') or
                        'See More' in post.get('post_text', '') or
                        'See more' in post.get('post_text', ''))
            ]

            # 如果已經獲得足夠的完整貼文，就停止
            if len(complete_posts) >= max_posts:
                print(f"🎯 已獲得 {len(complete_posts)} 篇完整貼文，達到目標！")
                break
            # 使用高效滾動策略：快速滾動並實時抓取更新內容
            scroll_distance = 600 + random.randint(-100, 100)  # 減少滾動距離提高效率
            step_size = 120 + random.randint(-30, 30)  # 增加步長提高效率

            clicks_in_scroll, all_posts = self.fast_scroll_with_realtime_extract(
                total_distance=scroll_distance,
                step=step_size,
                all_posts=all_posts
            )
            total_see_more_clicks += clicks_in_scroll

            # 計算完整貼文數量
            complete_posts_for_display = [
                post for post in all_posts
                if not ('查看更多' in post.get('post_text', '') or
                        'See More' in post.get('post_text', '') or
                        'See more' in post.get('post_text', ''))
            ]

            current_count = len(all_posts)
            complete_count = len(complete_posts_for_display)
            print(f"📊 已擷取 {current_count} 篇貼文（其中 {complete_count} 篇完整）...")

            # 檢查是否需要自動保存（基於完整貼文數量）
            if complete_count - last_save_count >= self.auto_save_interval:
                # 取得新增的完整貼文
                new_complete_posts = complete_posts_for_display[last_save_count:]
                if new_complete_posts:
                    saved_file = self.save_partial_results(
                        new_complete_posts, batch_number)
                    if saved_file:
                        print(
                            f"💾 自動保存完成：第 {batch_number} 批次，{len(new_complete_posts)} 篇完整貼文")
                        batch_number += 1
                        last_save_count = complete_count

            # 更新進度（基於完整貼文數量）
            if progress_callback:
                progress = min(100, (complete_count / max_posts) * 100)
                progress_callback(progress, complete_count)

            scroll_attempts += 1

            # 每10次滾動後短暫檢查
            if scroll_attempts % 10 == 0:
                print("🔄 快速檢查遺漏的「查看更多」...")
                extra_clicks, all_posts = self.quick_click_see_more(all_posts)
                total_see_more_clicks += extra_clicks
                if extra_clicks > 0:
                    print(f"✅ 快速檢查額外找到 {extra_clicks} 個文字標籤，已更新內容")

                print(f"⏸️ 短暫暫停... (已滾動 {scroll_attempts} 次)")
                time.sleep(random.uniform(1, 2))  # 大幅縮短暫停時間

        # 最終清理：快速檢查遺漏的「查看更多」
        print("🧹 最終清理：快速檢查遺漏的「查看更多」...")
        final_clicks, all_posts = self.quick_click_see_more(all_posts)
        total_see_more_clicks += final_clicks
        if final_clicks > 0:
            print(f"✅ 最終清理找到 {final_clicks} 個遺漏的文字標籤，已更新內容")

        # 保存剩餘的完整貼文
        final_complete_posts = [
            post for post in all_posts
            if not ('查看更多' in post.get('post_text', '') or
                    'See More' in post.get('post_text', '') or
                    'See more' in post.get('post_text', ''))
        ]

        if len(final_complete_posts) > last_save_count:
            remaining_posts = final_complete_posts[last_save_count:]
            if remaining_posts:
                saved_file = self.save_partial_results(
                    remaining_posts, batch_number)
                if saved_file:
                    print(f"✅ 最終批次保存完成：{len(remaining_posts)} 篇完整貼文")

        # 總共點擊的「查看更多」文字標籤統計
        print(f"📈 高效完成：共處理了 {total_see_more_clicks} 個「查看更多」文字標籤，實時抓取了內容")

        # 最終選取完整貼文
        print("🧹 最終選取：提取完整的貼文...")
        complete_posts = [
            post for post in all_posts
            if not ('查看更多' in post.get('post_text', '') or
                    'See More' in post.get('post_text', '') or
                    'See more' in post.get('post_text', ''))
        ]

        # 取得指定數量的完整貼文
        final_posts = complete_posts[:max_posts]
        filtered_out_count = len(all_posts) - len(complete_posts)

        if filtered_out_count > 0:
            print(f"📝 從 {len(all_posts)} 篇貼文中過濾掉 {filtered_out_count} 篇截斷貼文")
            print(f"📊 最終選取 {len(final_posts)} 篇完整貼文")
        else:
            print(f"✅ 所有 {len(final_posts)} 篇貼文都是完整內容")

        self.scraped_posts = final_posts

        # 如果有保存部分檔案，通知使用者
        if self.partial_files:
            print(f"📁 已建立 {len(self.partial_files)} 個部分檔案，爬取完成後會自動合併")
            if self.save_callback:
                self.save_callback(
                    f"已建立 {len(self.partial_files)} 個備份檔案，可避免資料丟失")

        return self.scraped_posts

    def save_partial_results(self, posts_batch, batch_number):
        """儲存部分爬取結果"""
        if not posts_batch:
            return None

        # 過濾截斷貼文再保存
        filtered_batch = []
        filtered_count = 0

        for post in posts_batch:
            post_text = post.get('post_text', '')
            has_see_more = (
                '查看更多' in post_text or
                'See More' in post_text or
                'See more' in post_text
            )

            if not has_see_more:
                filtered_batch.append(post)
            else:
                filtered_count += 1

        if filtered_count > 0:
            print(
                f"📝 部分保存時過濾了 {filtered_count} 篇截斷貼文，保存 {len(filtered_batch)} 篇完整貼文")

        if not filtered_batch:
            print("⚠️ 本批次沒有完整貼文可保存")
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"facebook_posts_partial_{timestamp}_batch_{batch_number}.csv"

            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['post_text', 'likes', 'comments',
                              'shares', 'post_time', 'post_url', 'scraped_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for post in filtered_batch:
                    writer.writerow(post)

            self.partial_files.append(filename)
            print(f"部分資料已儲存至: {filename}")

            # 通知GUI保存狀態
            if self.save_callback:
                self.save_callback(
                    f"已自動保存 {len(filtered_batch)} 篇完整貼文到: {filename}")

            return filename

        except Exception as e:
            print(f"儲存部分CSV檔案時發生錯誤: {e}")
            return None

    def merge_partial_files(self, final_filename=None):
        """合併所有部分檔案為最終檔案"""
        if not self.partial_files:
            print("沒有部分檔案需要合併")
            return False

        if not final_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_filename = f"facebook_posts_final_{timestamp}.csv"

        try:
            all_posts = []

            # 讀取所有部分檔案
            for partial_file in self.partial_files:
                if os.path.exists(partial_file):
                    with open(partial_file, 'r', encoding='utf-8-sig') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            all_posts.append(row)

            # 去除重複項目
            unique_posts = self.remove_duplicates(all_posts)

            # 寫入最終檔案
            with open(final_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                if unique_posts:
                    fieldnames = unique_posts[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for post in unique_posts:
                        writer.writerow(post)

            print(f"最終合併檔案已儲存至: {final_filename}")
            print(f"總共合併了 {len(unique_posts)} 篇獨特貼文")

            # 清理部分檔案（可選）
            self.cleanup_partial_files()

            return final_filename

        except Exception as e:
            print(f"合併檔案時發生錯誤: {e}")
            return False

    def cleanup_partial_files(self):
        """清理部分檔案"""
        try:
            for partial_file in self.partial_files:
                if os.path.exists(partial_file):
                    os.remove(partial_file)
                    print(f"已清理部分檔案: {partial_file}")
            self.partial_files = []
        except Exception as e:
            print(f"清理部分檔案時發生錯誤: {e}")

    def save_to_csv(self, filename=None):
        """將爬取的資料儲存為CSV檔案"""
        # 如果有部分檔案，先合併它們
        if self.partial_files:
            merged_file = self.merge_partial_files(filename)
            if merged_file:
                return True

        # 如果沒有部分檔案但有完整的爬取資料
        if not self.scraped_posts:
            print("沒有資料可供儲存")
            return False

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"facebook_posts_{timestamp}.csv"

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['post_text', 'likes', 'comments',
                              'shares', 'post_time', 'post_url', 'scraped_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for post in self.scraped_posts:
                    writer.writerow(post)

            print(f"資料已儲存至: {filename}")
            return True

        except Exception as e:
            print(f"儲存CSV檔案時發生錯誤: {e}")
            return False

    def stop_scraping_process(self):
        """停止爬取過程"""
        self.stop_scraping = True
        print("正在停止爬取過程...")

    def close(self):
        """關閉瀏覽器"""
        if self.driver:
            self.driver.quit()
            print("瀏覽器已關閉")
