# coding=utf8


import threading
import functools
import time
import contextlib
from typing import Optional, Union
import json
from datetime import datetime, timedelta

import requests

from geektime_dl.utils import (
    synchronized,
    Singleton,
    get_random_user_agent
)
from geektime_dl.log import logger


class GkApiError(Exception):
    """"""


def _retry(func):
    """
    重试机制，支持10次递增重试
    - 网络错误：1s, 2s, 3s, 4s, 5s, 6s, 7s, 8s, 9s
    - 验证码错误：5s, 10s, 15s, 20s, 25s, 30s, 35s, 40s, 45s
    """
    @functools.wraps(func)
    def wrap(gk_api: 'GkApiClient', *args, **kwargs):
        max_retries = 10
        for attempt in range(max_retries):
            try:
                res = func(gk_api, *args, **kwargs)
                return res
            except requests.RequestException:
                if attempt < max_retries - 1:
                    wait_time = 1 + attempt  # 递增延迟：1s, 2s, 3s...
                    print(f"网络错误，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    # 只有在密码认证时才reset_session
                    if hasattr(gk_api, '_auth_type') and gk_api._auth_type != 'token':
                        if hasattr(gk_api, 'reset_session'):
                            gk_api.reset_session()
                    continue
                else:
                    print(f"❌ 网络错误重试{max_retries}次后仍然失败，终止重试")
                    raise
            except GkApiError as e:
                # 对于验证码错误，重试
                if "非法图形验证码" in str(e) and attempt < max_retries - 1:
                    wait_time = 5 + attempt * 5  # 递增延迟：5s, 10s, 15s...
                    print(f"遇到验证码限制，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                elif "非法图形验证码" in str(e):
                    print(f"❌ 验证码错误重试{max_retries}次后仍然失败，请稍后再试")
                    raise
                else:
                    raise
            except Exception as e:
                raise GkApiError("geektime api error") from e

    return wrap


class GkApiClient:
    """
    一个课程，包括专栏、视频、微课等，称作 `course` 或者 `column`
    课程下的章节，包括文章、者视频等，称作 `post` 或者 `article`
    """

    def __init__(self, account: str = None, password: str = None, area: str = '86',
                 no_login: bool = False, lazy_login: bool = True,
                 cookies: Optional[dict] = None, auth_token: str = None,
                 auth_type: str = 'password'):
        self._cookies = None
        self._lock = threading.Lock()
        self._account = account
        self._password = password
        self._area = area
        self._no_login = no_login
        self._ua = get_random_user_agent()
        self._auth_token = auth_token
        self._auth_type = auth_type  # 'password' or 'token'

        if cookies:
            self._cookies = cookies
            return

        if lazy_login or no_login:
            # 对于token认证，即使lazy_login也需要立即登录
            if auth_token and auth_type == 'token':
                self._login_with_token()
            return
            
        # 如果提供了token，使用token登录
        if auth_token and auth_type == 'token':
            self._login_with_token()
        else:
            self.reset_session()

    def _post(self, url: str, data: dict = None, **kwargs) -> requests.Response:
        with contextlib.suppress(Exception):
            for k in ['cellphone', 'password']:
                if data and k in data:
                    data[k] = 'xxx'
            logger.info("request geektime api, {}, {}".format(url, data))

        headers = kwargs.setdefault('headers', {})
        headers.update({
            'Content-Type': 'application/json',
            'User-Agent': self._ua,
            'Referer': 'https://time.geekbang.org/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://time.geekbang.org',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'DNT': '1',
            'Connection': 'keep-alive'
        })
        
        # 如果使用token认证，添加Authorization头（主要用于JWT）
        if self._auth_type == 'token' and self._auth_token and self._auth_token.count('.') >= 2 and len(self._auth_token.split('.')) == 3:
            headers['Authorization'] = f'Bearer {self._auth_token}'
        
        # 增强的超时和会话配置
        session = requests.Session()
        session.headers.update(headers)
        
        # 支持代理（如需要）
        # proxies = {'http': 'http://proxy.example.com:8080', 'https': 'https://proxy.example.com:8080'}
        # if os.environ.get('GEEKTIME_PROXY'):
        #     session.proxies.update(proxies)
        
        # 处理cookies参数
        cookies = kwargs.pop('cookies', None)
        
        # 增加超时时间和重试配置
        timeout = 30  # 增加到30秒
        
        try:
            if cookies:
                if isinstance(cookies, dict):
                    # 如果cookies是字典，直接使用
                    resp = session.post(url, json=data, cookies=cookies, timeout=timeout, **kwargs)
                else:
                    # 如果cookies是其他类型（如CookieJar），转换为字典
                    import http.cookiejar
                    if isinstance(cookies, http.cookiejar.CookieJar):
                        cookies_dict = {}
                        for cookie in cookies:
                            cookies_dict[cookie.name] = cookie.value
                        resp = session.post(url, json=data, cookies=cookies_dict, timeout=timeout, **kwargs)
                    else:
                        resp = session.post(url, json=data, cookies=cookies, timeout=timeout, **kwargs)
            else:
                resp = session.post(url, json=data, timeout=timeout, **kwargs)
        finally:
            session.close()
            
        resp.raise_for_status()

        if resp.json().get('code') != 0:
            raise GkApiError('geektime api fail:' + resp.json()['error']['msg'])

        return resp

    @synchronized()
    def reset_session(self) -> None:
        """使用账号密码登录"""
        url = 'https://account.geekbang.org/account/ticket/login'

        self._ua = get_random_user_agent()
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',  # noqa: E501
            'Host': 'account.geekbang.org',
            'Referer': 'https://account.geekbang.org/signin?redirect=https%3A%2F%2Fwww.geekbang.org%2F',  # noqa: E501
        }

        data = {
            "country": self._area,
            "cellphone": self._account,
            "password": self._password,
            "captcha": "",
            "remember": 1,
            "platform": 3,
            "appid": 1
        }

        resp = self._post(url, data, headers=headers)

        self._cookies = resp.cookies

    @synchronized()
    def _login_with_token(self) -> None:
        """使用token登录"""
        if not self._auth_token:
            raise GkApiError("Token is required for token-based authentication")
            
        # 创建cookies字典
        cookies_dict = {}
        
        # 解析token并设置到cookies中
        try:
            # 优先检查是否为完整cookie字符串格式 (包含多个key=value)
            if '=' in self._auth_token and ';' in self._auth_token:
                # 完整cookie字符串格式: "key1=value1; key2=value2"
                for cookie_pair in self._auth_token.split(';'):
                    if '=' in cookie_pair:
                        name, value = cookie_pair.strip().split('=', 1)
                        cookies_dict[name.strip()] = value.strip()
            elif self._auth_token.count('.') >= 2 and len(self._auth_token.split('.')) == 3:
                # JWT token格式 (xxx.yyy.zzz)
                # JWT通常用于Authorization头，不设置cookies
                pass
            elif '=' in self._auth_token:
                # 单个key=value格式的token
                name, value = self._auth_token.strip().split('=', 1)
                cookies_dict[name.strip()] = value.strip()
            
            self._cookies = cookies_dict
            
        except Exception as e:
            raise GkApiError(f"Failed to parse token: {e}")

    def set_auth_token(self, token: str, auth_type: str = 'token') -> None:
        """设置认证token"""
        self._auth_token = token
        self._auth_type = auth_type
        
    def get_auth_info(self) -> dict:
        """获取当前认证信息"""
        return {
            'auth_type': self._auth_type,
            'account': self._account if self._auth_type == 'password' else None,
            'has_token': bool(self._auth_token),
            'has_cookies': bool(self._cookies),
            'cookies_type': type(self._cookies).__name__ if self._cookies else None,
            'cookies_content': str(self._cookies)[:100] + "..." if self._cookies and len(str(self._cookies)) > 100 else str(self._cookies)
        }

    @_retry
    def get_course_list(self) -> dict:
        """
        获取课程列表
        :return:
            key: value
            '1'
            '2'
            '3'
            '4':
        """
        url = 'https://time.geekbang.org/serv/v1/column/all'
        headers = {
            'Referer': 'https://time.geekbang.org/paid-content',
        }
        if not self._cookies and not self._no_login:
            if self._auth_type == 'token' and self._auth_token:
                self._login_with_token()
            else:
                self.reset_session()

        resp = self._post(url, headers=headers, cookies=self._cookies)
        return resp.json()['data']

    @_retry
    def get_post_list_of(self, course_id: int) -> list:
        """获取课程所有章节列表"""
        url = 'https://time.geekbang.org/serv/v1/column/articles'
        data = {
            "cid": str(course_id), "size": 1000, "prev": 0, "order": "newest"
        }
        headers = {
            'Referer': 'https://time.geekbang.org/column/{}'.format(course_id),
        }

        if not self._cookies and not self._no_login:
            if self._auth_type == 'token' and self._auth_token:
                self._login_with_token()
            else:
                self.reset_session()

        resp = self._post(url, data, headers=headers, cookies=self._cookies)

        if not resp.json()['data']:
            raise Exception('course not exists:%s' % course_id)

        return resp.json()['data']['list'][::-1]

    @_retry
    def get_course_intro(self, course_id: int) -> dict:
        """课程简介"""
        url = 'https://time.geekbang.org/serv/v1/column/intro'
        headers = {
            'Referer': 'https://time.geekbang.org/column/{}'.format(course_id),
        }

        if not self._cookies and not self._no_login:
            if self._auth_type == 'token' and self._auth_token:
                self._login_with_token()
            else:
                self.reset_session()

        resp = self._post(
            url, {'cid': str(course_id)}, headers=headers, cookies=self._cookies
        )

        data = resp.json()['data']
        if not data:
            raise GkApiError('无效的课程 ID: {}'.format(course_id))
        return data

    @_retry
    def get_post_content(self, post_id: int) -> dict:
        """课程章节详情"""
        url = 'https://time.geekbang.org/serv/v1/article'
        headers = {
            'Referer': 'https://time.geekbang.org/column/article/{}'.format(
                post_id)
        }

        if not self._cookies and not self._no_login:
            if self._auth_type == 'token' and self._auth_token:
                self._login_with_token()
            else:
                self.reset_session()

        resp = self._post(
            url, {'id': post_id}, headers=headers, cookies=self._cookies
        )

        return resp.json()['data']

    @_retry
    def get_post_comments(self, post_id: int) -> list:
        """课程章节评论"""
        url = 'https://time.geekbang.org/serv/v1/comments'
        headers = {
            'Referer': 'https://time.geekbang.org/column/article/{}'.format(
                post_id)
        }

        if not self._cookies and not self._no_login:
            if self._auth_type == 'token' and self._auth_token:
                self._login_with_token()
            else:
                self.reset_session()

        resp = self._post(
            url, {"aid": str(post_id), "prev": 0},
            headers=headers, cookies=self._cookies
        )

        return resp.json()['data']['list']

    @_retry
    def get_video_collection_intro(self, collection_id: int) -> dict:
        """每日一课合辑简介"""
        url = 'https://time.geekbang.org/serv/v2/video/GetCollectById'
        headers = {
            'Referer': 'https://time.geekbang.org/dailylesson/collection/{}'.format(  # noqa: E501
                collection_id)
        }

        if not self._cookies and not self._no_login:
            if self._auth_type == 'token' and self._auth_token:
                self._login_with_token()
            else:
                self.reset_session()

        resp = self._post(
            url, {'id': str(collection_id)},
            headers=headers, cookies=self._cookies
        )

        data = resp.json()['data']
        return data

    @_retry
    def get_video_collection_list(self) -> list:
        """每日一课合辑列表"""
        # 没分析出接口
        ids = list(range(3, 82)) + list(range(104, 141))
        return [{'collection_id': id_} for id_ in ids]

    @_retry
    def get_video_list_of(self, collection_id: int) -> list:
        """每日一课合辑视频列表"""

        url = 'https://time.geekbang.org/serv/v2/video/GetListByType'
        headers = {
            'Referer': 'https://time.geekbang.org/dailylesson/collection/{}'.format(  # noqa: E501
                collection_id)
        }

        if not self._cookies and not self._no_login:
            if self._auth_type == 'token' and self._auth_token:
                self._login_with_token()
            else:
                self.reset_session()

        resp = self._post(
            url, {"id": str(collection_id), "size": 50},
            headers=headers, cookies=self._cookies
        )

        return resp.json()['data']['list']
