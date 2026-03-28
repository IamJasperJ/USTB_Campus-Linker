import requests
import random
import time
from urllib.parse import quote
import uuid
from socket import *
def getIP():
    hostname = gethostname()
    ip_ls = [x[4][0] for x in getaddrinfo(hostname, None)]
    # print(ip_ls)
    addv4, addv6, cnt = '', '', 0
    for ip in ip_ls:
        if '2001' in ip:
            addv6 = ip
            cnt += 1
        elif '10.' in ip and ip != '10.110.120.3':
            addv4 = ip
            cnt += 1
        if cnt == 2:
            break
    return addv4, addv6     
def get_mac_address():
    mac_int = uuid.getnode()  # 获取 MAC 地址（整数形式）
    if mac_int == 0:  # 虚拟化环境可能返回 0
        return "Unknown"
    mac_str = f"{mac_int:012x}"  # 转换为 12 位 16 进制字符串（小写）
    return mac_str
def getNetworkStatus():
    for _ in range(5):
        try:
            x = requests.get('https://baidu.com', timeout=20)
            if x.status_code == 200:
                return x.status_code
            time.sleep(.5)
            continue
        except requests.exceptions.Timeout:
            print("网络连接请求超时(20 秒未收到响应）")
            continue
        except requests.exceptions.RequestException as e:
            print(f"网络连接请求失败：{e}")
            continue
    return False
def getVtext(SID, password):
    addv4, addv6 = getIP()
    mac = get_mac_address()
    SID = ',0,' + SID
    # print(addv4 + '\t' + addv6)
    text = 'http://202.204.48.66:801/eportal/portal/' \
           'login?callback=dr1004&login_method=1' \
           f'&user_account={quote(SID)}' \
           f'&user_password={quote(password)}' \
           f'&wlan_user_ip={quote(addv4)}' \
           f'&wlan_user_ipv6={quote(addv6)}' \
           f'&wlan_user_mac={quote(mac)}' \
           '&wlan_ac_ip=10.0.124.98' \
           '&wlan_ac_name=WX5560H' \
           '&jsVersion=4.1' \
           '&terminal_type=3' \
           '&lang=zh-cn' \
           f'&v={random.randint(1000, 9999)}' \
            '&lang=zh'
    return text
def submitVerification(text):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'http://202.204.48.66/' # 有些系统会校验来源页
    }
    for i in range(5):
        try:
            print(f"The {i + 1}-th try.")
            # 加入 headers 参数
            x = requests.get(text, headers=headers, timeout=20)
            time.sleep(5)
            print(f"服务器返回: {x.text}")
            return x.status_code == 200
        except Exception as e:
            print(f"请求失败: {e}")
            continue
    return False
    
if __name__ == '__main__':
    Sid = ''
    password  = ''
    assert Sid != '' and password != '', "Sid and Password is empty."
    while True:
        if getNetworkStatus() == False:
            print("network broken.")
            while(submitVerification(getVtext(Sid, password)) != True):
                print("try again")
                time.sleep(10)
            print('reconnect')
        print('network okay')
        time.sleep(10)