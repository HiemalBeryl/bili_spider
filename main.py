import asyncio
import math
import re
import httpx
import pymysql
from json import JSONDecodeError
from typing import Optional
from datetime import datetime
from httpx import Cookies
from pymysql import err, OperationalError


from bv2av_switcher import Video

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
db_host = 'nas.hiemalberyl.cn'
db_user = 'xtjcyyh'
db_password = 'xtjcyyh2023'
db_port = 3306
db_db = 'xtjcyyh'


def init_cookies():
    c = Cookies()
    with open("cookies.txt", "r", encoding="utf-8") as f:
        for line in f:
            cookie_split = line.split('=')
            c.set(name=cookie_split[0], value=cookie_split[1].strip(','), domain="https://www.bilibili.com")
    return c


# 网址解析器
async def fetch_data(url, method='GET', params=None, cookies=None):
    async with httpx.AsyncClient() as client:
        try:
            if method == 'GET':
                response = await client.get(url, params=params, headers=headers, cookies=cookies)
            elif method == 'POST':
                response = await client.post(url, data=params, headers=headers, cookies=cookies)
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
def get_video_info(av: Optional[str | int] = None, bv: Optional[str] = None):
    # 构造请求参数
    video = Video(av, bv)
    cookies = init_cookies()
    params = {
        'bvid': video.bv
    }

    # TODO:研究这里应该如何处理最优雅，异步请求如果出现异常返回空值，外部是接着抛异常还是用if判断！
    # 开始异步请求
    j = asyncio.run(fetch_data(basic_info, 'GET', params, cookies))
    if j is not None:
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
def get_video_reply(av: Optional[str | int] = None, bv: Optional[str] = None):
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
    j = asyncio.run(fetch_data(reply_by_page, 'GET', params))
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
                print(reply_data)
                save_into_db(reply_data, 'reply_info')
        # 再发送一次请求
        params['pn'] = page
        j = asyncio.run(fetch_data(reply_by_page, 'GET', params))
        if j is not None and 'data' in j:
            j = j['data']
        else:
            break


# 获取子评论
def get_sub_reply(start: Optional[int] = 1):
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
            j = asyncio.run(fetch_data(sub_reply, 'GET', params, cookies))
            if j is not None:
                j = j['data']
                size = j['page']['size']
                count = j['page']['count']
            else:
                continue
            for page in range(1, math.ceil(count / size) + 5):
                # 先处理上次请求获取的replies列表
                if isinstance(j['replies'], list):
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
                        print(reply_data)
                        save_into_db(reply_data, 'reply_info')
                # 再发送一次请求
                params['pn'] = page
                j = asyncio.run(fetch_data(sub_reply, 'GET', params))
                if j is not None and 'data' in j:
                    j = j['data']
                else:
                    break
        task_page += 1
        tasks = get_sub_reply_task_from_db(task_page)
        print(f"开始执行第{task_page}页任务，任务元组：{tasks}")


        # 保存到数据库


# TODO:保存到数据库，目前是串行不支持并发，一定要改！！！
def save_into_db(data: dict = None, table_name: str = None):
    try:
        connect = pymysql.connect(host=db_host, user=db_user, passwd=db_password, port=db_port, db=db_db)
        print("连接数据库成功！")
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
        print('数据插入成功！')
    except err.IntegrityError:
        print('数据已存在，保存失败')
    except:
        connect.rollback()
        print('发生未知错误！')
    connect.close()


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


# info = get_video_info(bv="BV1zv4y117zo")
# info2 = get_video_info(bv="BV1g84y1R7YH")
# info3 = get_video_info(bv="BV1Lw411w7Hc")
# info4 = get_video_info(bv="BV1x34y1M7LU")
# info5 = get_video_info(av=863041388)
# info6 = get_video_info(av=308030996)
# info7 = get_video_info(av=990547962)
# info8 = get_video_info(av=223004948)
# info9 = get_video_info(av=223004948)
# info10 = get_video_info(av=543790482)
# info11 = get_video_info(bv='BV1zv4y117zo')
info12 = get_video_info(bv='BV16s41167m3')
info13 = get_video_info(bv='BV1n54y1S79k')
info14 = get_video_info(bv='BV1At4y1q7UQ')
info15 = get_video_info(bv='BV1kJ411Q7rY')
info16 = get_video_info(bv='BV1MN4y177PB')
# save_into_db(info, 'video_info')
# save_into_db(info2, 'video_info')
# save_into_db(info3, 'video_info')
# save_into_db(info4, 'video_info')
# save_into_db(info5, 'video_info')
# save_into_db(info6, 'video_info')
# save_into_db(info7, 'video_info')
# save_into_db(info8, 'video_info')
# save_into_db(info9, 'video_info')
# save_into_db(info10, 'video_info')
# save_into_db(info11, 'video_info')
save_into_db(info12, 'video_info')
save_into_db(info13, 'video_info')
save_into_db(info14, 'video_info')
save_into_db(info15, 'video_info')
save_into_db(info16, 'video_info')
# get_video_reply(av=863041388)
# get_video_reply(av=308030996)
# get_video_reply(av=990547962)
# get_video_reply(av=223004948)
# get_video_reply(av=543790482)
# get_video_reply(av=565417552)

# get_video_reply(av=6108496)
# get_video_reply(av=838932570)
get_video_reply(av=627167023)
get_video_reply(av=77511727)
get_video_reply(av=898762590)
get_sub_reply()
# get_sub_reply(3)
