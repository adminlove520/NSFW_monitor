
import feedparser
import time
from .notify import push_message
from .config import get_proxies

# 获取数据并检查更新
def check_for_updates(feed_url, site_name, cursor, conn, send_push=True):
    print(f"{site_name} 监控中... ")
    data_list = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        file_data = feedparser.parse(feed_url, agent=headers['User-Agent'])
        data = file_data.entries
        process_entries(data, site_name, cursor, conn, send_push, data_list)
        
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

        # 查询数据库中是否存在相同链接的文章
        cursor.execute("SELECT * FROM items WHERE link = ?", (data_link,))
        result = cursor.fetchone()
        if result is None:
            # 未找到相同链接的文章
            push_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            
            # 只有在send_push为True时才发送推送
            if send_push:
                print(f"发现新文章，准备推送: {data_title}")
                push_message(f"{site_name} 更新", f"标题: {data_title}\n链接: {data_link}\n推送时间：{push_time}")

            # 存储到数据库 with a timestamp
            cursor.execute("INSERT INTO items (title, link, timestamp) VALUES (?, ?, CURRENT_TIMESTAMP)", (data_title, data_link))
            conn.commit()
