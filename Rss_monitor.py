
import argparse
import yaml
import time
from datetime import datetime
from utils.config import load_config, should_sleep
from utils.db import init_database
from utils.notify import push_message
from utils.rss import check_for_updates

__version__ = "V1.0.8"

# 主函数
def main():
    start_timestamp = time.time()
    banner = '''
    +-------------------------------------------+
                   RSS Monitor
    +-------------------------------------------+
                     Start...
    '''

    print(banner)
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='RSS Monitor Script')
    parser.add_argument('--once', action='store_true', help='Execute once and exit')
    parser.add_argument('--time-limit', type=int, default=0, help='Maximum run time in seconds (for GitHub Actions loop)')
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

    # 发送启动通知消息 (仅首次)
    config = load_config()
    push_config = config.get('push', {})
    print("Monitor Service Started")

    try:
        if args.once:
            # 单次执行模式
            print("Mode: Once")
            run_check(rss_config, cursor, conn)
        else:
            # 循环执行模式
            print("Mode: Loop")
            if args.time_limit > 0:
                print(f"Time limit set to: {args.time_limit} seconds")

            while True:
                try:
                    # 检查运行时间是否超过限制
                    if args.time_limit > 0:
                        elapsed = time.time() - start_timestamp
                        if elapsed > args.time_limit:
                            print(f"Time limit reached ({elapsed:.1f}s > {args.time_limit}s). Exiting gracefully.")
                            break
                    
                    # 检查是否需要夜间休眠
                    if should_sleep():
                        # 获取当前北京时间小时
                        current_bj_hour = (datetime.utcnow().hour + 8) % 24
                        sleep_hours = 7 - current_bj_hour
                        print(f"Sleeping for {sleep_hours} hours (Night Mode)...")
                        # 如果在Github Action中，夜间休眠可能意味着直接结束本次运行以免浪费资源
                        if args.time_limit > 0:
                             print("Night mode in Action, exiting.")
                             break
                        time.sleep(sleep_hours * 3600)
                        continue
                    
                    run_check(rss_config, cursor, conn)

                    # 每次检查间隔
                    sleep_interval = 600 # 10分钟
                    
                    if args.time_limit > 0:
                        elapsed = time.time() - start_timestamp
                        remaining = args.time_limit - elapsed
                        if remaining <= 0:
                            print("Time limit reached. Exiting before sleep.")
                            break
                        
                        # 如果剩余时间不足一个完整的睡眠周期，就只睡剩下的时间并退出
                        if remaining < sleep_interval:
                            print(f"Time remaining ({remaining:.1f}s) is less than sleep interval. Sleeping for {remaining:.1f}s and then exiting.")
                            if remaining > 0:
                                time.sleep(remaining)
                            break
                    
                    print(f"Waiting {sleep_interval}s for next check...")
                    time.sleep(sleep_interval)

                except Exception as e:
                    print(f"Error in loop: {str(e)}")
                    # 发生错误时缩短睡眠时间，尝试恢复
                    time.sleep(60)
    except Exception as e:
        print(f"Main Error: {str(e)}")
    finally:
        conn.close()
        print("Monitor Ended")

def run_check(rss_config, cursor, conn):
    for website, config in rss_config.items():
        website_name = config.get("website_name", website)
        rss_url = config.get("rss_url")
        if not rss_url: continue
        
        check_for_updates(rss_url, website_name, cursor, conn)

if __name__ == "__main__":
    main()
