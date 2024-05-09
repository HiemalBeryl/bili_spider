from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By

'''
# selenium4.10以上版本执行后会自动关闭浏览器，如想保持打开状态需要进行设置
op = webdriver.EdgeOptions()
op.add_experimental_option("detach", True)
driver = webdriver.Edge(op)
driver.get(url="https://www.baidu.com")
driver.find_element(by=By.ID, value="kw").send_keys('python')
driver.find_element(by=By.ID, value="su").click()
'''


# 1. 首先对于爬虫主程序来说，应该存在一个任务列表，爬虫按照优先级依次从上到下执行列表中的任务
#   1.1 列表中全部为视频av/bv号，每个任务包括上次爬取时间，优先级这两个属性
#   1.2 爬虫每隔一段时间（暂定为30min）遍历列表，找到应该执行的任务，执行爬取操作
#      1.2.1 爬取视频播放量、点赞、投币、收藏、分享数据并入库
#      1.2.2 爬取视频评论，评论用户名、评论用户UID、评论内容、评论时间、点赞量、子评论数、父评论（如果自己为父评论则为空，自己为子评论则记录评论回复的评论）
#   1.3 管理后台里应该维护这个任务列表，但不是通过直接指定av/bv号的方式，目前想到有两种方式
#      1.3.1 UP主列表，这个表最开始由系统管理员手动添加，后续也应该手动维护，是最近几年的百大UP主，程序把UP主的所有视频自动添加到任务列表中
#      1.3.2 热门视频列表，由程序自动获取（每2小时获取一次），地址为：https://www.bilibili.com/v/popular/rank/all
#
# 2. 好像没了


def create_driver(url: str = "https://www.bilibili.com"):
    op = webdriver.EdgeOptions()
    op.add_experimental_option("detach", True)
    driver = webdriver.Edge(op)
    driver.get(url="https://www.bilibili.com")
    cookies = [{'name': 'buvid3', 'value': 'F0421EF5-2FDE-7D65-D650-2C9400BF8CC316452infoc', 'path': '/',
      'domain': 'www.bilibili.com', 'secure': False, 'httpOnly': False},
     {'name': 'b_nut', 'value': '1698222616', 'path': '/', 'domain': 'www.bilibili.com', 'secure': False,
      'httpOnly': False},
     {'name': 'CURRENT_FNVAL', 'value': '4048', 'path': '/', 'domain': 'www.bilibili.com', 'secure': False,
      'httpOnly': False},
     {'name': 'b_lsid', 'value': 'CA10B7E107_18B65F4B84A', 'path': '/', 'domain': 'www.bilibili.com', 'secure': False,
      'httpOnly': False}, {'name': '_uuid', 'value': '104CEB109D-3241-7B107-109F2-2BF5D5A59C5918709infoc', 'path': '/',
                           'domain': 'www.bilibili.com', 'secure': False, 'httpOnly': False},
     {'name': 'buvid_fp', 'value': '1802e0a5af37a17b2a1586943b24eaf2', 'path': '/', 'domain': 'www.bilibili.com',
      'secure': False, 'httpOnly': False},
     {'name': 'buvid4', 'value': '8CCE389D-A79A-1D2F-C371-B16B0E65F46218188-023102516-vHi6lkY+gC/JcV1zC0w1Ag%3D%3D',
      'path': '/', 'domain': 'www.bilibili.com', 'secure': False, 'httpOnly': False},
     {'name': 'rpdid', 'value': "|(k|YulRu~Ym0J'uYm)kkkYu)", 'path': '/', 'domain': 'www.bilibili.com', 'secure': False,
      'httpOnly': False}, {'name': 'bili_ticket',
                           'value': 'eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTg0ODE4MjEsImlhdCI6MTY5ODIyMjU2MSwicGx0IjotMX0.xt6g0MhUeqo_xbmLATkpUxDHnTQDuptyCnlyKBz9CnA',
                           'path': '/', 'domain': 'www.bilibili.com', 'secure': False, 'httpOnly': False},
     {'name': 'bili_ticket_expires', 'value': '1698481761', 'path': '/', 'domain': 'www.bilibili.com', 'secure': False,
      'httpOnly': False}, {'name': 'SESSDATA',
                           'value': 'af581ed9%2C1713774826%2C1bd9b%2Aa1CjBgA_PT4DQA_7gDz6W9Gd2wN6aPZM9Br5TvRpoq_-zhhFHsV4QzPibzQl9Aj9-MD1wSVlNnTWZhM0pRU0p0SnNMY1IzQkRnT1VhQVQwRW1Mb3pQeGg2YTZBU1VsTjU1RjBoRmoyQlpKUGZ1OEt6T3R4MzBDeVNVZ0x4czcwTmpJbV8wQ3FXN253IIEC',
                           'path': '/', 'domain': 'www.bilibili.com', 'secure': False, 'httpOnly': False},
     {'name': 'bili_jct', 'value': '97f7b5a187b27b160efcd69c7d14f2e7', 'path': '/', 'domain': 'www.bilibili.com',
      'secure': False, 'httpOnly': False},
     {'name': 'DedeUserID', 'value': '1829480924', 'path': '/', 'domain': 'www.bilibili.com', 'secure': False,
      'httpOnly': False},
     {'name': 'DedeUserID__ckMd5', 'value': 'f3a5bbc575b2521f', 'path': '/', 'domain': 'www.bilibili.com',
      'secure': False, 'httpOnly': False},
     {'name': 'sid', 'value': 'qcdzbunn', 'path': '/', 'domain': 'www.bilibili.com', 'secure': False,
      'httpOnly': False},
     {'name': 'PVID', 'value': '1', 'path': '/', 'domain': 'www.bilibili.com', 'secure': False, 'httpOnly': False}]
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.get(url=url)
    return driver


def get_video_base_info(bv: str = None, av: Optional[int] = None):
    driver = create_driver(url=f"https://www.bilibili.com/{bv}")
    scripts = driver.find_element(By.TAG_NAME, "script")
    for s in scripts:
        print(s)


def get_comment():
    pass


get_video_base_info(bv="BV17x411w7KC")
