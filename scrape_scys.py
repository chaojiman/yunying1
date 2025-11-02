#!/usr/bin/env python3
"""
生财有术网站爬虫 - 爬取热门模块前5条内容并保存为PDF
"""
import os
import json
import time
import base64
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup

class SCYSPDF(FPDF):
    """自定义PDF类，支持中文"""
    def __init__(self):
        super().__init__()
        self.add_page()
        # 添加支持中文的字体
        self.font_loaded = False
        font_paths = [
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/truetype/arphic/uming.ttc',
            '/System/Library/Fonts/PingFang.ttc',  # macOS
        ]
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    self.add_font('Chinese', '', font_path, uni=True)
                    self.set_font('Chinese', '', 12)
                    self.font_loaded = True
                    break
            except Exception as e:
                continue
        
        if not self.font_loaded:
            print("警告：无法加载中文字体，PDF可能无法正确显示中文")
            try:
                self.set_font('Arial', '', 12)
            except:
                pass

class SCYSScraper:
    def __init__(self):
        self.base_url = "https://scys.com/"
        self.cookies_file = "scys_cookies.json"
        self.output_dir = "scys_pdfs"
        self.driver = None
        
        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def setup_driver(self):
        """设置Chrome浏览器"""
        chrome_options = Options()
        # 不使用无头模式，方便用户手动登录
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"Chrome WebDriver设置失败: {e}")
            print("尝试使用本地chromedriver...")
            self.driver = webdriver.Chrome(options=chrome_options)
    
    def load_cookies(self):
        """加载已保存的cookies"""
        if os.path.exists(self.cookies_file):
            try:
                with open(self.cookies_file, 'r') as f:
                    cookies = json.load(f)
                
                # 先访问网站主页
                self.driver.get(self.base_url)
                time.sleep(2)
                
                # 添加cookies
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        print(f"添加cookie失败: {e}")
                
                # 刷新页面
                self.driver.refresh()
                time.sleep(2)
                return True
            except Exception as e:
                print(f"加载cookies失败: {e}")
                return False
        return False
    
    def save_cookies(self):
        """保存cookies"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f)
            print(f"Cookies已保存到 {self.cookies_file}")
        except Exception as e:
            print(f"保存cookies失败: {e}")
    
    def manual_login(self):
        """提示用户手动登录"""
        print("\n" + "="*60)
        print("请在打开的浏览器窗口中手动登录生财有术网站")
        print("登录成功后，请在终端中按回车键继续...")
        print("="*60 + "\n")
        
        self.driver.get(self.base_url)
        input("登录完成后请按回车键继续...")
        
        # 保存cookies
        self.save_cookies()
        print("登录状态已保存！")
    
    def check_login_status(self):
        """检查是否已登录"""
        try:
            # 检查页面是否有登录后的元素（根据实际网站调整）
            # 这里需要根据实际网站结构来判断
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 简单检查：如果页面中没有登录按钮，则认为已登录
            page_source = self.driver.page_source
            if "登录" in page_source and "退出" not in page_source:
                return False
            return True
        except:
            return False
    
    def get_hot_articles(self):
        """获取热门模块的前5条文章链接和标题"""
        print("正在获取热门文章列表...")
        
        try:
            # 访问网站首页
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # 尝试找到热门模块（需要根据实际网站结构调整选择器）
            # 这里提供几种常见的选择器尝试
            articles = []
            
            # 尝试不同的选择器
            selectors = [
                "//div[contains(@class, 'hot')]//a[contains(@href, '/')]",
                "//div[contains(text(), '热门')]/..//a",
                "//section[contains(@class, 'hot')]//a",
                "//div[@class='list-item']//a",
                "//article//a[@href]",
                "//a[contains(@class, 'title')]"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements and len(elements) >= 5:
                        for element in elements[:5]:
                            try:
                                title = element.text.strip()
                                url = element.get_attribute('href')
                                if title and url and url.startswith('http'):
                                    articles.append({'title': title, 'url': url})
                                    if len(articles) >= 5:
                                        break
                            except:
                                continue
                    if len(articles) >= 5:
                        break
                except:
                    continue
            
            if not articles:
                # 如果没有找到，打印页面源码帮助调试
                print("未能找到热门文章，正在保存页面源码用于调试...")
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print("页面源码已保存到 debug_page.html")
                
                # 尝试获取所有链接
                print("尝试获取所有文章链接...")
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in all_links[:10]:
                    try:
                        title = link.text.strip()
                        url = link.get_attribute('href')
                        if title and url and len(title) > 5:
                            print(f"找到链接: {title[:50]} - {url}")
                            articles.append({'title': title, 'url': url})
                            if len(articles) >= 5:
                                break
                    except:
                        continue
            
            return articles[:5]
        
        except Exception as e:
            print(f"获取热门文章失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_article_content(self, url):
        """获取文章完整内容"""
        try:
            print(f"正在获取文章内容: {url}")
            self.driver.get(url)
            time.sleep(3)
            
            # 尝试获取文章内容（需要根据实际网站结构调整）
            content_selectors = [
                "//article",
                "//div[contains(@class, 'content')]",
                "//div[contains(@class, 'article')]",
                "//div[contains(@class, 'post-content')]",
                "//main",
                "//body"
            ]
            
            content_element = None
            for selector in content_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        content_element = elements[0]
                        break
                except:
                    continue
            
            if content_element:
                # 获取文章标题
                title = ""
                try:
                    title_element = self.driver.find_element(By.TAG_NAME, "h1")
                    title = title_element.text.strip()
                except:
                    title = self.driver.title
                
                # 获取文章内容
                content = content_element.text
                
                return {
                    'title': title,
                    'content': content,
                    'html': content_element.get_attribute('innerHTML')
                }
            else:
                print("未能找到文章内容元素")
                return None
        
        except Exception as e:
            print(f"获取文章内容失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_to_pdf(self, article_data, filename):
        """将文章内容保存为PDF"""
        try:
            print(f"正在保存PDF: {filename}")
            
            pdf = SCYSPDF()
            
            # 添加标题
            pdf.set_font_size(16)
            title = article_data['title']
            pdf.multi_cell(0, 10, title)
            pdf.ln(5)
            
            # 添加内容
            pdf.set_font_size(12)
            content = article_data['content']
            
            # 处理内容，避免特殊字符问题
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    try:
                        pdf.multi_cell(0, 8, line)
                    except Exception as e:
                        # 如果某行有问题，跳过
                        print(f"警告：跳过有问题的行: {e}")
                        continue
            
            # 保存PDF
            output_path = os.path.join(self.output_dir, filename)
            pdf.output(output_path)
            print(f"PDF已保存: {output_path}")
            return True
        
        except Exception as e:
            print(f"保存PDF失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 尝试使用备用方法：保存为HTML
            try:
                html_filename = filename.replace('.pdf', '.html')
                html_path = os.path.join(self.output_dir, html_filename)
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(f"<html><head><meta charset='utf-8'><title>{article_data['title']}</title></head>")
                    f.write(f"<body><h1>{article_data['title']}</h1>")
                    f.write(f"<div>{article_data['html']}</div></body></html>")
                print(f"已保存为HTML格式: {html_path}")
                
                # 尝试使用浏览器打印功能保存为PDF
                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.get(f"file://{os.path.abspath(html_path)}")
                time.sleep(2)
                
                # 使用打印功能保存PDF
                pdf_settings = {
                    "landscape": False,
                    "displayHeaderFooter": False,
                    "printBackground": True,
                    "preferCSSPageSize": True,
                }
                
                output_path = os.path.join(self.output_dir, filename)
                result = self.driver.execute_cdp_cmd("Page.printToPDF", pdf_settings)
                
                with open(output_path, 'wb') as f:
                    import base64
                    f.write(base64.b64decode(result['data']))
                
                print(f"通过浏览器打印已保存PDF: {output_path}")
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                
                return True
            except Exception as e2:
                print(f"备用方法也失败: {e2}")
                return False
    
    def run(self):
        """运行爬虫"""
        try:
            print("初始化浏览器...")
            self.setup_driver()
            
            # 尝试加载已保存的cookies
            cookies_loaded = self.load_cookies()
            
            if not cookies_loaded:
                # 需要手动登录
                self.manual_login()
            else:
                print("已加载保存的登录状态")
                # 检查登录状态
                if not self.check_login_status():
                    print("登录状态已失效，需要重新登录")
                    self.manual_login()
            
            # 获取热门文章列表
            articles = self.get_hot_articles()
            
            if not articles:
                print("未能获取到文章列表，请检查网站结构")
                return
            
            print(f"\n找到 {len(articles)} 篇文章")
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article['title']}")
            print()
            
            # 爬取每篇文章并保存为PDF
            for i, article in enumerate(articles, 1):
                print(f"\n处理第 {i}/{len(articles)} 篇文章...")
                
                # 获取文章内容
                content_data = self.get_article_content(article['url'])
                
                if content_data:
                    # 生成安全的文件名
                    safe_title = "".join(c for c in article['title'] if c.isalnum() or c in (' ', '-', '_'))
                    safe_title = safe_title[:50]  # 限制文件名长度
                    filename = f"{i:02d}_{safe_title}.pdf"
                    
                    # 保存为PDF
                    self.save_to_pdf(content_data, filename)
                else:
                    print(f"跳过第 {i} 篇文章（获取内容失败）")
                
                # 等待一下，避免请求过快
                time.sleep(2)
            
            print(f"\n完成！所有PDF已保存到 {self.output_dir} 目录")
        
        except Exception as e:
            print(f"运行出错: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            if self.driver:
                print("\n关闭浏览器...")
                self.driver.quit()

def main():
    print("="*60)
    print("生财有术网站爬虫")
    print("="*60)
    
    scraper = SCYSScraper()
    scraper.run()

if __name__ == "__main__":
    main()
