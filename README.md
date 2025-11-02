# 生财有术网站爬虫

爬取生财有术网站（https://scys.com/）热门模块前5条完整内容并保存为PDF。

## 功能特点

- 🔐 支持登录状态保存 - 首次登录后会保存cookies，下次运行自动使用
- 📥 自动爬取热门模块前5条内容
- 📄 每篇内容保存为独立的PDF文件，使用浏览器原生打印功能
- 🌐 支持完整网页内容，包括图片、样式等
- 🔍 多策略智能查找热门文章
- 🛡️ 错误处理和调试支持

## 快速开始

### 方法1: 使用自动安装脚本（推荐）

```bash
# 安装系统依赖和Python包
./install_dependencies.sh

# 运行改进版爬虫（推荐）
python3 scrape_scys_advanced.py
```

### 方法2: 手动安装

#### 1. 安装系统依赖

**Ubuntu/Debian:**
```bash
# 安装Chrome浏览器
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# 安装中文字体（可选，用于基础版）
sudo apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei
```

**macOS:**
```bash
# 使用Homebrew安装Chrome
brew install --cask google-chrome
```

#### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

#### 3. 运行爬虫

```bash
# 改进版（推荐） - 使用浏览器原生打印功能生成PDF
python3 scrape_scys_advanced.py

# 基础版 - 使用fpdf库生成PDF（需要中文字体）
python3 scrape_scys.py
```

## 使用说明

### 首次运行

1. 运行脚本后，会自动打开Chrome浏览器并访问生财有术网站
2. 在浏览器中手动登录你的账号
3. 登录完成后，返回终端按回车键继续
4. 脚本会自动：
   - 保存你的登录状态
   - 查找热门文章
   - 下载并保存为PDF

### 后续运行

- 脚本会自动使用保存的登录状态，无需再次登录
- 如果登录过期，会提示重新登录

## 版本对比

| 特性 | 基础版 | 改进版（推荐） |
|------|--------|----------------|
| PDF生成方式 | fpdf库 | 浏览器原生打印 |
| 中文支持 | 需要安装字体 | 完美支持 |
| 保留样式 | ❌ | ✅ |
| 保留图片 | ❌ | ✅ |
| 页面布局 | 文本流 | 原始网页布局 |
| 依赖 | 需要系统字体 | 仅需Chrome |

**推荐使用改进版 `scrape_scys_advanced.py`**

## 输出文件

```
项目目录/
├── scys_pdfs/              # PDF输出目录
│   ├── 01_文章标题.pdf
│   ├── 02_文章标题.pdf
│   └── ...
├── scys_cookies.json      # 保存的登录cookies
└── debug_page.html        # 调试用页面（仅在出错时生成）
```

## 配置选项

你可以在脚本中修改以下配置：

```python
# 在 SCYSScraperAdvanced 类中
self.base_url = "https://scys.com/"  # 网站地址
self.output_dir = "scys_pdfs"        # PDF输出目录
self.cookies_file = "scys_cookies.json"  # Cookies文件名
```

## 故障排除

### 问题1: 找不到chromedriver

**解决方案:**
- 脚本会自动下载chromedriver
- 如果失败，确保安装了Chrome浏览器

### 问题2: 无法找到热门文章

**解决方案:**
- 检查是否正确登录
- 查看生成的 `debug_page.html` 文件，了解页面结构
- 网站结构可能已更改，需要更新选择器

### 问题3: PDF保存失败

**解决方案:**
- 确保有写入权限
- 检查磁盘空间
- 尝试使用基础版

### 问题4: 登录状态失效

**解决方案:**
- 删除 `scys_cookies.json` 文件
- 重新运行脚本并登录

## 技术栈

- **Selenium WebDriver** - 浏览器自动化
- **Chrome DevTools Protocol** - PDF生成
- **BeautifulSoup4** - HTML解析
- **webdriver-manager** - 自动管理ChromeDriver

## 注意事项

⚠️ **使用须知:**

1. 本工具仅供学习和个人使用
2. 请遵守生财有术网站的使用条款和robots.txt规则
3. 爬取间隔设置为2秒，避免对服务器造成过大压力
4. 请勿用于商业用途或大规模爬取
5. 尊重内容版权，下载的内容仅供个人学习使用

## 开发

### 添加新功能

如果要修改查找文章的逻辑，编辑 `find_hot_articles()` 方法：

```python
def find_hot_articles(self):
    # 在这里添加你的查找逻辑
    pass
```

### 调试

运行时会生成 `debug_page.html`，可以用浏览器打开查看网页结构。

## License

MIT License

## 作者

本项目为自动化工具，用于便捷地保存和阅读生财有术网站内容。
