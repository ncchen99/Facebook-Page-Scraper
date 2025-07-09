import sys
import os
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, 
                            QProgressBar, QSpinBox, QGroupBox, QMessageBox, 
                            QComboBox, QCheckBox, QFileDialog, QSplitter)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap
from facebook_fan_page_scraper import FacebookPageScraper

class ScrapingThread(QThread):
    """爬取執行緒"""
    progress_updated = pyqtSignal(float, int)  # 進度百分比, 已爬取數量
    status_updated = pyqtSignal(str)  # 狀態訊息
    scraping_finished = pyqtSignal(bool)  # 爬取完成訊號
    save_status_updated = pyqtSignal(str)  # 自動保存狀態訊號
    
    def __init__(self, scraper, page_urls, max_posts):
        super().__init__()
        self.scraper = scraper
        self.page_urls = page_urls
        self.max_posts = max_posts
        self.is_running = False
        
    def run(self):
        """執行爬取作業"""
        self.is_running = True
        
        try:
            # 設定自動保存回調函數
            self.scraper.save_callback = self.save_status_updated.emit
            
            # 初始化瀏覽器
            self.status_updated.emit("正在初始化瀏覽器...")
            if not self.scraper.initialize_driver():
                self.status_updated.emit("瀏覽器初始化失敗")
                self.scraping_finished.emit(False)
                return
            
            # 登入Facebook
            self.status_updated.emit("正在登入Facebook...")
            if not self.scraper.login():
                self.status_updated.emit("Facebook登入失敗")
                self.scraping_finished.emit(False)
                return
            
            all_scraped_posts = []
            
            # 爬取每個粉絲專頁
            for i, page_url in enumerate(self.page_urls):
                if not self.is_running:
                    break
                    
                self.status_updated.emit(f"正在爬取第 {i+1}/{len(self.page_urls)} 個粉絲專頁...")
                
                # 前往粉絲專頁
                if not self.scraper.navigate_to_page(page_url):
                    self.status_updated.emit(f"無法前往粉絲專頁: {page_url}")
                    continue
                
                # 爬取貼文
                posts = self.scraper.scrape_posts(
                    self.max_posts, 
                    progress_callback=self.update_progress
                )
                
                all_scraped_posts.extend(posts)
                self.status_updated.emit(f"已完成第 {i+1} 個粉絲專頁，共爬取 {len(posts)} 篇貼文")
            
            # 儲存所有爬取的貼文
            self.scraper.scraped_posts = all_scraped_posts
            
            if all_scraped_posts:
                self.status_updated.emit(f"爬取完成！總共爬取 {len(all_scraped_posts)} 篇貼文")
                self.scraping_finished.emit(True)
            else:
                self.status_updated.emit("未爬取到任何貼文")
                self.scraping_finished.emit(False)
                
        except Exception as e:
            self.status_updated.emit(f"爬取過程發生錯誤: {str(e)}")
            self.scraping_finished.emit(False)
    
    def update_progress(self, progress, count):
        """更新進度"""
        self.progress_updated.emit(progress, count)
    
    def stop(self):
        """停止爬取"""
        self.is_running = False
        if hasattr(self, 'scraper') and self.scraper:
            self.scraper.stop_scraping_process()
            # 立即嘗試關閉瀏覽器以加速停止過程
            try:
                if hasattr(self.scraper, 'driver') and self.scraper.driver:
                    self.scraper.driver.quit()
            except:
                pass

class FacebookScraperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scraper = None
        self.scraping_thread = None
        self.init_ui()
        
    def init_ui(self):
        """初始化使用者界面"""
        self.setWindowTitle("Facebook 粉絲專頁爬蟲工具")
        self.setGeometry(100, 100, 900, 700)
        
        # 設定字體
        font = QFont("微軟正黑體", 10)
        self.setFont(font)
        
        # 主要容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 使用分割器
        splitter = QSplitter(Qt.Vertical)
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(splitter)
        
        # === 登入資訊區域 ===
        login_group = QGroupBox("Facebook 登入資訊")
        login_layout = QVBoxLayout(login_group)
        
        # 帳號輸入
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("請輸入Facebook帳號...")
        email_layout.addWidget(self.email_input)
        login_layout.addLayout(email_layout)
        
        # 密碼輸入
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("密碼:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("請輸入Facebook密碼...")
        password_layout.addWidget(self.password_input)
        login_layout.addLayout(password_layout)
        
        # 瀏覽器選擇
        browser_layout = QHBoxLayout()
        browser_layout.addWidget(QLabel("瀏覽器:"))
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["Microsoft Edge (推薦)", "Google Chrome"])
        browser_layout.addWidget(self.browser_combo)
        login_layout.addLayout(browser_layout)
        
        # 智慧功能說明
        info_label = QLabel("🍪 智慧登入：7天免重複登入 | 💾 自動備份：防資料丟失 | 🧹 智慧清理：日期格式處理 | 📖 安全展開：可見性檢查+ESC防護 | 🛡️ 強化彈窗：快速多重關閉")
        info_label.setStyleSheet("color: #666; font-size: 9px; margin: 5px;")
        info_label.setWordWrap(True)
        login_layout.addWidget(info_label)
        
        splitter.addWidget(login_group)
        
        # === 爬取設定區域 ===
        settings_group = QGroupBox("爬取設定")
        settings_layout = QVBoxLayout(settings_group)
        
        # 粉絲專頁網址輸入
        urls_layout = QVBoxLayout()
        urls_layout.addWidget(QLabel("粉絲專頁網址 (每行一個):"))
        self.urls_input = QTextEdit()
        self.urls_input.setMaximumHeight(120)
        self.urls_input.setPlaceholderText("請輸入粉絲專頁網址，例如:\nhttps://www.facebook.com/cnn\nhttps://www.facebook.com/bbc")
        urls_layout.addWidget(self.urls_input)
        settings_layout.addLayout(urls_layout)
        
        # 爬取數量設定
        posts_layout = QHBoxLayout()
        posts_layout.addWidget(QLabel("每個專頁爬取貼文數量:"))
        self.posts_spinbox = QSpinBox()
        self.posts_spinbox.setMinimum(1)
        self.posts_spinbox.setMaximum(1000)
        self.posts_spinbox.setValue(10)
        posts_layout.addWidget(self.posts_spinbox)
        posts_layout.addStretch()
        settings_layout.addLayout(posts_layout)
        
        splitter.addWidget(settings_group)
        
        # === 控制按鈕區域 ===
        controls_group = QGroupBox("操作控制")
        controls_layout = QVBoxLayout(controls_group)
        
        # 按鈕區域
        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("開始爬取")
        self.start_button.clicked.connect(self.start_scraping)
        self.start_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }")
        
        self.stop_button = QPushButton("停止爬取")
        self.stop_button.clicked.connect(self.stop_scraping)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; padding: 8px; }")
        
        self.save_button = QPushButton("儲存結果")
        self.save_button.clicked.connect(self.save_results)
        self.save_button.setEnabled(False)
        self.save_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; padding: 8px; }")
        
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addStretch()
        controls_layout.addLayout(buttons_layout)
        
        # 進度條
        progress_layout = QVBoxLayout()
        progress_layout.addWidget(QLabel("爬取進度:"))
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("準備就緒")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        controls_layout.addLayout(progress_layout)
        
        splitter.addWidget(controls_group)
        
        # === 日誌顯示區域 ===
        log_group = QGroupBox("執行日誌")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        splitter.addWidget(log_group)
        
        # 設定分割器比例
        splitter.setSizes([150, 180, 120, 150])
        
        # 初始化狀態
        self.log("歡迎使用 Facebook 粉絲專頁爬蟲工具！")
        self.log("請先輸入 Facebook 登入資訊和要爬取的粉絲專頁網址")
        
    def log(self, message):
        """新增日誌訊息"""
        self.log_text.append(f"[{self.get_current_time()}] {message}")
        self.log_text.ensureCursorVisible()
    
    def log_save_status(self, message):
        """新增自動保存狀態訊息"""
        self.log_text.append(f"[{self.get_current_time()}] 💾 {message}")
        self.log_text.ensureCursorVisible()
        
    def get_current_time(self):
        """取得當前時間字串"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
        
    def validate_inputs(self):
        """驗證輸入資料"""
        if not self.email_input.text().strip():
            QMessageBox.warning(self, "警告", "請輸入 Facebook Email")
            return False
            
        if not self.password_input.text().strip():
            QMessageBox.warning(self, "警告", "請輸入 Facebook 密碼")
            return False
            
        if not self.urls_input.toPlainText().strip():
            QMessageBox.warning(self, "警告", "請輸入至少一個粉絲專頁網址")
            return False
            
        return True
        
    def get_page_urls(self):
        """取得粉絲專頁網址列表"""
        urls_text = self.urls_input.toPlainText().strip()
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        # 驗證網址格式
        valid_urls = []
        for url in urls:
            if 'facebook.com' in url:
                valid_urls.append(url)
            else:
                self.log(f"忽略無效網址: {url}")
                
        return valid_urls
        
    def start_scraping(self):
        """開始爬取"""
        if not self.validate_inputs():
            return
            
        page_urls = self.get_page_urls()
        if not page_urls:
            QMessageBox.warning(self, "警告", "沒有有效的粉絲專頁網址")
            return
            
        # 初始化爬蟲
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        use_edge = self.browser_combo.currentIndex() == 0
        max_posts = self.posts_spinbox.value()
        
        self.scraper = FacebookPageScraper(email, password, use_edge)
        
        # 創建並啟動爬取執行緒
        self.scraping_thread = ScrapingThread(self.scraper, page_urls, max_posts)
        self.scraping_thread.progress_updated.connect(self.update_progress)
        self.scraping_thread.status_updated.connect(self.log)
        self.scraping_thread.save_status_updated.connect(self.log_save_status)
        self.scraping_thread.scraping_finished.connect(self.scraping_finished)
        
        # 更新UI狀態
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.progress_bar.setValue(0)
        
        self.log("開始爬取作業...")
        self.scraping_thread.start()
        
    def stop_scraping(self):
        """停止爬取"""
        if self.scraping_thread and self.scraping_thread.isRunning():
            self.log("正在停止爬取...")
            self.scraping_thread.stop()
            
            # 設置合理的超時時間，避免無限等待
            if not self.scraping_thread.wait(3000):  # 等待3秒
                self.log("⚠️ 強制終止爬取線程")
                self.scraping_thread.terminate()
                self.scraping_thread.wait(1000)  # 再等1秒
            
        self.scraping_finished(False)
        
    def update_progress(self, progress, count):
        """更新進度"""
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(f"已爬取 {count} 篇貼文 ({progress:.1f}%)")
        
    def scraping_finished(self, success):
        """爬取完成處理"""
        # 更新UI狀態
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        if success and self.scraper:
            # 檢查是否有任何資料（包括部分檔案）
            has_data = (self.scraper.scraped_posts or self.scraper.partial_files)
            
            if has_data:
                self.save_button.setEnabled(True)
                self.progress_bar.setValue(100)
                
                # 計算總資料量
                total_posts = len(self.scraper.scraped_posts) if self.scraper.scraped_posts else 0
                partial_files_count = len(self.scraper.partial_files) if self.scraper.partial_files else 0
                
                if self.scraper.partial_files:
                    self.log(f"✅ 爬取完成！資料已分批保存到 {partial_files_count} 個檔案中")
                    success_msg = f"爬取完成！\n資料已安全保存到 {partial_files_count} 個部分檔案\n點擊「儲存結果」可合併為單一檔案"
                else:
                    self.log(f"✅ 爬取成功完成！共取得 {total_posts} 篇貼文")
                    success_msg = f"爬取完成！\n共取得 {total_posts} 篇貼文"
                    
                QMessageBox.information(self, "成功", success_msg)
            else:
                self.save_button.setEnabled(False)
                self.log("❌ 未取得任何貼文資料")
        else:
            self.save_button.setEnabled(False)
            self.log("❌ 爬取未成功完成")
            
        # 在背景線程中關閉瀏覽器，避免阻塞UI
        if self.scraper:
            def close_browser():
                try:
                    self.scraper.close()
                except Exception as e:
                    print(f"關閉瀏覽器時發生錯誤: {e}")
            
            # 使用線程池在背景關閉瀏覽器
            threading.Thread(target=close_browser, daemon=True).start()
            
    def save_results(self):
        """儲存爬取結果"""
        if not self.scraper:
            QMessageBox.warning(self, "警告", "沒有爬蟲物件")
            return
            
        # 檢查是否有部分檔案或完整資料
        has_partial_files = self.scraper.partial_files
        has_scraped_posts = self.scraper.scraped_posts
        
        if not has_partial_files and not has_scraped_posts:
            QMessageBox.warning(self, "警告", "沒有資料可供儲存")
            return
            
        # 選擇儲存位置
        default_filename = f"facebook_posts_{self.get_current_time().replace(':', '')}.csv"
        if has_partial_files:
            default_filename = f"facebook_posts_merged_{self.get_current_time().replace(':', '')}.csv"
            
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "儲存爬取結果", 
            default_filename,
            "CSV files (*.csv)"
        )
        
        if filename:
            try:
                if has_partial_files:
                    # 如果有部分檔案，使用合併功能
                    self.log("正在合併部分檔案...")
                    merged_file = self.scraper.merge_partial_files(filename)
                    if merged_file:
                        self.log(f"✅ 已成功合併並儲存至: {filename}")
                        
                        # 詢問是否要清理部分檔案
                        reply = QMessageBox.question(
                            self, 
                            "清理檔案", 
                            f"合併完成！共有 {len(self.scraper.partial_files)} 個部分檔案。\n\n是否要刪除這些部分檔案？\n（建議保留作為備份）",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No
                        )
                        
                        if reply == QMessageBox.Yes:
                            self.scraper.cleanup_partial_files()
                            self.log("已清理部分檔案")
                        
                        QMessageBox.information(self, "成功", f"資料已成功合併並儲存至:\n{filename}")
                    else:
                        QMessageBox.critical(self, "錯誤", "合併檔案時發生錯誤")
                else:
                    # 使用傳統保存方式
                    if self.scraper.save_to_csv(filename):
                        self.log(f"結果已儲存至: {filename}")
                        QMessageBox.information(self, "成功", f"資料已成功儲存至:\n{filename}")
                    else:
                        QMessageBox.critical(self, "錯誤", "儲存檔案時發生錯誤")
                        
            except Exception as e:
                self.log(f"儲存過程發生錯誤: {str(e)}")
                QMessageBox.critical(self, "錯誤", f"儲存過程發生錯誤:\n{str(e)}")
                
    def closeEvent(self, event):
        """關閉視窗事件"""
        if self.scraping_thread and self.scraping_thread.isRunning():
            reply = QMessageBox.question(
                self, 
                "確認", 
                "爬取作業正在進行中，確定要關閉程式嗎？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 非阻塞式停止爬取
                self.log("正在快速關閉程式...")
                if self.scraping_thread:
                    self.scraping_thread.stop()
                    # 不等待線程結束，直接繼續關閉
                
                # 在背景清理資源
                self._cleanup_resources_async()
                event.accept()
            else:
                event.ignore()
        else:
            # 程式正常關閉
            self._cleanup_resources_async()
            event.accept()
    
    def _cleanup_resources_async(self):
        """在背景線程中異步清理資源"""
        def cleanup():
            try:
                # 強制終止爬取線程
                if self.scraping_thread and self.scraping_thread.isRunning():
                    self.scraping_thread.terminate()
                    self.scraping_thread.wait(1000)  # 最多等1秒
                
                # 關閉瀏覽器
                if self.scraper and hasattr(self.scraper, 'driver') and self.scraper.driver:
                    try:
                        self.scraper.driver.quit()
                    except:
                        # 強制殺死瀏覽器進程
                        try:
                            import psutil
                            import os
                            current_pid = os.getpid()
                            for proc in psutil.process_iter(['pid', 'name']):
                                if 'chrome' in proc.info['name'].lower() or 'edge' in proc.info['name'].lower():
                                    if proc.info['pid'] != current_pid:
                                        proc.terminate()
                        except:
                            pass
                        
            except Exception as e:
                print(f"清理資源時發生錯誤: {e}")
        
        # 使用daemon線程確保不會阻礙程式關閉
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 設定現代化樣式
    
    window = FacebookScraperGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 