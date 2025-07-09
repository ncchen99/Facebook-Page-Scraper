# Facebook 粉絲專頁爬蟲工具 - 詳細設置指南

本指南將帶您從零開始安裝和設置Facebook粉絲專頁爬蟲工具，適用於 **Windows**、**macOS** 和 **Linux** 系統。

---

## 📋 目錄

1. [系統需求](#系統需求)
2. [Python 安裝](#python-安裝)
3. [下載爬蟲工具](#下載爬蟲工具)
4. [安裝依賴套件](#安裝依賴套件)
5. [瀏覽器設置](#瀏覽器設置)
6. [首次使用](#首次使用)
7. [常見問題排除](#常見問題排除)
8. [進階設定](#進階設定)

---

## 🖥️ 系統需求

- **Python**: 3.7 或更高版本
- **作業系統**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **記憶體**: 至少 4GB RAM
- **硬碟空間**: 至少 1GB 可用空間
- **網路**: 穩定的網際網路連線

---

## 🐍 Python 安裝

### Windows 系統

#### 方法一：從官網下載（推薦）

1. **前往 Python 官網**
   ```
   https://www.python.org/downloads/
   ```

2. **下載最新版本**
   - 點擊 "Download Python 3.x.x" 按鈕
   - 下載 Windows installer (64-bit)

3. **安裝 Python**
   - 執行下載的 `.exe` 檔案
   - ⚠️ **重要**：勾選 "Add Python to PATH"
   - 選擇 "Install Now"
   - 等待安裝完成

4. **驗證安裝**
   ```cmd
   # 開啟命令提示字元 (cmd) 並輸入：
   python --version
   pip --version
   ```

#### 方法二：使用 Microsoft Store

1. 開啟 Microsoft Store
2. 搜尋 "Python"
3. 安裝 "Python 3.x" (選擇最新版本)

### macOS 系統

#### 方法一：使用 Homebrew（推薦）

1. **安裝 Homebrew**
   ```bash
   # 在終端機中執行：
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **安裝 Python**
   ```bash
   brew install python
   ```

3. **驗證安裝**
   ```bash
   python3 --version
   pip3 --version
   ```

#### 方法二：從官網下載

1. **前往 Python 官網**
   ```
   https://www.python.org/downloads/macos/
   ```

2. **下載 macOS installer**
   - 選擇適合您系統的版本
   - Intel Mac: 選擇 "macOS 64-bit Intel installer"
   - Apple Silicon (M1/M2): 選擇 "macOS 64-bit universal2 installer"

3. **安裝 Python**
   - 執行下載的 `.pkg` 檔案
   - 按照安裝精靈指示完成安裝

4. **更新 PATH（如果需要）**
   ```bash
   # 編輯 ~/.zshrc 或 ~/.bash_profile
   echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

#### 方法三：使用 pyenv（進階用戶）

1. **安裝 pyenv**
   ```bash
   curl https://pyenv.run | bash
   ```

2. **設定環境變數**
   ```bash
   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
   echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
   echo 'eval "$(pyenv init -)"' >> ~/.zshrc
   source ~/.zshrc
   ```

3. **安裝 Python**
   ```bash
   pyenv install 3.11.0
   pyenv global 3.11.0
   ```

### Linux 系統（Ubuntu/Debian）

```bash
# 更新套件清單
sudo apt update

# 安裝 Python 和 pip
sudo apt install python3 python3-pip python3-venv

# 驗證安裝
python3 --version
pip3 --version
```

---

## 📥 下載爬蟲工具

### 方法一：Git Clone（推薦）

```bash
# Windows (在 cmd 或 PowerShell 中)
git clone https://github.com/your-repo/facebook-fan-page-crawler.git
cd facebook-fan-page-crawler

# macOS/Linux (在終端機中)
git clone https://github.com/your-repo/facebook-fan-page-crawler.git
cd facebook-fan-page-crawler
```

### 方法二：直接下載

1. 前往專案頁面
2. 點擊 "Code" -> "Download ZIP"
3. 解壓縮到您喜歡的位置
4. 進入解壓縮後的資料夾

---

## 📦 安裝依賴套件

### Windows 系統

```cmd
# 在專案資料夾中開啟命令提示字元
# 升級 pip
python -m pip install --upgrade pip

# 安裝依賴套件
pip install -r requirements.txt

# 如果出現權限問題，使用：
pip install --user -r requirements.txt
```

### macOS 系統

```bash
# 在專案資料夾中開啟終端機
# 建立虛擬環境（推薦）
python3 -m venv venv
source venv/bin/activate

# 升級 pip
pip install --upgrade pip

# 安裝依賴套件
pip install -r requirements.txt
```

### 虛擬環境設置（推薦所有系統）

#### Windows:
```cmd
# 建立虛擬環境
python -m venv facebook_scraper_env

# 啟動虛擬環境
facebook_scraper_env\Scripts\activate

# 安裝套件
pip install -r requirements.txt
```

#### macOS/Linux:
```bash
# 建立虛擬環境
python3 -m venv facebook_scraper_env

# 啟動虛擬環境
source facebook_scraper_env/bin/activate

# 安裝套件
pip install -r requirements.txt
```

---

## 🌐 瀏覽器設置

### Microsoft Edge (推薦)

#### Windows:
- Edge 通常已預裝
- WebDriver 會自動管理，無需額外設置

#### macOS:
```bash
# 使用 Homebrew 安裝
brew install --cask microsoft-edge
```

### Google Chrome

#### Windows:
1. 前往 [Chrome 官網](https://www.google.com/chrome/) 下載安裝
2. 下載對應的 [ChromeDriver](https://chromedriver.chromium.org/)
3. 將 `chromedriver.exe` 放入專案的 `chromedriver-win64` 資料夾

#### macOS:
```bash
# 使用 Homebrew 安裝 Chrome
brew install --cask google-chrome

# 安裝 ChromeDriver
brew install chromedriver

# 或者使用自動管理（推薦）
pip install webdriver-manager
```

#### 檢查瀏覽器版本:

**Windows:**
```cmd
# Edge 版本
reg query "HKEY_CURRENT_USER\Software\Microsoft\Edge\BLBeacon" /v version

# Chrome 版本
reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version
```

**macOS:**
```bash
# Edge 版本
/Applications/Microsoft\ Edge.app/Contents/MacOS/Microsoft\ Edge --version

# Chrome 版本
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
```

---

## 🚀 首次使用

### 1. 測試安裝

```bash
# 測試 Python 和套件
python -c "import selenium, requests, beautifulsoup4; print('所有套件安裝成功！')"

# macOS 使用 python3
python3 -c "import selenium, requests, bs4; print('所有套件安裝成功！')"
```

### 2. 啟動 GUI 程式

#### Windows:
```cmd
python facebook_scraper_gui.py
```

#### macOS:
```bash
python3 facebook_scraper_gui.py
```

### 3. 使用程式化介面

```python
# 編輯 example_usage.py 檔案
python example_usage.py  # Windows
python3 example_usage.py  # macOS
```


## 🛠️ 常見問題排除

### Python 相關問題

#### Q: 找不到 Python 命令
**Windows:**
```cmd
# 重新安裝 Python 並確保勾選 "Add to PATH"
# 或手動添加到環境變數
set PATH=%PATH%;C:\Python39;C:\Python39\Scripts
```

**macOS:**
```bash
# 檢查 Python 安裝位置
which python3
which pip3

# 添加到 PATH
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### Q: pip 安裝失敗
```bash
# 升級 pip
python -m pip install --upgrade pip

# 使用國內鏡像源（中國用戶）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 使用用戶目錄安裝
pip install --user -r requirements.txt
```

### 套件安裝問題

#### Q: BeautifulSoup 安裝失敗
```bash
# 明確指定版本
pip install beautifulsoup4==4.12.2
pip install lxml==4.9.3
```

#### Q: PyQt5 安裝失敗

**macOS M1/M2:**
```bash
# 使用 conda 安裝
conda install pyqt
# 或
pip install PyQt5 --no-cache-dir
```

**Linux:**
```bash
sudo apt-get install python3-pyqt5
```

### 瀏覽器驅動問題

#### Q: WebDriver 版本不匹配

**自動管理方案:**
```python
# 安裝 webdriver-manager
pip install webdriver-manager

# 在程式中使用
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
```

#### Q: macOS 安全性警告

```bash
# 允許未知開發者的軟體執行
sudo spctl --master-disable

# 或針對特定檔案
sudo xattr -r -d com.apple.quarantine /path/to/chromedriver
```

### 權限問題

#### macOS 權限設定:
```bash
# 給予 Python 完整磁碟存取權限
# 系統偏好設定 -> 安全性與隱私權 -> 隱私權 -> 完整磁碟存取權限
# 添加 Terminal 和 Python

# 給予程式網路存取權限
# 系統偏好設定 -> 安全性與隱私權 -> 防火牆 -> 防火牆選項
```

---

## ⚙️ 進階設定

### 1. 建立桌面快捷方式

#### Windows:
創建 `start_scraper.bat` 檔案：
```batch
@echo off
cd /d "C:\path\to\facebook-fan-page-crawler"
python facebook_scraper_gui.py
pause
```

#### macOS:
創建 `start_scraper.command` 檔案：
```bash
#!/bin/bash
cd "/path/to/facebook-fan-page-crawler"
python3 facebook_scraper_gui.py
```

設定執行權限：
```bash
chmod +x start_scraper.command
```

### 2. 環境變數設定

創建 `.env` 檔案：
```env
FACEBOOK_EMAIL=your_email@example.com
FACEBOOK_PASSWORD=your_password
CHROME_DRIVER_PATH=/path/to/chromedriver
EDGE_DRIVER_PATH=/path/to/edgedriver
```

### 3. 代理設定（可選）

編輯程式檔案，添加代理設定：
```python
# 在 facebook_fan_page_scraper.py 中添加
proxy_options = {
    'http': 'http://proxy.example.com:8080',
    'https': 'https://proxy.example.com:8080'
}
```

### 4. 自動化排程

#### Windows 工作排程器:
1. 開啟「工作排程器」
2. 建立基本工作
3. 設定觸發程序和動作

#### macOS Cron Job:
```bash
# 編輯 crontab
crontab -e

# 添加排程（每天早上9點執行）
0 9 * * * cd /path/to/facebook-fan-page-crawler && python3 example_usage.py
```

---

## 📞 支援與幫助

### 檢查系統資訊

#### Windows:
```cmd
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
python --version
```

#### macOS:
```bash
sw_vers
python3 --version
```

### 產生錯誤報告

如果遇到問題，請收集以下資訊：

1. **系統資訊**
   - 作業系統版本
   - Python 版本
   - 瀏覽器版本

2. **錯誤訊息**
   ```bash
   python facebook_scraper_gui.py > error_log.txt 2>&1
   ```

3. **套件版本**
   ```bash
   pip list > installed_packages.txt
   ```

### 重新安裝

如果問題持續，可以嘗試完全重新安裝：

```bash
# 移除虛擬環境
rm -rf facebook_scraper_env  # macOS/Linux
rmdir /s facebook_scraper_env  # Windows

# 重新建立環境
python3 -m venv facebook_scraper_env
source facebook_scraper_env/bin/activate  # macOS/Linux
facebook_scraper_env\Scripts\activate  # Windows

# 重新安裝套件
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🎉 完成設置

恭喜您！現在可以開始使用 Facebook 粉絲專頁爬蟲工具了。

### 快速開始：

1. **啟動 GUI**：
   ```bash
   python facebook_scraper_gui.py  # Windows
   python3 facebook_scraper_gui.py  # macOS
   ```

2. **輸入 Facebook 帳號密碼**

3. **輸入粉絲專頁網址**

4. **點擊「開始爬取」**

5. **等待完成並保存結果**

---

## 💡 提示與最佳實務

1. **使用虛擬環境**：避免套件衝突
2. **定期更新**：保持套件為最新版本
3. **備份設定**：保存重要的設定檔案
4. **遵守使用條款**：請遵守 Facebook 的服務條款
5. **合理使用**：避免過度頻繁的爬取請求

---

**享受您的 Facebook 爬蟲體驗！** 🚀 