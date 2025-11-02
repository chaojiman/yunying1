#!/usr/bin/env python3
"""
生财有术网站爬虫 - 改进版
支持多种方式生成PDF，包括直接使用浏览器打印功能
"""
import os
import json
import time
import base64
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class SCYSScraperAdvanced:
    def __init__(self):
        self.base_url = "https://scys.com/"
        self.cookies_file = "scys_cookies.json"
        self.output_dir = "scys_pdfs"
        self.driver = None
        
        # 创建输出目录
        Path(self.output_dir).mkdir(exist_ok=True)
    
    def setup_driver(self, headless=False):
        """设置Chrome浏览器"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless=new')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 启用打印到PDF功能
        chrome_options.add_argument('--kiosk-printing')
        
        # 下载设置
        prefs = {
            'printing.print_preview_sticky_settings.appState': json.dumps({
                'recentDestinations': [{
                    'id': 'Save as PDF',
                    'origin': 'local',
                    'account': ''
                }],
                'selectedDestinationId': 'Save as PDF',
                'version': 2
            }),
            'savefile.default_directory': os.path.abspath(self.output_dir)
        }
        chrome_options.add_experimental_option('prefs', prefs)
        
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"使用webdriver_manager失败: {e}")
            print("尝试使用系统Chrome...")
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except:
                print("尝试使用chromium...")
                chrome_options.binary_location = "/usr/bin/chromium-browser"
                self.driver = webdriver.Chrome(options=chrome_options)
        
        print("浏览器初始化成功")
    
    def load_cookies(self):
        """加载已保存的cookies"""
        if not os.path.exists(self.cookies_file):
            return False
        
        try:
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
            
            self.driver.get(self.base_url)
            time.sleep(2)
            
            for cookie in cookies:
                try:
                    if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                        cookie['sameSite'] = 'Lax'
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"添加cookie失败: {e}")
            
            self.driver.refresh()
            time.sleep(2)
            print("已加载保存的登录状态")
            return True
        except Exception as e:
            print(f"加载cookies失败: {e}")
            return False
    
    def save_cookies(self):
        """保存cookies"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f, indent=2)
            print(f"✓ Cookies已保存到 {self.cookies_file}")
        except Exception as e:
            print(f"保存cookies失败: {e}")
    
    def manual_login(self):
        """提示用户手动登录"""
        print("\n" + "="*70)
        print("  请在打开的浏览器窗口中手动登录生财有术网站")
        print("  登录成功后，请返回终端并按回车键继续...")
        print("="*70 + "\n")
        
        self.driver.get(self.base_url)
        
        try:
            input("✓ 登录完成后请按回车键继续...")
        except:
            time.sleep(30)
            print("等待30秒后自动继续...")
        
        self.save_cookies()
        print("✓ 登录状态已保存！\n")
    
    def find_hot_articles(self):
        """查找热门文章"""
        print("正在查找热门文章...")
        
        # 保存页面以便分析
        page_source = self.driver.page_source
        
        # 尝试多种策略查找热门文章
        articles = []
        
        # 策略1: 查找包含"热门"的区域
        try:
            hot_sections = self.driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'hot') or contains(text(), '热门')]/ancestor::section | " +
                "//h2[contains(text(), '热门')]/following-sibling::div | " +
                "//div[contains(@class, 'hot')]"
            )
            
            for section in hot_sections[:3]:
                links = section.find_elements(By.TAG_NAME, 'a')
                for link in links:
                    try:
                        href = link.get_attribute('href')
                        text = link.text.strip()
                        if href and text and len(text) > 5:
                            articles.append({
                                'title': text,
                                'url': href
                            })
                            if len(articles) >= 5:
                                return articles[:5]
                    except:
                        continue
        except Exception as e:
            print(f"策略1失败: {e}")
        
        # 策略2: 查找所有看起来像文章标题的链接
        if len(articles) < 5:
            try:
                all_links = self.driver.find_elements(By.XPATH,
                    "//a[contains(@class, 'title') or contains(@class, 'post') or contains(@class, 'article')]"
                )
                
                for link in all_links:
                    try:
                        href = link.get_attribute('href')
                        text = link.text.strip()
                        if href and text and len(text) > 5:
                            # 避免重复
                            if not any(a['url'] == href for a in articles):
                                articles.append({
                                    'title': text,
                                    'url': href
                                })
                                if len(articles) >= 5:
                                    return articles[:5]
                    except:
                        continue
            except Exception as e:
                print(f"策略2失败: {e}")
        
        # 策略3: 使用BeautifulSoup分析
        if len(articles) < 5:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # 查找所有链接
                for a in soup.find_all('a', href=True):
                    text = a.get_text(strip=True)
                    href = a['href']
                    
                    # 过滤条件
                    if (len(text) > 10 and 
                        ('scys.com' in href or href.startswith('/')) and
                        not any(x in href.lower() for x in ['login', 'register', 'about', 'help'])):
                        
                        full_url = href if href.startswith('http') else self.base_url.rstrip('/') + href
                        
                        if not any(a['url'] == full_url for a in articles):
                            articles.append({
                                'title': text,
                                'url': full_url
                            })
                            if len(articles) >= 5:
                                break
            except Exception as e:
                print(f"策略3失败: {e}")
        
        # 保存调试信息
        if len(articles) < 5:
            debug_file = "debug_page.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(page_source)
            print(f"⚠ 找到的文章数量不足，页面已保存到 {debug_file} 供调试")
        
        return articles[:5]
    
    def save_page_as_pdf(self, url, title, index):
        """使用浏览器打印功能保存页面为PDF"""
        try:
            print(f"正在访问: {title[:50]}...")
            self.driver.get(url)
            time.sleep(3)
            
            # 等待页面加载完成
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 滚动页面确保所有内容加载
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # 生成安全的文件名
            safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
            safe_title = safe_title[:80]
            filename = f"{index:02d}_{safe_title}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # 使用Chrome DevTools Protocol打印PDF
            print(f"正在生成PDF...")
            
            pdf_settings = {
                'landscape': False,
                'displayHeaderFooter': False,
                'printBackground': True,
                'preferCSSPageSize': True,
                'paperWidth': 8.27,  # A4
                'paperHeight': 11.69,
                'marginTop': 0.4,
                'marginBottom': 0.4,
                'marginLeft': 0.4,
                'marginRight': 0.4,
            }
            
            result = self.driver.execute_cdp_cmd('Page.printToPDF', pdf_settings)
            
            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(result['data']))
            
            print(f"✓ 已保存: {filename}")
            return True
            
        except Exception as e:
            print(f"✗ 保存失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self):
        """运行爬虫"""
        try:
            print("\n" + "="*70)
            print("  生财有术网站爬虫 - 改进版")
            print("="*70 + "\n")
            
            print("步骤 1/4: 初始化浏览器...")
            self.setup_driver(headless=False)
            
            print("\n步骤 2/4: 登录...")
            cookies_loaded = self.load_cookies()
            
            if not cookies_loaded:
                self.manual_login()
            else:
                # 验证登录状态
                self.driver.get(self.base_url)
                time.sleep(2)
                
                page_content = self.driver.page_source
                if '登录' in page_content and '登出' not in page_content and '退出' not in page_content:
                    print("⚠ 登录状态已过期，需要重新登录")
                    self.manual_login()
                else:
                    print("✓ 登录状态有效")
            
            print("\n步骤 3/4: 查找热门文章...")
            articles = self.find_hot_articles()
            
            if not articles:
                print("\n✗ 未找到文章，请检查:")
                print("  1. 网站结构是否发生变化")
                print("  2. 是否正确登录")
                print("  3. 查看 debug_page.html 了解页面结构")
                return
            
            print(f"\n✓ 找到 {len(articles)} 篇文章:\n")
            for i, article in enumerate(articles, 1):
                print(f"  {i}. {article['title'][:60]}")
            
            print(f"\n步骤 4/4: 开始下载并保存为PDF...")
            print("-" * 70)
            
            success_count = 0
            for i, article in enumerate(articles, 1):
                print(f"\n[{i}/{len(articles)}] {article['title'][:50]}...")
                
                if self.save_page_as_pdf(article['url'], article['title'], i):
                    success_count += 1
                
                # 避免请求过快
                if i < len(articles):
                    time.sleep(2)
            
            print("\n" + "="*70)
            print(f"  完成！成功保存 {success_count}/{len(articles)} 个PDF文件")
            print(f"  保存位置: {os.path.abspath(self.output_dir)}/")
            print("="*70 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n用户中断操作")
        except Exception as e:
            print(f"\n✗ 运行出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                print("清理资源...")
                try:
                    self.driver.quit()
                except:
                    pass

def main():
    scraper = SCYSScraperAdvanced()
    scraper.run()

if __name__ == "__main__":
    main()
