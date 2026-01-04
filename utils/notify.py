
import requests
import dingtalkchatbot.chatbot as cb
import time
import random
import re
from .config import load_config, get_proxies

# 分类颜色定义 (Decimal)
CATEGORY_COLORS = {
    'Articles': 3447003,      # Blue
    'Social Media': 10181046, # Purple
    'Pictures': 5763719,      # Green
    'Videos': 15548997,       # Red
    'Notifications': 16776960 # Yellow
}

# 推送函数
def push_message(title, content, category="Articles"):
    config = load_config()
    push_config = config.get('push', {})
    
    # 格式化标题，增加分类标签
    formatted_title = f"[{category}] {title}"
    
    # 钉钉推送
    if 'dingding' in push_config and push_config['dingding'].get('switch', '') == "ON":
        send_dingding_msg(push_config['dingding'].get('webhook'), push_config['dingding'].get('secret_key'), formatted_title,
                          content)

    # 飞书推送
    if 'feishu' in push_config and push_config['feishu'].get('switch', '') == "ON":
        send_feishu_msg(push_config['feishu'].get('webhook'), formatted_title, content)

    # Telegram Bot推送
    if 'tg_bot' in push_config and push_config['tg_bot'].get('switch', '') == "ON":
        send_tg_bot_msg(push_config['tg_bot'].get('token'), push_config['tg_bot'].get('group_id'), formatted_title, content)
    
    # Discard推送
    if 'discard' in push_config and push_config['discard'].get('switch', '') == "ON" and push_config['discard'].get('send_normal_msg', '') == "ON":
        send_discard_msg(push_config['discard'].get('webhook'), title, content, category)

# 飞书推送
def send_feishu_msg(webhook, title, content):
    feishu(title, content, webhook)

# Telegram Bot推送
def send_tg_bot_msg(token, group_id, title, content):
    tgbot(title, content, token, group_id)

# 钉钉推送
def send_dingding_msg(webhook, secret_key, title, content):
    dingding(title, content, webhook, secret_key)

# 钉钉推送实现
def dingding(text, msg, webhook, secretKey):
    try:
        if not webhook or webhook == "https://oapi.dingtalk.com/robot/send?access_token=你的token":
            print(f"钉钉推送跳过：webhook地址未配置")
            return
            
        if not secretKey or secretKey == "你的Key":
            print(f"钉钉推送跳过：secret_key未配置")
            return
            
        ding = cb.DingtalkChatbot(webhook, secret=secretKey)
        ding.send_text(msg='{}\r\n{}'.format(text, msg), is_at_all=False)
        print(f"钉钉推送成功: {text}")
    except Exception as e:
        print(f"钉钉推送失败: {str(e)}")

# 飞书推送实现
def feishu(text, msg, webhook):
    try:
        if not webhook or webhook == "飞书的webhook地址":
            print(f"飞书推送跳过：webhook地址未配置")
            return
            
        headers = {
            "Content-Type": "application/json;charset=utf-8"
        }
        data = {
            "msg_type": "text",
            "content": {
                "text": '{}\n{}'.format(text, msg)
            }
        }
        
        # 飞书推送不需要代理
        response = requests.post(webhook, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"飞书推送成功: {text}")
    except Exception as e:
        print(f"飞书推送失败: {str(e)}")

# Telegram Bot推送实现
def tgbot(text, msg, token, group_id):
    import telegram
    try:
        if not token or token == "Telegram Bot的token":
            print(f"Telegram推送跳过：token未配置")
            return
            
        if not group_id or group_id == "Telegram Bot的group_id":
            print(f"Telegram推送跳过：group_id未配置")
            return
            
        # 获取代理配置
        proxies = get_proxies()
        
        if proxies:
            # 配置telegram bot使用代理
            request_kwargs = {'proxies': proxies}
            bot = telegram.Bot(token=token, request_kwargs=request_kwargs)
        else:
            bot = telegram.Bot(token=token)
            
        bot.send_message(chat_id=group_id, text=f'{text}\n{msg}')
        print(f"Telegram推送成功: {text}")
    except Exception as e:
        print(f"Telegram推送失败: {str(e)}")

# Discard推送
def send_discard_msg(webhook, title, content, category="Articles"):
    # 检查是否是占位符
    if not webhook or webhook == "discard的webhook地址":
        print(f"Discard推送跳过：webhook地址未配置")
        return
    
    # 检查webhook地址格式
    if not webhook.startswith('http'):
        print(f"Discard推送失败：webhook地址格式错误，必须以http或https开头")
        return
    
    try:
        headers = {
            "Content-Type": "application/json;charset=utf-8"
        }
        
        # 推送普通消息，使用 Embeds
        # 尝试从content中解析真正的 标题 和 链接
        embed_title = title
        embed_desc = content
        embed_url = ""
        
        try:
            # 简单的解析逻辑
            title_match = re.search(r'标题: (.*?)\n', content)
            link_match = re.search(r'链接: (.*?)\n', content)
            
            if title_match:
                embed_title = title_match.group(1)
            if link_match:
                embed_url = link_match.group(1)
                
            # 如果能解析出更干净的描述，可以去掉标题和链接行
            embed_desc = f"来源: {title}"
        except:
            pass

        # 增加分类前缀到标题
        embed_title = f"[{category}] {embed_title}"

        # 获取分类对应颜色，如果没有则随机
        color = CATEGORY_COLORS.get(category)
        if not color:
             color = random.randint(0, 0xFFFFFF)
        
        embed = {
            "title": embed_title,
            "description": embed_desc,
            "color": color,
            "footer": {
                "text": f"Powered by Rss_monitor • {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
            }
        }
        
        if embed_url:
            embed["url"] = embed_url
        
        data = {
            "embeds": [embed]
        }
    
        print(f"正在发送Discard推送：{title} (Category: {category})")
        
        # 获取代理配置
        proxies = get_proxies()
        if proxies:
            print(f"使用代理：{proxies}")
        
        # 使用较短的超时时间，避免长时间阻塞
        response = requests.post(webhook, json=data, headers=headers, timeout=5, proxies=proxies)
        
        print(f"Discard推送响应状态码：{response.status_code}")
        
        # 检查响应状态
        if response.status_code in [200, 204]:
            print(f"Discard推送成功: {title}")
        else:
            print(f"Discard推送失败: HTTP状态码 - {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"Discard推送失败: {str(e)}")
