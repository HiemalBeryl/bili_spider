import asyncio
import math
import re
import time

import httpx
import pymysql
from json import JSONDecodeError
from typing import Optional
from datetime import datetime
from httpx import Cookies
from pymysql import err, OperationalError
from .bv2avSwitcher import Video
from entity.spiderEntity import SpiderParam

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 '
                  'Safari/537.36',
    'origin': 'https://www.bilibili.com/',
    'cookie': '',
    'Connection': 'close',
    'referer': 'https://www.bilibili.com/'
}
basic_info = "https://api.bilibili.com/x/web-interface/view"
reply_by_page = "https://api.bilibili.com/x/v2/reply"
sub_reply = "https://api.bilibili.com/x/v2/reply/reply"
reply_lazy_loading = "https://api.bilibili.com/x/v2/reply/main"
ranking = "https://api.bilibili.com/x/web-interface/ranking/v2"
ranking_params = {
    '全站': {'rid': 0, 'type': 'all'},
    '国创相关': {'rid': 168, 'type': 'all'},
    '动画': {'rid': 1, 'type': 'all'},
    '音乐': {'rid': 3, 'type': 'all'},
    '舞蹈': {'rid': 129, 'type': 'all'},
    '游戏': {'rid': 4, 'type': 'all'},
    '知识': {'rid': 36, 'type': 'all'},
    '科技': {'rid': 188, 'type': 'all'},
    '运动': {'rid': 234, 'type': 'all'},
    '汽车': {'rid': 223, 'type': 'all'},
    '生活': {'rid': 160, 'type': 'all'},
    '美食': {'rid': 211, 'type': 'all'},
    '动物圈': {'rid': 217, 'type': 'all'},
    '鬼畜': {'rid': 119, 'type': 'all'},
    '时尚': {'rid': 155, 'type': 'all'},
    '娱乐': {'rid': 5, 'type': 'all'},
    '影视': {'rid': 181, 'type': 'all'},
    '原创': {'rid': 0, 'type': 'origin'},
    '新人': {'rid': 0, 'type': 'rookie'}
}
db_host = 'nas.hiemalberyl.cn'
db_user = 'xtjcyyh'
db_password = 'xtjcyyh2023'
db_port = 3306
db_db = 'xtjcyyh'


def init_cookies():
    c = Cookies()
    with open("./spider/cookies.txt", "r", encoding="utf-8") as f:
        for line in f:
            cookie_split = line.split('=')
            c.set(name=cookie_split[0], value=cookie_split[1].strip(','), domain="https://www.bilibili.com")
    return c


# 网址解析器
async def fetch_data(url, method='GET', params=None, cookies=None):
    async with httpx.AsyncClient() as client:
        try:
            if method == 'GET':
                response = await client.get(url, params=params, headers=headers, cookies=cookies, timeout=10)
            elif method == 'POST':
                response = await client.post(url, data=params, headers=headers, cookies=cookies, timeout=10)
            else:
                raise ValueError("Unsupported HTTP method")

            response.raise_for_status()  # 检查响应状态码
            data = response.json()  # 尝试解析 JSON 数据

            return data
        except httpx.RequestError as e:
            print(f"Request error: {e}")
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e}")
        except JSONDecodeError as e:
            print(f"JSON decode error: {e}")


# 获取视频播放量等基础信息
async def get_video_info(av: Optional[str | int] = None, bv: Optional[str] = None):
    # 构造请求参数
    video = Video(av, bv)
    cookies = init_cookies()
    params = {
        'bvid': video.bv
    }

    # TODO:研究这里应该如何处理最优雅，异步请求如果出现异常返回空值，外部是接着抛异常还是用if判断！
    # 开始异步请求
    j = await fetch_data(basic_info, 'GET', params, cookies)
    if j is not None and 'data' in j:
        j = j['data']
    else:
        return None

    # 构造返回结果
    video_data = {
        'bv': j['bvid'],
        'av': j['aid'],
        'videos': j['videos'],
        'tag_id': j['tid'],
        'tag_name': j['tname'],
        'pic': j['pic'],
        'title': j['title'],
        'des': j['desc'],
        'upload_time': datetime.fromtimestamp(j['ctime']),
        'view_times': j['stat']['view'],
        'danmaku': j['stat']['danmaku'],
        'reply': j['stat']['reply'],
        'like_times': j['stat']['like'],
        'coin': j['stat']['coin'],
        'favorite': j['stat']['favorite'],
        'share_times': j['stat']['share']
    }
    return video_data


