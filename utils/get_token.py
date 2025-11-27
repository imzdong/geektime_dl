#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
极客时间Token获取工具

这个脚本帮助用户从浏览器cookies中获取极客时间的认证token
"""

import json
import sys
import argparse
from urllib.parse import unquote

def parse_cookies_string(cookies_str):
    """
    解析cookie字符串，提取极客时间相关的token信息
    """
    cookies = {}
    for cookie_pair in cookies_str.split(';'):
        if '=' in cookie_pair:
            name, value = cookie_pair.strip().split('=', 1)
            cookies[name] = unquote(value)
    
    # 查找极客时间相关的token
    token_candidates = [
        'GCLOUD', 'GCESS', 'SERVERID', 'token', 'SESSION', 'sessionid'
    ]
    
    tokens = {}
    for name in token_candidates:
        if name in cookies:
            tokens[name] = cookies[name]
    
    return tokens

def main():
    parser = argparse.ArgumentParser(description='极客时间Token获取工具')
    parser.add_argument('--cookies', help='浏览器cookie字符串')
    parser.add_argument('--file', help='从文件读取cookie字符串')
    
    args = parser.parse_args()
    
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                cookies_str = f.read().strip()
        except Exception as e:
            print(f"读取文件失败: {e}")
            return 1
    elif args.cookies:
        cookies_str = args.cookies
    else:
        print("使用方法:")
        print("1. 从浏览器开发者工具复制极客时间的cookie")
        print("2. 运行: python get_token.py --cookies 'your_cookies_here'")
        print("3. 或者将cookie保存到文件中: python get_token.py --file cookies.txt")
        print("\n如何获取cookie:")
        print("1. 在浏览器中登录极客时间")
        print("2. 按F12打开开发者工具")
        print("3. 切换到Network标签")
        print("4. 刷新页面，找到任意请求")
        print("5. 在请求头中找到Cookie字段，复制完整值")
        return 0
    
    if not cookies_str:
        print("错误: 未提供cookie字符串")
        return 1
    
    tokens = parse_cookies_string(cookies_str)
    
    if not tokens:
        print("未找到极客时间相关的token信息")
        return 1
    
    print("找到以下token信息:")
    print("=" * 50)
    
    for name, value in tokens.items():
        print(f"{name}: {value}")
    
    print("\n推荐的登录配置:")
    print("=" * 50)
    print("# 方式一: 使用完整cookie字符串")
    print(f"geektime login --auth-token \"{cookies_str}\" --auth-type token")
    print("\n# 方式二: 使用单个token（如果有）")
    
    main_token = None
    for name in ['GCLOUD', 'token', 'SESSION']:
        if name in tokens:
            main_token = tokens[name]
            print(f"geektime login --auth-token \"{main_token}\" --auth-type token")
            break
    
    if not main_token:
        print("使用完整cookie字符串进行登录")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())