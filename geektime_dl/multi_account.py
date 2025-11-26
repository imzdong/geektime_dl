# coding=utf8

import os
import json
import random
import time
from typing import List, Dict


class MultiAccountManager:
    """多账号管理器，通过轮换账号避免451错误"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or os.path.expanduser("~/.geektime_dl/accounts.json")
        self.accounts = self._load_accounts()
        self.current_account_index = 0
        self.current_usage = 0
        self.max_usage_per_account = 20  # 每个账号最多使用20次
        
    def _load_accounts(self) -> List[Dict]:
        """加载多个账号配置"""
        if not os.path.exists(self.config_file):
            print(f"❌ 账号配置文件不存在: {self.config_file}")
            print("请创建配置文件，格式示例：")
            print(json.dumps([
                {
                    "name": "账号1",
                    "auth_token": "cookie1...",
                    "auth_type": "token"
                },
                {
                    "name": "账号2", 
                    "auth_token": "cookie2...",
                    "auth_type": "token"
                }
            ], indent=2, ensure_ascii=False))
            return []
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载账号配置失败: {e}")
            return []
    
    def get_next_account(self) -> Dict:
        """获取下一个可用账号"""
        if not self.accounts:
            raise Exception("没有可用的账号配置")
            
        # 检查当前账号使用次数
        if self.current_usage >= self.max_usage_per_account:
            self._switch_to_next_account()
            
        account = self.accounts[self.current_account_index].copy()
        account['name'] = f"{account.get('name', 'Unknown')} ({self.current_account_index + 1})"
        self.current_usage += 1
        
        print(f"🔄 切换到账号: {account['name']} (使用次数: {self.current_usage}/{self.max_usage_per_account})")
        return account
    
    def _switch_to_next_account(self):
        """切换到下一个账号"""
        self.current_usage = 0
        self.current_account_index = (self.current_account_index + 1) % len(self.accounts)
        
        # 切换账号后等待更长时间
        wait_time = random.uniform(60, 120)  # 1-2分钟冷却
        print(f"🔄 账号使用次数达到上限，切换到下一个账号，休息{wait_time:.1f}秒...")
        time.sleep(wait_time)
    
    def reset_usage(self):
        """重置使用计数"""
        self.current_usage = 0
        self.current_account_index = 0
    
    def get_status(self) -> str:
        """获取当前状态"""
        if not self.accounts:
            return "无可用账号"
            
        current = self.accounts[self.current_account_index]
        return f"当前账号: {current.get('name', 'Unknown')} ({self.current_usage}/{self.max_usage_per_account})"


def create_sample_config():
    """创建示例配置文件"""
    config_file = os.path.expanduser("~/.geektime_dl/accounts.json")
    
    sample_config = [
        {
            "name": "主账号",
            "auth_token": "_ga=GA1.2...; LF_ID=...; GCESS=...",  # 替换为真实cookie
            "auth_type": "token"
        },
        {
            "name": "备用账号1", 
            "auth_token": "_ga=GA1.2...; LF_ID=...; GCESS=...",  # 替换为真实cookie
            "auth_type": "token"
        }
    ]
    
    try:
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)
        print(f"✅ 示例配置已创建: {config_file}")
        print("请编辑配置文件，替换为真实的cookie")
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")


if __name__ == '__main__':
    # 创建示例配置
    create_sample_config()