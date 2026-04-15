# 🚀 USTB 校园网自动连接脚本 (Campus-Linker)

这是一个基于 Python 编写的自动化脚本，用于监控校园网（USTB）的连接状态。当检测到网络断开时，脚本会自动通过抓包构造的认证 URL 发起登录请求，实现“无感”重连。

适用于北京科技大学

现在只在USTB_Student下测试过，如果有bug欢迎在issue讨论或提交PR

## 使用说明
如果想要即插即用的日志及循环框架，请使用`fileYouNeed.py`文件
``` python
# ---------------------------------------------------------
# 配置参数
# WindowsOnly: 无需安装第三方库 (使用 subprocess)
# alwaysWork: 跨平台兼容性更好 (需安装 requests 和 netifaces)
from WindowsOnly import aNetTry 
USER_SID = ""
USER_PWD = ""
CHECK_INTERVAL = 60      # 每 60 秒检查一次网络状态
# ---------------------------------------------------------

``` 

 📦 依赖环境
运行此脚本需要安装以下 Python 库：
```bash
pip install requests netifaces
```

更加详细的说明：

若使用这个框架文件，提供的接口有仅适用windows的`WindowsOnly.py`和跨平台的`alwaysWork.py`中的`aNetTry()`,按需使用即可
`USER_SID`和`USER_PWD`为你的学号和校园网密码，正确填写是成功登入的保障

`allInOne.py`文件中包含了你需要的一切，跨平台且包含日志，你可以将其编译成可执行文件

## 🛠️ 核心逻辑说明

该脚本主要通过以下四个步骤实现自动化维护：

### 1. 网络状态监控 (`getNetworkStatus`)
通过向 `https://baidu.com` 发起轻量级请求：
* 如果返回 `200`，判定网络正常。
* 如果请求失败或超时，触发后续的自动登录流程。

### 2. 本地信息获取 (`getIP` & `get_gateway`)
利用 `socket` 和 `netifaces` 库动态获取设备当前的：
* **IPv4 地址**：筛选 `10.x.x.x` 网段的内网地址。
* **IPv6 地址**：筛选以 `2001` 开头的公网 IPv6 地址。
* **默认网关**：作为参数的一部分，确保请求发送至正确的接入点。

### 3. URL 构造 (基于抓包数据)
通过对校园网 Portal 认证页面的抓包分析，构造出包含校验参数的请求地址。

**核心参数解析：**

| 参数名 | 含义 | 来源 |
| :--- | :--- | :--- |
| `user_account` | 用户账号 | 格式为 `,0,学号` (需 `quote` 编码) |
| `user_password` | 登录密码 | 用户原始密码 (需 `quote` 编码) |
| `wlan_user_ip` | 本地 IPv4 | 动态获取 |
| `wlan_ac_ip` | 接入控制器 IP | 抓包锁定为 `10.0.124.98` |
| `v` | 随机数校验 | 1000-9999 随机数，防止请求缓存 |

### 4. 结果解析 (`getResultFromJsonP`)
由于服务器返回的是 JSONP 格式数据（如 `dr1004({"result":1, ...})`），脚本使用正则表达式检测字符串中是否包含 **"成功"** 关键字，以此判定认证是否最终完成。

