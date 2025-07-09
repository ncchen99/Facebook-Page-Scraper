#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook 粉絲專頁爬蟲 - 使用範例

此範例展示如何直接使用 FacebookPageScraper 類別來爬取 Facebook 粉絲專頁的貼文。
"""

from facebook_fan_page_scraper import FacebookPageScraper

def main():
    # 設定您的 Facebook 登入資訊
    email = "your_email@example.com"  # 請替換為您的 Facebook 帳號
    password = "your_password"        # 請替換為您的 Facebook 密碼
    
    # 設定要爬取的粉絲專頁網址
    page_urls = [
        "https://www.facebook.com/cnn",
        "https://www.facebook.com/bbc",
        # 可以加入更多粉絲專頁網址
    ]
    
    # 設定每個專頁要爬取的貼文數量
    max_posts_per_page = 5
    
    # 初始化爬蟲（使用 Edge 瀏覽器，推薦）
    scraper = FacebookPageScraper(email, password, use_edge=True)
    
    # 設定自動保存回調函數（顯示保存訊息）
    def save_callback(message):
        print(f"💾 {message}")
    
    scraper.save_callback = save_callback
    
    try:
        print("=== Facebook 粉絲專頁爬蟲開始 ===")
        
        # 初始化瀏覽器
        print("正在初始化瀏覽器...")
        if not scraper.initialize_driver():
            print("❌ 瀏覽器初始化失敗")
            return
        
        # 登入 Facebook
        print("正在登入 Facebook...")
        if not scraper.login():
            print("❌ Facebook 登入失敗")
            return
        
        print("✅ 登入成功！")
        
        all_posts = []
        
        # 依序爬取每個粉絲專頁
        for i, page_url in enumerate(page_urls):
            print(f"\n--- 爬取第 {i+1}/{len(page_urls)} 個粉絲專頁 ---")
            print(f"專頁網址: {page_url}")
            
            # 前往粉絲專頁
            if not scraper.navigate_to_page(page_url):
                print(f"❌ 無法前往粉絲專頁: {page_url}")
                continue
            
            # 爬取貼文（會自動點擊「查看更多」按鈕展開完整內容）
            print(f"開始爬取 {max_posts_per_page} 篇貼文...")
            
            def progress_callback(progress, count):
                print(f"  進度: {progress:.1f}% ({count} 篇)")
            
            posts = scraper.scrape_posts(max_posts_per_page, progress_callback)
            
            if posts:
                all_posts.extend(posts)
                print(f"✅ 成功爬取 {len(posts)} 篇貼文")
                
                # 顯示前幾篇貼文的摘要
                print("貼文摘要:")
                for j, post in enumerate(posts[:3]):  # 只顯示前3篇
                    text_preview = post['post_text'][:50] + "..." if len(post['post_text']) > 50 else post['post_text']
                    print(f"  {j+1}. {text_preview}")
                    print(f"     按讚: {post['likes']}, 留言: {post['comments']}, 分享: {post['shares']}")
            else:
                print("❌ 未能爬取到任何貼文")
        
        # 儲存所有爬取的貼文
        if all_posts:
            scraper.scraped_posts = all_posts
            filename = "facebook_posts_example.csv"
            
            print(f"\n=== 儲存結果 ===")
            print(f"總共爬取了 {len(all_posts)} 篇貼文")
            
            if scraper.save_to_csv(filename):
                print(f"✅ 結果已儲存至: {filename}")
            else:
                print("❌ 儲存檔案時發生錯誤")
        else:
            print("\n❌ 沒有爬取到任何貼文")
            
    except KeyboardInterrupt:
        print("\n⚠️  使用者中斷爬取過程")
    except Exception as e:
        print(f"\n❌ 爬取過程發生錯誤: {e}")
    finally:
        # 確保關閉瀏覽器
        print("\n正在關閉瀏覽器...")
        scraper.close()
        print("=== 爬取程序結束 ===")

if __name__ == "__main__":
    print("Facebook 粉絲專頁爬蟲 - 使用範例")
    print("請注意：使用前請先修改此檔案中的 email 和 password 變數")
    print("=" * 50)
    
    # 檢查是否還是預設的範例帳密
    example_email = "your_email@example.com"
    example_password = "your_password"
    
    # 這裡可以從檔案讀取或讓使用者輸入
    from facebook_fan_page_scraper import FacebookPageScraper
    
    # 簡單的帳密輸入（實際使用時可以改為從設定檔讀取）
    email = input("請輸入 Facebook 帳號: ").strip()
    password = input("請輸入 Facebook 密碼: ").strip()
    
    if email and password:
        print(f"\n使用帳號: {email}")
        
        # 修改全域變數並執行
        import sys
        sys.modules[__name__].email = email
        sys.modules[__name__].password = password
        
        main()
    else:
        print("❌ 帳號或密碼不能為空") 