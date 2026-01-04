
import yaml
import os
from datetime import datetime

# 加载配置文件
def load_config():
    # 从文件加载配置
    config = {}
    try:
        # 尝试从上级目录加载config.yaml (假设运行目录在根目录)
        # 或者从当前目录加载
        config_path = 'config.yaml'
        if not os.path.exists(config_path):
             config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        print("未找到config.yaml文件，将使用环境变量配置")
    except Exception as e:
        print(f"加载config.yaml文件出错: {str(e)}")
    
    # 初始化push配置
    push_config = config.get('push', {})
    
    # 钉钉推送配置
    if 'dingding' not in push_config:
        push_config['dingding'] = {}
    
    push_config['dingding']['webhook'] = os.environ.get('DINGDING_WEBHOOK', push_config['dingding'].get('webhook', ''))
    push_config['dingding']['secret_key'] = os.environ.get('DINGDING_SECRET', push_config['dingding'].get('secret_key', ''))
    push_config['dingding']['switch'] = os.environ.get('DINGDING_SWITCH', push_config['dingding'].get('switch', 'OFF'))
    
    # 飞书推送配置
    if 'feishu' not in push_config:
        push_config['feishu'] = {}
    
    push_config['feishu']['webhook'] = os.environ.get('FEISHU_WEBHOOK', push_config['feishu'].get('webhook', ''))
    push_config['feishu']['switch'] = os.environ.get('FEISHU_SWITCH', push_config['feishu'].get('switch', 'OFF'))
    
    # Telegram Bot推送配置
    if 'tg_bot' not in push_config:
        push_config['tg_bot'] = {}
    
    push_config['tg_bot']['token'] = os.environ.get('TELEGRAM_TOKEN', push_config['tg_bot'].get('token', ''))
    push_config['tg_bot']['group_id'] = os.environ.get('TELEGRAM_GROUP_ID', push_config['tg_bot'].get('group_id', ''))
    push_config['tg_bot']['switch'] = os.environ.get('TELEGRAM_SWITCH', push_config['tg_bot'].get('switch', 'OFF'))
    
    # Discard推送配置
    if 'discard' not in push_config:
        push_config['discard'] = {}
    
    push_config['discard']['webhook'] = os.environ.get('DISCARD_WEBHOOK', push_config['discard'].get('webhook', ''))
    push_config['discard']['switch'] = os.environ.get('DISCARD_SWITCH', push_config['discard'].get('switch', 'OFF'))
    push_config['discard']['send_normal_msg'] = os.environ.get('DISCARD_SEND_NORMAL_MSG', push_config['discard'].get('send_normal_msg', 'ON'))
    
    # 添加夜间休眠配置
    config['night_sleep'] = {
        'switch': os.environ.get('NIGHT_SLEEP_SWITCH', config.get('night_sleep', {}).get('switch', 'ON'))
    }
        
    # 加载代理配置
    proxy_config = config.get('proxy', {})
    config['proxy'] = {
        'enable': os.environ.get('PROXY_ENABLE', proxy_config.get('enable', 'OFF')),
        'http_proxy': os.environ.get('HTTP_PROXY', proxy_config.get('http_proxy', '')),
        'https_proxy': os.environ.get('HTTPS_PROXY', proxy_config.get('https_proxy', '')),
        'no_proxy': os.environ.get('NO_PROXY', proxy_config.get('no_proxy', ''))
    }
    
    config['push'] = push_config
    return config

# 判断是否应该进行夜间休眠
def should_sleep():
    # 加载配置
    config = load_config()
    # 检查是否开启夜间休眠功能
    sleep_switch = os.environ.get('NIGHT_SLEEP_SWITCH', config.get('night_sleep', {}).get('switch', 'ON'))
    if sleep_switch != 'ON':
        return False
    
    # 判断当前时间（北京时间）是否在0-7点之间
    # 获取当前UTC时间，转换为北京时间（UTC+8）
    now_utc = datetime.utcnow()
    # 转换为北京时间
    now_bj = now_utc.hour + 8
    # 处理跨天情况
    if now_bj >= 24:
        now_bj -= 24
    
    return now_bj < 7

# 获取代理配置
def get_proxies():
    config = load_config()
    proxy_config = config.get('proxy', {})
    
    if proxy_config.get('enable', 'OFF') == 'OFF':
        return None
    
    proxies = {}
    if proxy_config.get('http_proxy'):
        proxies['http'] = proxy_config.get('http_proxy')
    if proxy_config.get('https_proxy'):
        proxies['https'] = proxy_config.get('https_proxy')
    
    return proxies if proxies else None
