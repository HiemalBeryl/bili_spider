import asyncio
import sys
from enum import Enum
from typing import Union

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

from entity.spiderEntity import SpiderParam
from spider.startSpider import start_spider



app = FastAPI()
spider_list: list[dict] = []


# TODO(973650812@qq.com):设计爬虫服务的api接口
#   1. 爬虫有三种类型，爬视频信息、爬评论、爬子评论，设想的功能是有一个后台页面可以添加爬虫，添加后的爬虫展示在任务列表中，
#      可以开启/关闭/编辑/删除。
#   2. 接口设计为查询爬虫列表、增加爬虫、编辑爬虫、改变爬虫工作状态、删除爬虫（作为管理员用户）
#   3. 普通用户无权查看爬虫信息，只能够通过spring那边添加一个视频，接着这个视频被加入数据库的任务表中，由爬虫自动爬取。
#   4. 爬虫任务设计（想到了就写）：名称，类型，是否循环，间隔时间(前端做成横向滑块那种)


# 查询爬虫列表
@app.get("/spider/list")
async def list_spyder():
    global spider_list
    # 获取当前事件循环中的所有任务
    tasks = asyncio.all_tasks()
    result: list[dict] = []
    # 获取正在工作中的爬虫，直接加入结果
    for task in tasks:
        if task.get_name().startswith("T+"):
            name = task.get_name().strip("T+")
            for s in spider_list:
                if s.get("spider").name == name:
                    result.append(s)
    # 获取已经停止工作的爬虫
    for s in spider_list:
        if s not in result:
            s.get("spider").is_working = False
            result.append(s)
    spider_list = result
    return_result = []
    for r in result:
        return_result.append(r.get("spider"))
    # print(spider_list)
    return {"tasks": return_result}


# 新增爬虫任务
@app.post("/spider/add")
async def add_spyder(spider_param: SpiderParam):
    # 判断名称、种类是否唯一
    for s in spider_list:
        if s.get("spider").name == spider_param.name or s.get("spider").type == spider_param.type:
            return {"result": "spider already exists"}
    spider_param.is_working = False
    # 新建异步运行协程任务
    task = asyncio.create_task(start_spider(spider_param))
    task.set_name(f"T+{spider_param.name}")
    spider_param.is_working = True
    # 添加到全局列表中
    spider_list.append({"spider": spider_param, "task": task})
    return {"tasks": task.get_name().strip("T+")}


# 编辑爬虫
@app.put("/spider/edit")
async def edit_spyder(spider: SpiderParam):
    # 根据名称判断爬虫是否存在
    for s in spider_list:
        if s.get("spider").name == spider.name:
            # 修改原爬虫的名称、是否循环、循环间隔
            s.get("spider").name = spider.name
            s.get("spider").interval = spider.interval
            s.get("spider").is_loop = spider.is_loop
            # 停止旧任务，如果没找到旧任务，说明已经出现异常终止
            tasks = asyncio.all_tasks()
            for task in tasks:
                if task.get_name().startswith("T+"):
                    name = task.get_name().strip("T+")
                    if s.get("spider").name == name:
                        task.cancel()
            # 开启新任务
            s.get("spider").is_working = False
            new_task = asyncio.create_task(start_spider(s.get("spider")))
            new_task.set_name(f"T+{s.get('spider').name}")
            s.get("spider").is_working = True
            return {"tasks": s.get("spider")}
    return {"result": "spider not exists, please create a spider first."}


# 开启/关闭爬虫
@app.put("/spider/alert")
async def alert_spyder(spider_name: str, option: bool):
    # 根据名称判断爬虫是否存在
    for s in spider_list:
        if s.get("spider").name == spider_name:
            # 得到爬虫原状态，如果与修改状态相同则不做改变，不同则开启任务或终止任务
            is_working = s.get("spider").is_working
            if is_working == option:
                return {"result": "Status is unnecessary to change."}
            # 两种可能性，关闭改开启、开启改关闭
            if option:
                # 停止旧任务，如果没找到旧任务，说明已经出现异常终止
                tasks = asyncio.all_tasks()
                for task in tasks:
                    if task.get_name().startswith("T+"):
                        name = task.get_name().strip("T+")
                        if s.get("spider").name == name:
                            task.cancel()
                # 开启新任务
                s.get("spider").is_working = False
                new_task = asyncio.create_task(start_spider(s.get("spider")))
                new_task.set_name(f"T+{s.get('spider').name}")
                s.get("spider").is_working = True
                return {"tasks": s.get("spider")}
            else:
                # 停止旧任务，如果没找到旧任务，说明已经出现异常终止
                tasks = asyncio.all_tasks()
                for task in tasks:
                    if task.get_name().startswith("T+"):
                        name = task.get_name().strip("T+")
                        if s.get("spider").name == name:
                            task.cancel()
                s.get("spider").is_working = False
                return {"tasks": s.get("spider")}
    return {"result": "spider not exists, please create a spider first."}


# 删除爬虫
@app.delete("/spider/delete")
async def delete_spyder(spider_name: str):
    to_delete_spider = None
    # 判断爬虫是否存在，存在则先终止任务再删除；不存在直接返回信息
    for s in spider_list:
        if s.get("spider").name == spider_name:
            # 爬虫存在于任务列表中，判断协程是否还在执行，强行终止
            tasks = asyncio.all_tasks()
            for task in tasks:
                if task.get_name().startswith("T+"):
                    name = task.get_name().strip("T+")
                    if s.get("spider").name == name:
                        task.cancel()
            s.get("spider").is_working = False
            # 记录即将删除的爬虫
            to_delete_spider = s
    if to_delete_spider:
        spider_list.remove(to_delete_spider)
        return {"tasks": to_delete_spider.get("spider")}
    return {"result": "spider not exists, please create a spider first."}