import time
import logging
from logging.handlers import RotatingFileHandler
import os



# ---------------------------------------------------------
# 配置参数
# 选择你的执行方式 WindowsOnly 或者 alwaysWork
# WindowsOnly 不需要安装其他的package
from WindowsOnly import aNetTry 
USER_SID = ""
USER_PWD = ""
CHECK_INTERVAL = 60      # 每 60 秒检查一次网络状态
# ---------------------------------------------------------

def setup_logging():
    """配置日志：同时输出到文件和控制台"""
    logger = logging.getLogger("CampusNet")
    logger.setLevel(logging.INFO)
    
    # 格式：时间 - 级别 - 内容
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # 1. 文件日志：每个文件 2MB，保留 5 个备份，防止硬盘撑爆
    log_file = os.path.join(os.path.dirname(__file__), "network.log")
    file_handler = RotatingFileHandler(log_file, maxBytes=2*1024*1024, backupCount=2, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # 2. 控制台日志：方便查看实时状态
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

def run_manager():
    logger = setup_logging()
    logger.info("=== 校园网自动维护脚本已启动 ===")
    
    while True:
        try:
            # 调用你的函数
            # aNetTry 逻辑：
            # - 如果有网，返回 False
            # - 如果没网且登录成功，返回 True
            logger.info("正在检查网络连接...")
            status = aNetTry(USER_SID, USER_PWD)
            
            if status:
                logger.info("检测到网络中断，已成功重新触发登录。")
                # 登录成功后，可以稍微多等一会儿让网络稳定
                time.sleep(CHECK_INTERVAL)
            else:
                # 返回 False 说明 getNetworkStatus() 是 True，即网络正常
                logger.info("当前网络正常，无需操作。")
                time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            logger.info("用户手动停止了脚本。")
            break
        except Exception as e:
            logger.error(f"脚本执行出错: {str(e)}")
            # 出错后等待 10 秒重试，避免死循环导致日志刷屏
            time.sleep(10)

if __name__ == "__main__":
    run_manager()