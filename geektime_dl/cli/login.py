# coding=utf8

import sys

from geektime_dl.gt_apis import GkApiClient, GkApiError
from geektime_dl.cli import Command, add_argument


class Login(Command):
    """登录极客时间，支持账号密码或token认证，保存认证信息至配置文件"""

    def run(self, args: dict):
        area = args['area']
        account = args['account']
        password = args['password']
        auth_token = args.get('auth_token')
        auth_type = args.get('auth_type', 'password')
        
        # 判断使用哪种认证方式
        use_token = auth_token and auth_type == 'token'
        
        if use_token:
            # Token认证方式
            need_save = not auth_token
            
            if not auth_token:
                auth_token = input("enter your auth token: ")
                
            try:
                # 测试token是否有效
                client = GkApiClient(auth_token=auth_token, auth_type='token')
                course_list = client.get_course_list()
                
                if need_save:
                    new_cfg = {
                        'auth_token': auth_token,
                        'auth_type': 'token'
                    }
                    Command.save_cfg(new_cfg, args['config'])
                
                sys.stdout.write("Token login succeed\n")
                
            except GkApiError as e:
                sys.stdout.write(
                    "token login fail, error message:{}\n"
                    "Please check your token and try again\n".format(e)
                )
                sys.exit(1)
        else:
            # 传统账号密码认证方式
            need_save = not (area and account and password)

            if not account:
                account = input("enter your registered account(phone): ")
            if not area:
                area = input("enter country code: enter for 86 ") or '86'
            if not password:
                password = input("account: +{} {}\n"
                                 "enter password: ".format(area, account))

            try:
                GkApiClient(account=account, password=password, area=area)
                if need_save:
                    new_cfg = {
                        'account': account,
                        'password': password,
                        'area': area,
                        'auth_type': 'password'
                    }
                    Command.save_cfg(new_cfg, args['config'])

            except GkApiError as e:
                sys.stdout.write(
                    "login fail, error message:{}\nEnter again\n".format(e)
                )
                area = input("enter country code: enter for 86 ") or '86'
                account = input("enter your registered account(phone): ")
                password = input("account: +{} {}\n"
                                 "enter password: ".format(area, account))

                GkApiClient(account=account, password=password, area=area)

                new_cfg = {
                    'account': account,
                    'password': password,
                    'area': area,
                    'auth_type': 'password'
                }
                Command.save_cfg(new_cfg, args['config'])

            sys.stdout.write("Login succeed\n")





