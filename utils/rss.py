
import feedparser
import time
import requests
import re
from .notify import push_message
from .config import get_proxies

# 自定义获取函数，处理 429 重试
def fetch_feed_with_retry(url, max_retries=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    proxies = get_proxies()
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
            
            if response.status_code == 200:
                return response.content
            elif response.status_code in [429, 503]:
                wait_time = (attempt + 1) * 30  # 30s, 60s, 90s
                print(f"请求被限流 (HTTP {response.status_code})，等待 {wait_time} 秒后重试... ({attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"请求失败: HTTP {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"请求异常: {str(e)}")
            time.sleep(10)
            
    print(f"达到最大重试次数，跳过: {url}")
    return None

# 获取数据并检查更新
def check_for_updates(feed_url, site_name, cursor, conn, send_push=True):
    print(f"{site_name} 监控中... ")
    data_list = []
    
    try:
        # 使用自定义的重试逻辑获取内容
        feed_content = fetch_feed_with_retry(feed_url)
        
        if feed_content:
            file_data = feedparser.parse(feed_content)
            data = file_data.entries
            process_entries(data, site_name, cursor, conn, send_push, data_list)
        else:
            print(f"无法获取 RSS 内容: {site_name}")

    except Exception as e:
        print(f"RSS解析出错 [{site_name}]: {str(e)}")
    
    return data_list

def process_entries(entries, site_name, cursor, conn, send_push, data_list):
    if entries:
        # 只取最新的一条
        entry = entries[0]
        
        if isinstance(entry, dict):
            data_title = entry.get('title')
            data_link = entry.get('link')
        else:
            data_title = entry.title
            data_link = entry.link
            
        data_list.append(data_title)
        data_list.append(data_link)
        
        # 提取图片 URL
        image_url = None
        
        # 1. 尝试从 enclosures (附件) 提取
        if hasattr(entry, 'enclosures'):
            for enclosure in entry.enclosures:
                if enclosure.get('type', '').startswith('image/'):
                    image_url = enclosure.get('href')
                    break
        
        # 2. 尝试从 media_content 提取 (RSSHub 常用)
        if not image_url and hasattr(entry, 'media_content'):
             for media in entry.media_content:
                 if media.get('medium') == 'image' or media.get('type', '').startswith('image/'):
                     image_url = media.get('url')
                     break

        # 3. 尝试从内容中正则匹配 img 标签
        if not image_url:
            content_html = ''
            if hasattr(entry, 'content'):
                for c in entry.content:
                     content_html += c.get('value', '')
            if hasattr(entry, 'description'):
                content_html += entry.description
            
            # 简单的正则匹配 src
            img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content_html)
            if img_match:
                image_url = img_match.group(1)

        # 查询数据库中是否存在相同链接的文章
        cursor.execute("SELECT * FROM items WHERE link = ?", (data_link,))
        result = cursor.fetchone()
        if result is None:
            # 未找到相同链接的文章
            push_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            
            # 只有在send_push为True时才发送推送
            if send_push:
                print(f"发现新文章，准备推送: {data_title}")
                # 传递 image_url 给推送函数
                push_message(f"{site_name} 更新", f"标题: {data_title}\n链接: {data_link}\n推送时间：{push_time}", image_url=image_url)

            # 存储到数据库 with a timestamp
            cursor.execute("INSERT INTO items (title, link, timestamp) VALUES (?, ?, CURRENT_TIMESTAMP)", (data_title, data_link))
            conn.commit()
