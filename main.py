import requests
from bs4 import BeautifulSoup
from win11toast import toast
import time
import webbrowser
import os
import datetime
import sys
from io import StringIO

URL = "https://nbw.sztu.edu.cn/list.jsp?urltype=tree.TreeTempUrl&wbtreeid=1029"
BASE_URL = "https://nbw.sztu.edu.cn/"
check_interval = 10

# 获取图标文件的绝对路径
ICON_PATH = os.path.join(os.path.dirname(__file__), "icon.ico")

last_notice = None
current_link = None  # 存储当前通知的链接

def open_notice_link(args=None):
    """点击通知时打开对应的网页链接"""
    try:
        if current_link:
            print(f"[点击通知] 打开链接: {current_link}")
            webbrowser.open(current_link)
    except:
        pass  # 忽略所有错误和状态信息

def get_latest_notice():
    try:
        res = requests.get(URL, timeout=10, proxies={})
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")
        li = soup.find("li", class_="clearfix")
        title_div = li.find("div", class_=lambda x: x and "width04" in x)
        a_tag = title_div.find("a")
        title = a_tag.get("title", "").strip()
        link = BASE_URL + a_tag.get("href", "")
        date_div = li.find("div", class_=lambda x: x and "width06" in x)
        date = date_div.text.strip() if date_div else "未知"
        
        return title, date, link
    except Exception as e:
        print(f"[错误] 请求或解析失败: {e}")
        return None, None, None
while True:
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title, date, link = get_latest_notice()
    if title and (title != last_notice):
        print(f"\033[92m[{current_time}][新通知] {title} ({date}) \033[0m")
        print(f"\033[92m[{current_time}][链接] {link}\033[0m")
        last_notice = title
        
        current_link = link
        
        # 临时重定向标准输出以隐藏 ToastDismissalReason 信息
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            toast(
                "学校新通知", 
                f"{title}\n日期:{date}\n点击通知查看详情", 
                on_click=open_notice_link,
                icon=ICON_PATH,
            )
        finally:
            # 恢复标准输出
            sys.stdout = old_stdout
    else:
        print(f"\033[93m[{current_time}][无新通知]\033[0m")

    time.sleep(check_interval)
