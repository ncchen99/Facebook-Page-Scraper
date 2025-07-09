#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook 粉絲專頁爬蟲工具 - 快速啟動腳本

雙擊此檔案或在命令列執行以啟動圖形界面。
"""

import sys
import os

def check_dependencies():
    """檢查必要的依賴套件是否已安裝"""
    required_packages = [
        ('PyQt5', 'PyQt5'),
        ('selenium', 'selenium'),
        ('beautifulsoup4', 'bs4'),
        ('lxml', 'lxml')
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ 缺少必要的套件:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n請執行以下命令安裝缺少的套件:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    print("Facebook 粉絲專頁爬蟲工具")
    print("=" * 40)
    
    # 檢查依賴套件
    print("正在檢查依賴套件...")
    if not check_dependencies():
        input("\n按 Enter 鍵退出...")
        return
    
    print("✅ 所有依賴套件已安裝")
    
    # 檢查主程式檔案是否存在
    gui_file = "facebook_scraper_gui.py"
    if not os.path.exists(gui_file):
        print(f"❌ 找不到主程式檔案: {gui_file}")
        print("請確認檔案是否存在於同一目錄中")
        input("\n按 Enter 鍵退出...")
        return
    
    # 啟動GUI
    print("正在啟動圖形界面...")
    try:
        # 匯入並執行GUI
        from facebook_scraper_gui import main as gui_main
        gui_main()
    except Exception as e:
        print(f"❌ 啟動圖形界面時發生錯誤: {e}")
        print("\n詳細錯誤資訊:")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 鍵退出...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程式已中斷")
    except Exception as e:
        print(f"\n發生未預期的錯誤: {e}")
        input("按 Enter 鍵退出...") 