# coding=utf8

import json
import threading

from tqdm import tqdm

from geektime_dl.gt_apis import GkApiClient
from geektime_dl.utils import synchronized, read_local_cookies
from geektime_dl.cache import GeektimeCache, EmptyCache, SqliteCache
from geektime_dl.progress import DownloadProgress


class DataClient:

    def __init__(self, gk: GkApiClient, cache: GeektimeCache):
        self._gt = gk
        self._cache: GeektimeCache = cache
        self._lock = threading.Lock()  # 限制并发
        self._progress_manager = None  # 进度管理器

    def get_column_list(self, **kwargs) -> dict:
        """
        获取专栏列表
        """
        use_cache = not kwargs.get("no_cache", False)
        key = "column_all"
        expire = 1 * 24 * 3600  # 1 day
        if use_cache:
            value = self._cache.get(key)
            if value:
                return value
        data = self._gt.get_course_list()
        if use_cache:
            self._cache.set(key, data, expire)

        return data

    @synchronized()
    def get_column_intro(self, column_id: int, **kwargs) -> dict:
        """
        获取专栏简介
        """
        use_cache = not kwargs.get("no_cache", False)
        if use_cache:
            cache = self._cache.get_column_intro(column_id)
            if cache and cache['is_finish'] and cache['had_sub']:
                return cache

        course_intro = self._gt.get_course_intro(column_id)
        course_intro['column_id'] = course_intro['id']
        articles = self._gt.get_post_list_of(column_id)
        course_intro['articles'] = articles

        if use_cache:
            self._cache.save_column_intro(course_intro)

        return course_intro

    def set_progress_manager(self, course_id: int) -> None:
        """设置进度管理器"""
        self._progress_manager = DownloadProgress(course_id)
    
    @synchronized()
    def get_article_content(self, article_id: int, **kwargs) -> dict:
        """
        获取 article 的所有内容，包括评论
        支持断点续下载：如果已缓存且no_cache=False，直接返回
        """
        use_cache = not kwargs.get("no_cache", False)
        
        # 断点续下载：检查是否已缓存
        if use_cache:
            cache = self._cache.get_article(article_id)
            if cache:
                # 更新进度
                if self._progress_manager:
                    self._progress_manager.update_progress(article_id)
                return cache

        try:
            article_info = self._gt.get_post_content(article_id)
            article_info['article_id'] = article_info['id']
            article_info['comments'] = self._get_article_comments(article_id)
            
            if use_cache:
                self._cache.save_article(article_info)
                # 更新进度
                if self._progress_manager:
                    self._progress_manager.update_progress(article_id)

            return article_info
        except Exception as e:
            # 即使失败也要等待间隔时间，避免后续请求过于密集
            raise
        finally:
            # 添加请求间隔，避免触发限流
            # 更真实的访问模式：模拟人类阅读时间
            import time
            import random
            
            # 基础间隔：3-8秒（模拟阅读时间）
            base_wait = random.uniform(3.0, 8.0)
            
            # 每10篇文章后增加更长的"休息"时间
            if hasattr(self, '_request_count'):
                self._request_count += 1
            else:
                self._request_count = 1
                
            if self._request_count % 10 == 0:
                # 每10篇休息15-30秒
                extra_wait = random.uniform(15.0, 30.0)
                print(f"  🛏️  已下载{self._request_count}篇，休息{extra_wait:.1f}秒...")
                wait_time = base_wait + extra_wait
            elif self._request_count % 5 == 0:
                # 每5篇休息5-10秒
                extra_wait = random.uniform(5.0, 10.0)
                print(f"  ☕ 已下载{self._request_count}篇，休息{extra_wait:.1f}秒...")
                wait_time = base_wait + extra_wait
            else:
                wait_time = base_wait
                
            time.sleep(wait_time)

    def _get_article_comments(self, article_id: int) -> list:
        """
        获取 article 的评论
        """
        data = self._gt.get_post_comments(article_id)
        for c in data:
            c['replies'] = json.dumps(c.get('replies', []))
        return data

    def get_video_collection_list(self, **kwargs) -> list:
        """
        获取每日一课合辑列表
        """
        return self._gt.get_video_collection_list()

    @synchronized()
    def get_video_collection_intro(self, collection_id: int, **kwargs) -> dict:
        """
        获取每日一课合辑简介
        """
        data = self._gt.get_video_collection_intro(collection_id)
        return data

    @synchronized()
    def get_daily_content(self, video_id: int, **kwargs) -> dict:
        """
        获取每日一课内容
        """
        data = self._gt.get_post_content(video_id)
        return data

    def get_video_collection_content(self, collection_id: int,
                                     force: bool = False,
                                     pbar=True, pbar_desc='') -> list:
        """
        获取每日一课合辑ID 为 collection_id 的所有视频内容
        """
        data = []
        v_ids = self._gt.get_video_list_of(collection_id)
        if pbar:
            v_ids = tqdm(v_ids)
            v_ids.set_description(pbar_desc)
        for v_id in v_ids:
            v = self.get_daily_content(v_id['article_id'], force=force)
            data.append(v)
        return data


dc_global = None
_dc_global_lock = threading.Lock()


def get_data_client(cfg: dict) -> DataClient:
    with _dc_global_lock:
        global dc_global
        
        # 创建基于认证方式的key
        auth_type = cfg.get('auth_type', 'password')
        auth_token = cfg.get('auth_token')
        account = cfg.get('account')
        
        # 为不同认证方式创建不同的客户端
        cache_key = f"{auth_type}:{auth_token or account}"
        
        # 如果已有客户端且认证方式相同，返回缓存实例
        if (dc_global is not None and 
            hasattr(dc_global, '_auth_cache_key') and 
            dc_global._auth_cache_key == cache_key):
            return dc_global

        # 构建GkApiClient参数
        gk_params = {
            'no_login': cfg['no_login'],
            'lazy_login': True,
            'cookies': read_local_cookies(),
            'auth_type': auth_type
        }
        
        if auth_type == 'token':
            gk_params['auth_token'] = auth_token
        else:
            gk_params.update({
                'account': account,
                'password': cfg.get('password'),
                'area': cfg.get('area', '86')
            })

        gk = GkApiClient(**gk_params)

        if cfg.get('no_cache', False):
            cache = EmptyCache()
        else:
            cache = SqliteCache()

        dc = DataClient(gk, cache=cache)
        dc._auth_cache_key = cache_key  # 添加认证方式标识
        dc_global = dc

    return dc
