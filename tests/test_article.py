#!/usr/bin/env python3
# coding=utf8

import sys
sys.path.insert(0, '.')

from geektime_dl.gt_apis import GkApiClient, GkApiError

def test_article_access():
    try:
        token = "_ga=GA1.2.496332097.1736651838; LF_ID=90be707-16cc400-d06642d-ff4c34a; mantis5539=2e01d025245c4af9bad2c9d261fa29ef@5539; MEIQIA_TRACK_ID=2so3lBHtT50ImdQM7xHUWtlxEiG; MEIQIA_VISIT_ID=2so3lBGCroP35N5q3RpkUJB5Ga1; _tea_utm_cache_20000743={%22utm_term%22:%22pc_interstitial_1984%22}; gksskpitn=5b2203b0-5a78-4098-92d6-7451b3328611; HMACCOUNT=0B5DE57CDE4EAFDC; _ga_MTX5SQH9CV=GS2.2.s1760777262$o4$g1$t1760777302$j20$l0$h0; Hm_lvt_022f847c4e3acd44d4a2481d9187f1e6=1763597546; Hm_lvt_59c4ff31a9ee6263811b23eb921a5083=1763597546; GCID=6db28b5-0abec68-8e1b6e4-4a70c67; _ga_JW698SFNND=GS2.2.s1763597565$o9$g1$t1763597569$j56$l0$h0; gk_process_ev={%22count%22:2%2C%22utime%22:1763597570276%2C%22referrer%22:%22https://time.geekbang.org/column/intro/101089301%22%2C%22target%22:%22page_geektime_login%22%2C%22referrerTarget%22:%22page_geektime_login%22}; GRID=6db28b5-0abec68-8e1b6e4-4a70c67; GCESS=BgoEAAAAAAgBAwkBAQYEc4VnvwUEAAAAAAcEJYf76Q0BAQEIYkYPAAAAAAAEBACNJwACBAxdHmkMAQELAgYAAwQMXR5p; tfstk=gAwI3pbyfzeNkxNxOYSwGn_zBhMSFGWVN3i8mupe2vHKF4a8SBlrzuLWFrzhqMqzL5a7Vr0KUvyFF7M3QWJr8wD72rk5uZWV3kqnnYQVuT79A5kxcepJz4K9BYoWnoubXkqnEh2iD76YxTG_1vg-ezHt6mmme0dLyFEtS0mJJ0pdfl3iWDpKyBK960oxyeU-eGZtS0H-yzhRfl3i2Y3JPx9IbMggAiVwhupDERqK5Lp8pTcnl63ijDysVXgxxV98ARiIOqELLypDq0NYhX4A7BuLG7aj0yW9drZ8m7h_F9Tm7jmb5jPClpMYKuFmJ5bMycNTmzmYJNJIkSqtpmV1lpDUcVMUdxBDJ4Pac8i7EaX_luE0wfw5dE0Zi0IrBKujPaOWfjvSfqS1fQAu_woDkon_FchKjc7PfGO4qXnif5I1fQAo9cmZWGs6guf..; _gid=GA1.2.1509807370.1763988496; acw_tc=1a0acab617639919606421152e84218223d767e1d7ff2f146794efadaff88a; _gat=1; Hm_lpvt_59c4ff31a9ee6263811b23eb921a5083=1763993591; Hm_lpvt_022f847c4e3acd44d4a2481d9187f1e6=1763993591; __tea_cache_tokens_20000743={%22web_id%22:%227574593791965853196%22%2C%22user_unique_id%22:%221001058%22%2C%22timestamp%22:1763993590915%2C%22_type_%22:%22default%22}; _ga_03JGDGP9Y3=GS2.2.s1763991960$o18$g1$t1763993591$j60$l0$h0; SERVERID=1fa1f330efedec1559b3abbcb6e30f50|1763993592|1763988496"
        
        client = GkApiClient(auth_token=token, auth_type='token')
        
        # 获取课程简介
        print("获取课程简介...")
        course_intro = client.get_course_intro(48)
        print(f"课程标题: {course_intro.get('column_title', '未知')}")
        
        # 获取文章列表
        print("获取文章列表...")
        articles = client.get_post_list_of(48)
        print(f"文章数量: {len(articles)}")
        
        # 测试获取前3篇文章的内容
        for i, article in enumerate(articles[:3]):
            article_id = article['id']
            article_title = article['article_title'][:20] + "..."
            print(f"\n测试第{i+1}篇文章: {article_title} (ID: {article_id})")
            
            try:
                content = client.get_post_content(article_id)
                print(f"  ✓ 获取成功，内容长度: {len(content.get('article_content', ''))}")
            except GkApiError as e:
                print(f"  ✗ 获取失败: {e}")
                if "非法图形验证码" in str(e):
                    print("  ⚠️  发现验证码错误！")
                    return False
            except Exception as e:
                print(f"  ✗ 其他错误: {e}")
                import traceback
                traceback.print_exc()
        
    except GkApiError as e:
        print(f'API错误: {e}')
        if "非法图形验证码" in str(e):
            print("⚠️  在获取课程信息时出现验证码错误！")
        return False
    except Exception as e:
        print(f'测试失败: {e}')
        return False
    
    return True

if __name__ == '__main__':
    success = test_article_access()
    if success:
        print("\n✓ 所有测试通过")
    else:
        print("\n✗ 测试失败")
    sys.exit(0 if success else 1)