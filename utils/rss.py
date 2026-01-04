
import feedparser
import time
import requests
import re
import json
from .notify import push_message
from .config import get_proxies

# 获取数据并检查更新
def check_for_updates(feed_url, site_name, cursor, conn, send_push=True, category="Articles"):
    print(f"{site_name} [{category}] 监控中... ")
    data_list = []
    
    # 检查是否是 Folo 直接链接
    if "folo.is" in feed_url and "view=1" in feed_url:
        data_list = check_folo_updates(feed_url, site_name, cursor, conn, send_push, category)
        return data_list

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        file_data = feedparser.parse(feed_url, agent=headers['User-Agent'])
        data = file_data.entries
        process_entries(data, site_name, cursor, conn, send_push, data_list, category)
        
    except Exception as e:
        print(f"RSS解析出错 [{site_name}]: {str(e)}")
    
    return data_list

def check_folo_updates(url, site_name, cursor, conn, send_push, category):
    data_list = []
    try:
        print(f"检测到 Folo 链接，正在直接解析: {url}")
        proxies = get_proxies()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
        response.raise_for_status()
        html = response.text
        
        # 提取 HYDRATE 数据
        # 改进 Regex：
        # 1. 使用 ((?:[^'\\]|\\.)*?) 来匹配单引号内的内容，确保不会因为内部的转义单引号 \' 而提前结束
        pattern = r'window\.__HYDRATE__\[".*?"\]=JSON\.parse\(\'((?:[^\'\\]|\\.)*?)\'\)'
        match = re.search(pattern, html)
        
        if match:
            json_str = match.group(1)
            try:
                # 修复 JS 字符串转 JSON 的问题
                # Content inside JSON.parse('...') is a JS string.
                # It may contain \' which is valid in JS string but invalid in JSON.
                # It may contain \\ which is valid in both.
                
                # Replace \' with ' 
                json_str = json_str.replace(r"\'", "'")
                # 其他转义如 \\, \n, \", 应该保持原样用于 JSON 解析?
                # Case 1: JS source: '\\' -> Regex captures: '\\' -> JSON expects '\\' (escaped backslash). OK.
                # Case 2: JS source: '\'' -> Regex captures: '\'' -> JSON expects '\'' ?? NO. JSON strings don't allow escaped single quotes.
                # So we replaced it.
                
                # Case 3: JS source: '\"' -> Regex: '\"' -> JSON: '\"'. OK (Valid JSON escape).
                
                # 有时候为了保险，可能还有类似 \\' 的情况？(escaped backslash then quote?)
                # 暂时先处理最常见的 \' 
                
                data = json.loads(json_str)
                entries = data.get('entries', [])
                
                formatted_entries = []
                for entry in entries:
                    formatted_entries.append({
                        'title': entry.get('title'),
                        'link': entry.get('url'),
                        'published': entry.get('publishedAt')
                    })
                
                process_entries(formatted_entries, site_name, cursor, conn, send_push, data_list, category)
                
            except json.JSONDecodeError as e:
                print(f"Folo JSON 解析失败: {str(e)}")
                # Debug: print snippet where error occurred
                # start_idx = max(0, e.pos - 20)
                # end_idx = min(len(json_str), e.pos + 20)
                # print(f"Error context: ...{json_str[start_idx:end_idx]}...")
        else:
            print("未在 Folo 页面找到数据 (Regex mismatch)")
            
    except Exception as e:
        print(f"Folo 请求或处理失败 [{site_name}]: {str(e)}")
    
    return data_list

def process_entries(entries, site_name, cursor, conn, send_push, data_list, category):
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
                print(f"发现新文章，准备推送: {data_title} (Category: {category})")
                push_message(f"{site_name} 更新", f"标题: {data_title}\n链接: {data_link}\n推送时间：{push_time}", category=category)

            # 存储到数据库 with a timestamp
            cursor.execute("INSERT INTO items (title, link, timestamp) VALUES (?, ?, CURRENT_TIMESTAMP)", (data_title, data_link))
            conn.commit()