# 获取评论
async def get_video_reply(av: Optional[str | int] = None, bv: Optional[str] = None):
    # 构造请求参数
    video = Video(av, bv)
    # pn页码，type资源类型（视频、动态），oid资源id（视频为av号），sort排序方式（0按时间2按热度）
    params = {
        'pn': 1,
        'type': 1,
        'oid': video.av,
        'sort': 0
    }

    # TODO:研究这里应该如何处理最优雅，异步请求如果出现异常返回空值，外部是接着抛异常还是用if判断！
    # 开始异步请求
    j = await fetch_data(reply_by_page, 'GET', params)
    if j is not None:
        j = j['data']
        count = j['page']['count']
        acount = j['page']['acount']
    else:
        return None
    # TODO:这里计算评论总页数可能有bug，反正是目前获取不到所有评论
    for page in range(1, math.ceil(count / 20) + 50):
        # 先处理上次请求获取的replies列表
        if isinstance(j['replies'], list):
            insert_data = []
            for item in j['replies']:
                reply_data = {
                    'rpid': item.get('rpid'),
                    'oid': item.get('oid'),
                    'mid': item.get('mid'),
                    'type': item.get('type'),
                    'root': item.get('root'),
                    'parent': item.get('parent'),
                    'dialog': item.get('dialog'),
                    'count': item.get('count'),
                    'rcount': item.get('rcount'),
                    'state': item.get('state'),
                    'fansgrade': item.get('fansgrade'),
                    'attr': item.get('attr'),
                    'upload_time': datetime.fromtimestamp(item.get('ctime')),
                    'like_times': item.get('like'),
                    'username': item.get('member')['uname'],
                    'sex': item.get('member')['sex'],
                    'sign': item.get('member')['sign'],
                    'avatar': item.get('member')['avatar'],
                    'user_level': item.get('member')['level_info']['current_level'],
                    'is_official': item.get('member')['official_verify']['type'],
                    'official_desc': item.get('member')['official_verify']['desc'],
                    'is_big_vip': item.get('member')['vip']['vipStatus'],
                    'big_vip_endtime': datetime.fromtimestamp(int(item.get('member')['vip']['vipDueDate']) / 1000),
                    'message': item.get('content')['message'],
                    'members': str(item.get('content')['members']) if item.get('content') and 'members' in item.get(
                        'content') else ' ',
                    'emote': str(item.get('content')['emote']) if item.get('content') and 'emote' in item.get(
                        'content') else ' ',
                    'jump_url': str(item.get('content')['jump_url']) if item.get('content') and 'jump_url' in item.get(
                        'content') else ' ',
                    'have_sub_replies': 0,
                    'location': None
                }
                if 'sub_reply_title_text' in item.get('reply_control'):
                    pattern = r'\d+'  # 匹配一个或多个数字
                    reply_data['have_sub_replies'] = re.findall(pattern,
                                                                item.get('reply_control')['sub_reply_title_text'])
                if 'location' in item.get('reply_control'):
                    reply_data['location'] = item.get('reply_control')['location']
                insert_data.append(reply_data)
            # print(insert_data)
            save_batch_into_db(insert_data, 'reply_info')
        # 再发送一次请求
        await asyncio.sleep(5)
        params['pn'] = page
        j = await fetch_data(reply_by_page, 'GET', params)
        if j is not None and 'data' in j:
            j = j['data']
        else:
            break


