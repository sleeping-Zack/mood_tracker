import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from get_urls import urls


class XiaoHongShuSpider:
    def __init__(self):
        # 初始化 Chrome 浏览器
        self.options = Options()
        self.driver = webdriver.Chrome(executable_path=r'D:\\py\\chromedriver.exe', options=self.options)

        # Cookies 可以通过开发者工具拿到
        self.cookies = {
            "abRequestId": "956891d0-26ec-5285-8322-2b8bc732713f",
            "a1": "19675d6c68fhxjna0aidhzdaplj5zzxir4itvx3xg50000289642",
            "webId": "fa23a68785c40e3815dedc055907c140",
            "gid": "yjKW2fKf2SFqyjKW2fKSK4CqYixCVI0803fx3Ckuf0U1V9282uuC3h888JYjK4J8dJD0i2YD",
            "webBuild": "4.62.3",
            "xsecappid": "xhs-pc-web",
            "unread": '{"ub":"68075e42000000000f03a372","ue":"67fb4957000000001d0278a4","uc":24}',
            "acw_tc": "0a00d90517466894383613364e2b1ddffeb3d9057b1f6fea8f22ab83a3d981",
            "loadts": "1746689445803",
            "websectiga": "8886be45f388a1ee7bf611a69f3e174cae48f1ea02c0f8ec3256031b8be9c7ee",
            "sec_poison_id": "ab647dfc-bfe4-42b5-9a39-d99b0798c0f8"
        }

        # 创建保存路径
        if not os.path.exists('文案2'):
            os.makedirs('文案2')

    def open_detail_page(self, url):
        """访问详情页并添加 Cookie"""
        print(f"[INFO] 正在访问: {url}")
        self.driver.get(url)

        # 注入 Cookies
        print("[INFO] 注入 Cookies...")
        for name, value in self.cookies.items():
            self.driver.add_cookie({'name': name, 'value': value})

        # 刷新页面，加载登录状态
        self.driver.refresh()
        time.sleep(5)

    def extract_text(self, url):
        """获取页面中的文案"""
        print("[INFO] 开始提取文案...")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'note-text'))
            )
            contents = self.driver.find_elements(By.CLASS_NAME, 'note-text')
            text_list = [content.text for content in contents if len(content.text) > 10]

            # 获取页面的唯一ID作为文件名
            page_id = url.split('/')[4].split('?')[0]

            # 保存文案
            for idx, text in enumerate(text_list):
                filename = f'文案2/{page_id}_{idx}.txt'
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(text)
                print(f"[INFO] 文案已保存: {filename}")

        except Exception as e:
            print(f"[ERROR] 提取文案失败: {e}")

    def run(self):
        """启动爬虫"""
        for url in urls:
            try:
                self.open_detail_page(url)
                self.extract_text(url)
            except Exception as e:
                print(f"[ERROR] 访问失败: {url} - 错误信息: {e}")
        print("[INFO] 所有任务完成")
        self.driver.quit()


if __name__ == "__main__":
    spider = XiaoHongShuSpider()
    spider.run()
