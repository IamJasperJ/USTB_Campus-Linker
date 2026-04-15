import time
import random
import logging
from logging.handlers import RotatingFileHandler
from urllib.parse import quote
# 核心网络请求改用标准库
import urllib.request
import urllib.parse

# --- 日志配置 (保持不变，因为 logging 是标准库，开销极小) ---
log_filename = "connect_log.txt"
log_format = '%(asctime)s - %(levelname)s - %(message)s'
file_handler = RotatingFileHandler(log_filename, maxBytes=1024 * 1024, backupCount=3, encoding='utf-8')
stream_handler = logging.StreamHandler()
logging.basicConfig(level=logging.INFO, format=log_format, handlers=[file_handler, stream_handler])

def getIP():
    from socket import gethostname, getaddrinfo
    try:
        hostname = gethostname()
        addr_info = getaddrinfo(hostname, None)
        addv4, addv6 = '', ''
        for item in addr_info:
            ip = item[4][0]
            if ':' in ip and '2001' in ip:
                addv6 = ip
            elif '.' in ip and ip.startswith('10.') and ip != '10.110.120.3':
                addv4 = ip
            if addv4 and addv6: break
        return addv4, addv6
    except Exception as e:
        logging.error(f"获取IP失败: {e}")
        return '', ''

def get_mac_address():
    import uuid
    mac_int = uuid.getnode()
    return f"{mac_int:012x}" if mac_int != 0 else "Unknown"

def getNetworkStatus():
    """使用标准库检测网络状态"""

    # 不跟随重定向
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def http_error_302(self, req, fp, code, msg, headers):
            raise urllib.request.HTTPError(req.get_full_url(), code, msg, headers, fp)
        http_error_301 = http_error_303 = http_error_307 = http_error_302
    opener = urllib.request.build_opener(NoRedirect())

    for _ in range(3):
        try:
            with opener.open('http://www.baidu.com', timeout=5) as response:
                if response.getcode() == 200:
                    return True
        except:
            continue
    return False

def getVtext(SID, password):
    addv4, addv6 = getIP()
    mac = get_mac_address()
    full_sid = ',0,' + SID
    
    url = 'http://202.204.48.66:801/eportal/portal/login?callback=dr1004&login_method=1' \
          f'&user_account={quote(full_sid)}' \
          f'&user_password={quote(password)}' \
          f'&wlan_user_ip={quote(addv4)}' \
          f'&wlan_user_ipv6={quote(addv6)}' \
          f'&wlan_user_mac={quote(mac)}' \
          '&wlan_ac_ip=10.0.124.98' \
          '&wlan_ac_name=WX5560H' \
          '&jsVersion=4.1' \
          '&terminal_type=3' \
          '&lang=zh-cn' \
          f'&v={random.randint(1000, 9999)}&lang=zh'
    return url

def submitVerification(url):
    """使用标准库发送认证请求"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'http://202.204.48.66/'
    }
    for i in range(5):
        try:
            logging.info(f"正在进行第 {i + 1} 次认证尝试...")
            # 构造 Request 对象以添加 Headers
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                res_text = response.read().decode('utf-8')
                time.sleep(1)
                if "成功" in res_text or "result\":1" in res_text:
                    logging.info(f"认证成功: {res_text[:60]}")
                    return True
                else:
                    logging.warning(f"响应异常: {res_text[:100]}")
        except Exception as e:
            logging.error(f"网络异常: {e}")
            time.sleep(2)
    return False

if __name__ == '__main__':
    Sid = ''
    password  = ''
    logging.info("=== 校园网自动连接助手启动 ===")
    
    while True:
        if not getNetworkStatus():
            logging.warning("离线确认，开始重连...")
            while not submitVerification(getVtext(Sid, password)):
                logging.error("重连失败，20秒后重试...")
                time.sleep(20)
            logging.info("连接已恢复。")
        
        # 1分钟巡检一次
        time.sleep(60)