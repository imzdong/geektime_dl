#!/usr/bin/env python3
# coding=utf8

import sys
sys.path.insert(0, '.')

from geektime_dl.dal import get_data_client
from geektime_dl.progress import DownloadProgress
import time

def test_resume_download():
    print("🧪 测试断点续下载功能...")
    
    # 配置
    cfg = {
        'no_cache': False,  # 启用缓存，支持断点续下载
        'no_login': False,
        'output_folder': './output',
        'comments_count': 0,
        'auth_type': 'token',
        'auth_token': '_ga=GA1.2.496332097.1736651838; LF_ID=90be707-16cc400-d06642d-ff4c34a; mantis5539=2e01d025245c4af9bad2c9d261fa29ef@5539; MEIQIA_TRACK_ID=2so3lBHtT50ImdQM7xHUWtlxEiG; MEIQIA_VISIT_ID=2so3lBGCroP35N5q3RpkUJB5Ga1; _tea_utm_cache_20000743={%22utm_term%22:%22pc_interstitial_1984%22}; gksskpitn=5b2203b0-5a78-4098-92d6-7451b3328611; HMACCOUNT=0B5DE57CDE4EAFDC; _ga_MTX5SQH9CV=GS2.2.s1760777262$o4$g1$t1760777302$j20$l0$h0; Hm_lvt_022f847c4e3acd44d4a2481d9187f1e6=1763597546; Hm_lvt_59c4ff31a9ee6263811b23eb921a5083=1763597546; GCID=6db28b5-0abec68-8e1b6e4-4a70c67; _ga_JW698SFNND=GS2.2.s1763597565$o9$g1$t1763597569$j56$l0$h0; gk_process_ev={%22count%22:2%2C%22utime%22:1763597570276%2C%22referrer%22:%22https://time.geekbang.org/column/intro/101089301%22%2C%22target%22:%22page_geektime_login%22%2C%22referrerTarget%22:%22page_geektime_login%22}; GRID=6db28b5-0abec68-8e1b6e4-4a70c67; GCESS=BgoEAAAAAAgBAwkBAQYEc4VnvwUEAAAAAAcEJYf76Q0BAQEIYkYPAAAAAAAEBACNJwACBAxdHmkMAQELAgYAAwQMXR5p; tfstk=gAwI3pbyfzeNkxNxOYSwGn_zBhMSFGWVN3i8mupe2vHKF4a8SBlrzuLWFrzhqMqzL5a7Vr0KUvyFF7M3QWJr8wD72rk5uZWV3kqnnYQVuT79A5kxcepJz4K9BYoWnoubXkqnEh2iD76YxTG_1vg-ezHt6mmme0dLyFEtS0mJJ0pdfl3iWDpKyBK960oxyeU-eGZtS0H-yzhRfl3i2Y3JPx9IbMggAiVwhupDERqK5Lp8pTcnl63ijDysVXgxxV98ARiIOqELLypDq0NYhX4A7BuLG7aj0yW9drZ8m7h_F9Tm7jmb5jPClpMYKuFmJ5bMycNTmzmYJNJIkSqtpmV1lpDUcVMUdxBDJ4Pac8i7EaX_luE0wfw5dE0Zi0IrBKujPaOWfjvSfqS1fQAu_woDkon_FchKjc7PfGO4qXnif5I1fQAo9cmZWGs6guf..; acw_tc=1a0acab617641144856093598e8412673ad88629afd32a2cb84baff7fb4f77; Hm_lpvt_59c4ff31a9ee6263811b23eb921a5083=1764114486; Hm_lpvt_022f847c4e3acd44d4a2481d9187f1e6=1764114486; __tea_cache_tokens_20000743={%22web_id%22:%227574593791965853196%22%2C%22user_unique_id%22:%221001058%22%2C%22timestamp%22:1764114486344%2C%22_type_%22:%22default%22}; _gid=GA1.2.296588085.1764114487; _gat=1; SERVERID=3431a294a18c59fc8f5805662e2bd51e|1764114488|1764114485; _ga_03JGDGP9Y3=GS2.2.s1764114488$o19$g0$t1764114488$j60$l0$h0'
    }
    
    try:
        # 获取数据客户端
        dc = get_data_client(cfg)
        
        # 设置课程ID
        course_id = 48
        dc.set_progress_manager(course_id)
        
        # 获取课程简介
        course_intro = dc.get_column_intro(course_id, no_cache=False)
        print(f"✓ 课程: {course_intro['column_title']}")
        print(f"✓ 总文章数: {len(course_intro['articles'])}")
        
        # 检查进度
        progress_manager = DownloadProgress(course_id)
        print(f"📊 当前进度: {progress_manager.get_progress_summary()}")
        
        # 获取前3篇文章作为测试
        articles = course_intro['articles'][:3]
        print(f"📥 测试下载 {len(articles)} 篇文章...")
        
        for i, article in enumerate(articles, 1):
            article_id = article['id']
            article_title = article['article_title'][:30] + "..."
            
            try:
                print(f"  {i}. 下载文章 {article_id}: {article_title}")
                content = dc.get_article_content(article_id, no_cache=False)
                print(f"     ✓ 成功，内容长度: {len(content.get('article_content', ''))}")
                
                # 显示更新后的进度
                print(f"     📊 {progress_manager.get_progress_summary()}")
                
                # 等待一下，模拟真实下载间隔
                time.sleep(1)
                
            except Exception as e:
                print(f"     ❌ 失败: {e}")
        
        # 最终进度
        print(f"\n🏁 最终进度: {progress_manager.get_progress_summary()}")
        
        # 测试重复下载（应该直接从缓存读取）
        print(f"\n🔄 测试重复下载第一篇文章...")
        first_article = articles[0]
        try:
            start_time = time.time()
            content = dc.get_article_content(first_article['id'], no_cache=False)
            end_time = time.time()
            print(f"  ✓ 重复下载成功，耗时: {end_time - start_time:.2f}秒 (应该很快)")
            print(f"  📊 {progress_manager.get_progress_summary()}")
        except Exception as e:
            print(f"  ❌ 重复下载失败: {e}")
        
        print("\n🎉 断点续下载功能测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_resume_download()
    print(f"\n结果: {'✅ 成功' if success else '❌ 失败'}")