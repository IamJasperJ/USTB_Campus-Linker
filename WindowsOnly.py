import requests
import time
import random
from urllib.parse import quote
import subprocess
import json
import re
def getResultFromJsonP(text):
    match = re.search(r'成功', text)
    if match:
        return True
    return False
    
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
            return getResultFromJsonP(x.text)
        except Exception as e:
            print(f"请求失败: {e}")
            continue
    return False

def getnetinfo():
    # 构造 PowerShell 脚本，将结果转换为 JSON 格式方便 Python 解析
    ps_script = (
        "Get-NetIPConfiguration -InterfaceAlias *WLAN* | Select-Object "
        "InterfaceAlias, "
        "@{Name='IPv4'; Expression={$_.IPv4Address.IPAddress}}, "
        "@{Name='IPv6'; Expression={$_.IPv6Address.IPAddress}}, "
        "@{Name='Gateway'; Expression={$_.IPv4DefaultGateway.NextHop}}, "
        "@{Name='MAC'; Expression={(Get-NetAdapter -Name $_.InterfaceAlias).MacAddress}} "
        "| ConvertTo-Json"
    )

    try:
        # 执行 PowerShell 命令
        raw_output = subprocess.check_output(["powershell", "-Command", ps_script], encoding='gbk')
        print(raw_output)
        # 解析 JSON 数据
        data = json.loads(raw_output)
        # print("--- 网络配置信息 ---")
        # print(f"网卡名称: {data.get('InterfaceAlias')}")
        # print(f"IPv4 地址: {data.get('IPv4')}")
        # print(f"IPv6 地址: {data.get('IPv6')}")
        # print(f"IPv4 网关: {data.get('Gateway')}")
        # print(f"MAC 地址 : {data.get('MAC')}")
    except Exception as e:
        print(f"获取失败，请检查网卡名称或网络连接。错误详情: {e}")
    return data.get('IPv4'), data.get('IPv6'), data.get('Gateway'), data.get('MAC')

def getLoad(SID, password):
    addv4, addv6, mac, router = getnetinfo()
    SID = ',0,' + SID
    # print(addv4 + '\t' + addv6)
    text = 'http://202.204.48.66:801/eportal/portal/' \
           'login?callback=dr1004&login_method=1' \
           f'&user_account={quote(SID)}' \
           f'&user_password={quote(password)}' \
           f'&wlan_user_ip={quote(addv4)}' \
           f'&wlan_user_ipv6={quote(addv6)}' \
           f'&wlan_user_mac={quote(mac)}' \
           f'&wlan_ac_ip={quote("10.0.124.98")}' \
           '&wlan_ac_name=WX5560H' \
           '&jsVersion=4.1' \
           '&terminal_type=3' \
           '&lang=zh-cn' \
           f'&v={random.randint(1000, 9999)}' \
            '&lang=zh'
    return text

def getNetworkStatus():
    try:
        result = subprocess.run(
            ["powershell", "-Command", "ping -n 1 -w 1000 baidu.com"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception:
        return False

def aNetTry(sid, password):
    # 进行一次网络测试
    assert sid != '' and password != '', "sid and Password is empty."
    if getNetworkStatus() == False:
        print("network broken.")
        while(submitVerification(getLoad(sid, password)) != True):
            print("try again")
            time.sleep(10)
        return True
    return False

if __name__ == '__main__':
    # 输入学号和校园网密码
    # 如果非用于测试，务必修改最后一行的阻塞时间 !
    Sid = ''
    password  = ''
    assert Sid != '' and password != '', "Sid and Password is empty."
    while True:
        if getNetworkStatus() == False:
            print("network broken.")
            while(submitVerification(getLoad(Sid, password)) != True):
                print("try again")
                time.sleep(10)
            print('reconnect')
        print('network okay')
        time.sleep(10)