# 获取子评论
async def get_sub_reply(start: Optional[int] = 1):
    # 获取任务列表
    task_page = start
    tasks = get_sub_reply_task_from_db(task_page)
    print(f"开始执行第{task_page}页任务，任务元组：{tasks}")
    while len(tasks) != 0:
        # 查询评论并格式化数据

        for task in tasks:
            # 构造请求参数
            cookies = init_cookies()
            params = {
                'oid': task[0],
                'type': task[1],
                'root': task[2],
                'ps': 20,
                'pn': 1
            }

            # 开始异步请求
            j = await fetch_data(sub_reply, 'GET', params, cookies)
            if j is not None:
                j = j['data']
                size = j['page']['size']
                count = j['page']['count']
            else:
                continue
            for page in range(1, math.ceil(count / size) + 5):
                # 先处理上次请求获取的replies列表
                if isinstance(j['replies'], list):
                    insert_data = []
                    for item in j['replies']:
                        reply_data = {
                            'rpid': item.get('rpid'),
                            'oid': item.get('oid'),
                            'mid': item.get('mid'),
                            'type': item.get('type'),
                            'root': item.get('root'),
                            'parent': item.get('parent'),
                            'dialog': item.get('dialog'),
                            'count': item.get('count'),
                            'rcount': item.get('rcount'),
                            'state': item.get('state'),
                            'fansgrade': item.get('fansgrade'),
                            'attr': item.get('attr'),
                            'upload_time': datetime.fromtimestamp(item.get('ctime')),
                            'like_times': item.get('like'),
                            'username': item.get('member')['uname'],
                            'sex': item.get('member')['sex'],
                            'sign': item.get('member')['sign'],
                            'avatar': item.get('member')['avatar'],
                            'user_level': item.get('member')['level_info']['current_level'],
                            'is_official': item.get('member')['official_verify']['type'],
                            'official_desc': item.get('member')['official_verify']['desc'],
                            'is_big_vip': item.get('member')['vip']['vipStatus'],
                            'big_vip_endtime': datetime.fromtimestamp(
                                int(item.get('member')['vip']['vipDueDate']) / 1000),
                            'message': item.get('content')['message'],
                            'members': str(item.get('content')['members']) if item.get(
                                'content') and 'members' in item.get(
                                'content') else ' ',
                            'emote': str(item.get('content')['emote']) if item.get('content') and 'emote' in item.get(
                                'content') else ' ',
                            'jump_url': str(item.get('content')['jump_url']) if item.get(
                                'content') and 'jump_url' in item.get(
                                'content') else ' ',
                            'have_sub_replies': 0,
                            'location': None
                        }
                        if 'sub_reply_title_text' in item.get('reply_control'):
                            pattern = r'\d+'  # 匹配一个或多个数字
                            reply_data['have_sub_replies'] = re.findall(pattern,
                                                                        item.get('reply_control')[
                                                                            'sub_reply_title_text'])
                        if 'location' in item.get('reply_control'):
                            reply_data['location'] = item.get('reply_control')['location']
                        insert_data.append(reply_data)
                    # print(insert_data)
                    save_batch_into_db(insert_data, 'reply_info')
                # 再发送一次请求
                await asyncio.sleep(2)
                params['pn'] = page
                j = await fetch_data(sub_reply, 'GET', params)
                if j is not None and 'data' in j:
                    j = j['data']
                else:
                    break
        task_page += 1
        tasks = get_sub_reply_task_from_db(task_page)
        print(f"开始执行第{task_page}页任务，任务元组：{tasks}")


# 从排行榜获取当前热门视频
async def get_ranking():
    for v in ranking_params.values():
        j = await fetch_data(ranking, 'GET', v, init_cookies())
        if j is not None and 'data' in j:
            j = j['data']['list']
        insert_data = []
        for item in j:
            task_data0 = {
                'bv': item['bvid'],
                'av': item['aid'],
                'mid': item['owner']['mid'],
                'up_name': item['owner']['name'],
                'reply_next_page': 0,
                'owner': 0,
                'type': 0
            }
            task_data1 = {
                'bv': item['bvid'],
                'av': item['aid'],
                'mid': item['owner']['mid'],
                'up_name': item['owner']['name'],
                'reply_next_page': 0,
                'owner': 0,
                'type': 1
            }
            task_data2 = {
                'bv': item['bvid'],
                'av': item['aid'],
                'mid': item['owner']['mid'],
                'up_name': item['owner']['name'],
                'reply_next_page': 0,
                'owner': 0,
                'type': 2
            }
            insert_data.append(task_data0)
            insert_data.append(task_data1)
            insert_data.append(task_data2)
        # print(insert_data)
        save_batch_into_db(insert_data, 'task_list')


def save_into_db(data: dict = None, table_name: str = None):
    try:
        connect = pymysql.connect(host=db_host, user=db_user, passwd=db_password, port=db_port, db=db_db)
    except:
        print("连接数据库失败！")
        return 1

    cursor = connect.cursor()
    cols = ", ".join('`{}`'.format(k) for k in data.keys())
    # print(cols)

    val_cols = ', '.join('%({})s'.format(k) for k in data.keys())
    # print(val_cols)

    sql = "insert into %s(%s) values(%s)"
    res_sql = sql % (table_name, cols, val_cols)
    # print(res_sql)

    try:
        cursor.execute(res_sql, data)
        connect.commit()
    except err.IntegrityError:
        print('数据已存在，保存失败')
    except Exception as e:
        connect.rollback()
        print(f'发生未知错误！{e}')
    connect.close()


