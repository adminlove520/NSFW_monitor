
import argparse
import yaml
import time
from datetime import datetime
from utils.config import load_config, should_sleep
from utils.db import init_database
from utils.notify import push_message
from utils.rss import check_for_updates

# 主函数
def main():
    banner = '''
    +-------------------------------------------+
                   RSS Monitor
    +-------------------------------------------+
                     Start...
    '''

    print(banner)
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='RSS Monitor Script')
    parser.add_argument('--once', action='store_true', help='Execute once (GitHub Actions)')
    args = parser.parse_args()
    
    conn = init_database()
    cursor = conn.cursor()
    rss_config = {}

    try:
        with open('rss.yaml', 'r', encoding='utf-8') as file:
            rss_config = yaml.load(file, Loader=yaml.FullLoader) or {}
    except Exception as e:
        print(f"Error loading rss.yaml: {str(e)}")
        conn.close()
        return

    # 发送启动通知消息
    # 检查是否有任何推送服务的开关是开启的
    config = load_config()
    push_config = config.get('push', {})
    any_push_enabled = False
    
    for service in push_config.values():
        if service.get('switch', 'OFF') == 'ON':
            any_push_enabled = True
            break
    
    if any_push_enabled:
        print("Monitor Service Started")

    try:
        if args.once:
            # 单次执行模式，适合GitHub Action
            print("Mode: Once")
            for website, config in rss_config.items():
                website_name = config.get("website_name", website)
                rss_url = config.get("rss_url")
                category = config.get("category", "Articles") # Default category
                if not rss_url: continue
                
                check_for_updates(rss_url, website_name, cursor, conn, category=category)
        else:
            # 循环执行模式，适合本地运行
            while True:
                try:
                    # 检查是否需要夜间休眠
                    if should_sleep():
                        sleep_hours = 7 - datetime.now().hour
                        print(f"Sleeping for {sleep_hours} hours (Night Mode)...")
                        time.sleep(sleep_hours * 3600)
                        continue
                    
                    for website, config in rss_config.items():
                        website_name = config.get("website_name", website)
                        rss_url = config.get("rss_url")
                        category = config.get("category", "Articles") # Default category
                        if not rss_url: continue
                        
                        check_for_updates(rss_url, website_name, cursor, conn, category=category)

                    # 每二小时执行一次
                    time.sleep(7200)

                except Exception as e:
                    print(f"Error in loop: {str(e)}")
                    time.sleep(60)
    except Exception as e:
        print(f"Main Error: {str(e)}")
    finally:
        conn.close()
        print("Monitor Ended")

if __name__ == "__main__":
    main()
