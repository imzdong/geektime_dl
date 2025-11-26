# coding=utf8

import os
import json
import time
from typing import Dict, List, Optional


class DownloadProgress:
    """下载进度管理器"""
    
    def __init__(self, course_id: int, cache_dir: str = None):
        self.course_id = course_id
        self.cache_dir = cache_dir or os.path.expanduser("~/.geektime_dl")
        self.progress_file = os.path.join(self.cache_dir, f"progress_{course_id}.json")
        
        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def save_progress(self, downloaded_articles: List[int], total_articles: int, 
                     start_time: float = None) -> None:
        """保存下载进度"""
        progress_data = {
            'course_id': self.course_id,
            'downloaded_articles': downloaded_articles,
            'total_articles': total_articles,
            'last_update': time.time(),
            'start_time': start_time or time.time()
        }
        
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存进度失败: {e}")
    
    def load_progress(self) -> Optional[Dict]:
        """加载下载进度"""
        if not os.path.exists(self.progress_file):
            return None
        
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载进度失败: {e}")
            return None
    
    def get_downloaded_articles(self) -> List[int]:
        """获取已下载的文章ID列表"""
        progress = self.load_progress()
        if progress:
            return progress.get('downloaded_articles', [])
        return []
    
    def update_progress(self, article_id: int) -> None:
        """更新进度，添加新下载的文章"""
        progress = self.load_progress() or {
            'course_id': self.course_id,
            'downloaded_articles': [],
            'total_articles': 0,
            'start_time': time.time()
        }
        
        if article_id not in progress['downloaded_articles']:
            progress['downloaded_articles'].append(article_id)
            progress['last_update'] = time.time()
            
            self.save_progress(
                progress['downloaded_articles'],
                progress['total_articles'],
                progress['start_time']
            )
    
    def clear_progress(self) -> None:
        """清除进度文件"""
        try:
            if os.path.exists(self.progress_file):
                os.remove(self.progress_file)
        except Exception as e:
            print(f"清除进度失败: {e}")
    
    def get_progress_summary(self) -> str:
        """获取进度摘要"""
        progress = self.load_progress()
        if not progress:
            return "暂无下载进度"
        
        downloaded = len(progress['downloaded_articles'])
        total = progress['total_articles']
        
        if total > 0:
            percentage = (downloaded / total) * 100
            return f"进度: {downloaded}/{total} ({percentage:.1f}%)"
        else:
            return f"已下载: {downloaded} 篇文章"
    
    def is_completed(self) -> bool:
        """检查是否下载完成"""
        progress = self.load_progress()
        if not progress:
            return False
        
        downloaded = len(progress['downloaded_articles'])
        total = progress['total_articles']
        
        return total > 0 and downloaded >= total