def save_batch_into_db(data_list: list = None, table_name: str = None):
    if not data_list:
        print("数据为空，无需插入。")
        return

    try:
        connection = pymysql.connect(host=db_host, user=db_user, passwd=db_password, port=db_port, db=db_db)
    except Exception as e:
        print(f"连接数据库失败: {e}")
        return 1

    cursor = connection.cursor()
    cols = ", ".join('`{}`'.format(k) for k in data_list[0].keys())

    val_cols = ', '.join('%s' for _ in data_list[0].keys())

    sql = f"INSERT INTO {table_name} ({cols}) VALUES ({val_cols}) ON DUPLICATE KEY UPDATE "
    update_cols = ', '.join([f"{col}=VALUES({col})" for col in data_list[0].keys()])
    sql += update_cols

    try:
        # Prepare a list of tuples for executemany
        data = [tuple(item.values()) for item in data_list]

        cursor.executemany(sql, data)
        print(f"执行成功，即将提交事务，影响行数：{cursor.rowcount}")
        connection.commit()
    except Exception as e:
        connection.rollback()
        print(f'发生未知错误！{e}')
    finally:
        connection.close()


def get_sub_reply_task_from_db(page: int = 1, size: Optional[int] = 1000) -> tuple:
    try:
        connect = pymysql.connect(host=db_host, user=db_user, passwd=db_password, port=db_port, db=db_db)
        print("连接数据库成功！")
    except:
        print("连接数据库失败！")
        return 1

    try:
        cursor = connect.cursor()
        sql = f"SELECT oid, type, rpid FROM reply_info WHERE have_sub_replies != 0 LIMIT {size * (page - 1)},{size}"
        print(sql)
        cursor.execute(sql)
        response = cursor.fetchall()
        connect.close()
        return response
    except OperationalError:
        print("查询失败，可能是sql语法有误！")
        connect.close()
        return ()


# 从数据库中获取即将执行的任务
def get_task_from_db(page: int = 1, size: Optional[int] = 1000, task_type: int = 0):
    try:
        connect = pymysql.connect(host=db_host, user=db_user, passwd=db_password, port=db_port, db=db_db)
        print("连接数据库成功！")
    except:
        print("连接数据库失败！")
        return 1

    try:
        cursor = connect.cursor()
        sql = f"SELECT bv, av FROM task_list WHERE type = {task_type} AND is_working = 1 AND TIMESTAMPDIFF(MINUTE, last_execute_time, CURTIME()) LIMIT {size * (page - 1)},{size}"
        print(sql)
        cursor.execute(sql)
        response = cursor.fetchall()
        connect.close()
        return response
    except OperationalError:
        print("查询失败，可能是sql语法有误！")
        connect.close()
        return ()


# 任务1，爬取其播放量信息
async def main1():
    page = 1
    size = 500
    results = get_task_from_db(page, size, 0)
    while len(results) != 0:
        videos = []
        for r in results:
            videos.append(Video(r[1], r[0]))
        page += 1
        print(page)
        for v in videos:
            info = await get_video_info(v.av)
            if info is not None:
                save_into_db(info, 'video_info')
        results = get_task_from_db(page, size, 0)


# 任务2 爬取视频评论
async def main2():
    page = 1
    size = 30
    results = get_task_from_db(page, size, 1)
    while len(results) != 0:
        videos = []
        for r in results:
            videos.append(Video(r[1], r[0]))
        page += 1
        print(page)
        for v in videos:
            await get_video_reply(av=v.av)
        results = get_task_from_db(page, size, 1)


# 任务3 爬取视频子评论
async def main3():
    await get_sub_reply()


# 启动爬虫
async def start_spider(spider: SpiderParam):
    loop = True
    while loop:
        if spider.type == 0:
            await main1()
        elif spider.type == 1:
            await main2()
        elif spider.type == 2:
            await main3()
        elif spider.type == 3:
            await get_ranking()
        else:
            raise ValueError("爬虫类型错误！")
        loop = spider.is_loop
        print(f"循环状态：{loop},即将开始sleep")
        await asyncio.sleep(spider.interval)
        print(f"sleep结束")
