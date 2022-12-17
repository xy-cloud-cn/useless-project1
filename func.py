# -*- coding: utf-8 -*-
'''
@Author   : xy_cloud
@IDE      : PyCharm
@Project  : Python Project
@File     : func.py
@Time     : 2022/12/9 14:45
'''
import base64
import csv
import ctypes
import datetime
import inspect
import os.path
import random
import re
import threading
import time
from io import BytesIO
import json
import cv2
import numpy
import requests
import textwrap
from PIL import Image, ImageSequence, ImageFont, ImageDraw

from receive import *
from send import *

groupid = [895105949]
player_list = {}
test_dict = {}
test_answer_dict = {}
data = []
admin = [1787670159]
can_exit = 0
can_update = 0

# 线程控制
def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


# 文件管理
def read_info(filename):
    print('./test/' + filename + '.info')
    if not os.path.exists('./test/' + filename + '.info'):
        return 'error name'
    with open('./test/' + filename + '.info', 'r', encoding='utf-8') as f:
        return f.read()


def read_test(filename):
    global test_dict
    print('./test/' + filename + '.csv')
    if not os.path.exists('./test/' + filename + '.csv'):
        return
    with open('./test/' + filename + '.csv', 'r', encoding='utf-8') as f:
        test_dict[filename] = list(csv.reader(f))
        print(test_dict)
        return


def write_log(log):
    with open('./log.log', 'a', encoding='utf-8') as f:
        f.write('[' + str(datetime.datetime.now()) + '] [info] ' + log + '\n')


def read_answer(filename):
    global test_answer_dict
    print('./test/' + filename + '_answer.csv')
    if not os.path.exists('./test/' + filename + '_answer.csv'):
        return
    with open('./test/' + filename + '_answer.csv', 'r', encoding='utf-8') as f:
        test_answer_dict[filename] = list(csv.reader(f))
        print(test_answer_dict)
        return


def read_data():
    with open('data.csv', 'r', encoding='utf-8') as f:
        data = list(csv.reader(f))
    return data


def update_data(dataz):
    with open("data.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for i in dataz:
            writer.writerow(i)
    global data
    data = read_data()


# 便利函数
def check(qq):
    global data
    for i in data:
        if str(qq) == str(i[0]):
            return
    data.append(
        [qq, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    update_data(data)
    data = read_data()

def search_data(data, qq):
    for i in range(len(data)):
        if qq == data[i][0]:
            return i
    return -1
# 功能实现
def answer(answer, qq):
    global test_dict, player_list
    print(test_dict[player_list[qq][0]][player_list[qq][1]][(ord(answer.upper()) - 65) * 2 + 2])
    player_list[qq][2] += float(test_dict[player_list[qq][0]][player_list[qq][1]][(ord(answer.upper()) - 65) * 2 + 2])
    player_list[qq][1] += 1
    if player_list[qq][1] >= len(test_dict[player_list[qq][0]]):
        test_end(qq)
    else:
        refresh_ask(qq)


def test_end(qq):
    global test_dict, player_list, test_answer_dict
    jg = ''
    jy = ''
    score = round(player_list[qq][2])

    for i in test_answer_dict[player_list[qq][0]]:
        if int(i[0]) <= score <= int(i[1]):
            jg = i[2]
            jy = i[3]
            break
    write_log(f'{qq}答完了{player_list[qq][0]}问卷,分数是:{score}\n判断结果:{jg}\n建议:{jy}')
    send_msg({'msg_type': 'private', 'number': qq,
              'msg': f'你答完啦~\n您的分数是:{score}\n判断结果:{jg}\n建议:{jy}'})
    del player_list[qq]


def refresh_ask(qq):
    global test_dict, player_list
    text = test_dict[player_list[qq][0]][player_list[qq][1]][0]
    for i in range(1, len(test_dict[player_list[qq][0]][player_list[qq][1]]), 2):
        text += '\n' + chr(65 + i // 2) + '.' + test_dict[player_list[qq][0]][player_list[qq][1]][i]
    send_msg({'msg_type': 'private', 'number': qq,
              'msg': text})





def main(rev):
    global groupid, player_list, data, admin, can_exit, can_update
    random.seed(time.time())
    # print(rev) #需要功能自己DIY
    if rev["message_type"] == "private":  # 私聊
        with open('admin.csv', 'r', encoding='utf-8') as f:
            admin = list(map(int, list(csv.reader(f))[0]))
        qq = rev['sender']['user_id']
        if qq in admin:
            if rev['message'] == 'help':
                send_msg({'msg_type': 'private', 'number': qq, 'msg': '私聊\n'
                                                                      'get\n'
                                                                      'hget\n'
                                                                      'delete [id]\n'
                                                                      '审核 [编号] [通过/不通过] [不通过原因]\n'
                                                                      '添加管理员 [qq](xy专属)\n'
                                                                      '移除管理员 [id](xy专属)\n'
                                                                      '管理员列表\n'
                                                                      'say 群号 内容\n'
                                                                      'vote 群号 qq 时间（分）\n'
                                                                      '群聊\n'
                                                                      '清除签到时间\n'
                                                                      '清除今日运势时间\n'})
            elif rev['message'] == 'get':

                with open('hitokoto_requsets.csv', 'r', encoding='utf-8') as f:
                    checklist = list(csv.reader(f))
                ju = ''
                for i in range(len(checklist)):
                    ju = ju + f'id.{i} 来自:{checklist[i][3]} 语句:{checklist[i][0]} 来源:{checklist[i][1]} 作者:{checklist[i][2]}\n'
                send_msg({'msg_type': 'private', 'number': qq, 'msg': ju})
            elif rev['message'] == '管理员列表':

                with open('admin.csv', 'r', encoding='utf-8') as f:
                    admin = list(csv.reader(f))[0]
                send_msg({'msg_type': 'private', 'number': qq, 'msg': str(admin)})
            elif rev['message'] == 'hget':

                with open('hitokoto.csv', 'r', encoding='utf-8') as f:
                    checklist = list(csv.reader(f))
                ju = ''
                for i in range(len(checklist)):
                    ju = ju + f'id.{i} 来自:{checklist[i][3]} 语句:{checklist[i][0]} 来源:{checklist[i][1]} 作者:{checklist[i][2]}\n'
                send_msg({'msg_type': 'private', 'number': qq, 'msg': ju})
            elif rev['message'].split(' ')[0] == '审核':

                info_input = rev['raw_message'].split(' ')
                reason = ''
                if len(info_input) >= 3:
                    sid = int(info_input[1])
                    result = info_input[2]
                else:
                    send_msg({'msg_type': 'private', 'number': qq, 'msg': f'请输入正确的格式！'})
                    return
                if result == '不通过':
                    if len(info_input) == 4:
                        reason = info_input[3]
                    else:
                        send_msg({'msg_type': 'private', 'number': qq, 'msg': f'请输入正确的格式！'})
                        return
                elif not result == '通过':
                    send_msg({'msg_type': 'private', 'number': qq, 'msg': f'请输入正确的格式！'})
                    return
                with open('hitokoto_requsets.csv', 'r', encoding='utf-8') as f:
                    checklist = list(csv.reader(f))
                reply = f'管理员已处理你的一言:{checklist[sid][0]} 结果:{result}'
                if result == '不通过':
                    reply += f' 原因:{reason} 请修改后再试！'
                else:
                    reply += f' 感谢支持！'
                    text = checklist[sid][0]
                    fro = checklist[sid][1]
                    write = checklist[sid][2]
                    with open('hitokoto.csv', 'a', encoding='utf-8') as f:
                        f.write(text + ',' + fro + ',' + write + ',' + checklist[sid][3] + '\n')
                send_msg({'msg_type': 'private', 'number': int(checklist[sid][3]),
                          'msg': reply})
                send_msg({'msg_type': 'private', 'number': qq, 'msg': f'审核成功！'})
                checklist.pop(sid)
                with open('hitokoto_requsets.csv', 'w', encoding='utf-8', newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(checklist)
            elif rev['message'].split(' ')[0] == 'delete':

                info_input = rev['raw_message'].split(' ')
                reason = ''
                if len(info_input) == 2:
                    sid = int(info_input[1])
                else:
                    send_msg({'msg_type': 'private', 'number': qq, 'msg': f'请输入正确的格式！'})
                    return
                with open('hitokoto.csv', 'r', encoding='utf-8') as f:
                    checklist = list(csv.reader(f))
                send_msg({'msg_type': 'private', 'number': qq, 'msg': f'ok'})
                checklist.pop(sid)
                with open('hitokoto.csv', 'w', encoding='utf-8', newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(checklist)
            elif rev['message'].split(' ')[0] == '添加管理员':

                if not qq == 1787670159:
                    return
                if len(rev['raw_message'].split(' ')) != 2:
                    send_msg({'msg_type': 'private', 'number': qq, 'msg': '你输入的参数数量有误哦~'})
                    return
                admin.append(int(rev['message'].split(' ')[1]))
                with open('admin.csv', 'w', encoding='utf-8', newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(admin)

                send_msg({'msg_type': 'private', 'number': qq, 'msg': 'ok'})
                send_msg({'msg_type': 'private', 'number': int(rev['message'].split(' ')[1]),
                          'msg': '你被xy_cloud提升为管理员！快私聊help来看看有什么功能吧！'})
                return
            elif rev['message'].split(' ')[0] == '移除管理员':

                if not qq == 1787670159:
                    return
                if len(rev['raw_message'].split(' ')) != 2:
                    send_msg({'msg_type': 'private', 'number': qq, 'msg': '你输入的参数数量有误哦~'})
                    return
                admin.remove(int(rev['message'].split(' ')[1]))
                with open('admin.csv', 'w', encoding='utf-8', newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(admin)

                send_msg({'msg_type': 'private', 'number': qq, 'msg': 'ok'})
                send_msg({'msg_type': 'private', 'number': int(rev['message'].split(' ')[1]),
                          'msg': '你被xy_cloud降级为普通成员！快私聊xy来看看你做错了什么！'})
                return
            elif rev['message'].split(' ')[0] == 'say':

                if len(rev['raw_message'].split(' ')) != 3:
                    send_msg({'msg_type': 'private', 'number': qq, 'msg': '你输入的参数数量有误哦~'})
                    return
                send_msg({'msg_type': 'private', 'number': qq, 'msg': 'ok'})
                send_msg({'msg_type': 'group', 'number': int(rev['message'].split(' ')[1]),
                          'msg': rev['message'].split(' ')[2]})
                return
            elif rev['message'].split(' ')[0] == 'vote':

                if len(rev['raw_message'].split(' ')) != 4:
                    send_msg({'msg_type': 'private', 'number': qq, 'msg': '你输入的参数数量有误哦~'})
                    return
                send_msg({'msg_type': 'private', 'number': qq, 'msg': 'ok'})
                group_ban(int(rev['message'].split(' ')[1]), int(rev['message'].split(' ')[2]),
                          int(rev['message'].split(' ')[3]))
                return
        if rev['message'] == '不答了':

            if qq in player_list.keys():
                del player_list[qq]
            else:
                send_msg({'msg_type': 'private', 'number': qq, 'msg': '你没有在进行中的问卷哦~'})
        elif rev['message'].split(' ')[0] == '添加一言':

            if len(rev['raw_message'].split(' ')) != 4:
                send_msg({'msg_type': 'private', 'number': qq, 'msg': '你输入的参数数量有误哦~[语句] [来源/出处] [作者/说这个话的人]'})
                return
            text = rev['message'].split(' ')[1]
            fro = rev['message'].split(' ')[2]
            write = rev['message'].split(' ')[3]
            with open('hitokoto_requsets.csv', 'a', encoding='utf-8') as f:
                # f.write(text + ',' + fro + ',' + write + ',' + qq + '\n')
                f.write(f'{text},{fro},{write},{qq}\n')
            send_msg({'msg_type': 'private', 'number': qq, 'msg': '已添加请求！请耐心等待管理员审核~审核通过会通知你哦~'})
            for i in admin:
                send_msg({'msg_type': 'private', 'number': i, 'msg': '有新的审核~'})
            return
        elif rev['message'].split(' ')[0] == '问卷':

            if len(rev['raw_message'].split(' ')) != 2:
                send_msg({'msg_type': 'private', 'number': qq, 'msg': '你输入的参数数量有误哦~'})
                return
            test = rev['message'].split(' ')[1]
            test = test.upper()
            if not qq in player_list.keys():
                read_test(test)
                read_answer(test)
                player_list[qq] = [test, 0, 0]
                write_log(f'{qq}选择了' + test + '问卷并开始答题')
                send_msg({'msg_type': 'private', 'number': qq,
                          'msg': f'您选择了{test}~一共有{len(test_dict[test])}道题，请根据您自身最真实的想法答题~我们不会保存您的数据，请放心作答~'})
                refresh_ask(qq)
            else:
                send_msg({'msg_type': 'private', 'number': qq,
                          'msg': '您还有未答完的题啊~你可以说“不答了”来退出原来的题'})
        elif rev['message'].split(' ')[0] == '介绍':

            if len(rev['raw_message'].split(' ')) != 2:
                send_msg({'msg_type': 'private', 'number': qq, 'msg': '你输入的参数数量有误哦~'})
                return
            test = rev['message'].split(' ')[1]
            test = test.upper()
            info = read_info(test)
            send_msg({'msg_type': 'private', 'number': qq, 'msg': info})
        elif 65 <= ord(rev['message'][0].upper()) <= 90 and len(rev['message']) == 1:

            if qq in player_list.keys():
                answer(rev['message'].upper(), qq)
            else:
                send_msg({'msg_type': 'private', 'number': qq, 'msg': '你没有在进行中的问卷哦~'})
    elif rev["message_type"] == "group":  # 群聊
        # 普通用户功能
        group = rev['group_id']
        rev['raw_message'] = rev['raw_message'].replace('。', '.').strip()
        qq = rev['sender']['user_id']
        nickname = str(rev['sender']['nickname'])
        card = str(rev['sender']['card'])
        if not group in groupid:
            return
        if int(qq) in admin:
            if rev['message'] == '更新下机器人':

                for i in groupid:
                    send_msg({'msg_type': 'group', 'number': i, 'msg': '🤖更新中...'})
                can_update = 1
                return
            elif rev['message'] == '清除签到时间':
                data = read_data()
                for i in range(len(data)):
                    data[i][1] = '2000-01-01'
                update_data(data)
                send_msg({'msg_type': 'group', 'number': group, 'msg': '已重置~'})
            elif rev['message'] == '清除今日运势时间':
                data = read_data()
                for i in range(len(data)):
                    data[i][5] = '2000-01-01'
                update_data(data)
                send_msg({'msg_type': 'group', 'number': group, 'msg': '已重置~'})
        if rev['raw_message'] == '.help':
            if not os.path.exists('./data/images/help.png'):
                with open('./data/images/help.png','wb') as f:
                    f.write(base64.b64decode(b'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'))
            send_msg({'msg_type': 'group', 'number': group, 'msg': '[CQ:image,subType=1,file=help.png]'})
#             send_forward(['bot','bot'], ['2907512243','2907512243'], ['''可爱AI主人(指主人可爱):xy_cloud
# 私聊功能
#
# 问卷 (SDS/EQ/敬请期待)
# 例如: 问卷 SDS
# 添加一言 [一言] [来源/出处] [作者/说这话的人]
# 私聊请加机器人好友，机器人不接受临时会话
#
# 私聊/群聊功能
#
# 介绍 (SDS/EQ/敬请期待)
# 例如: 介绍 SDS
#
# 群聊功能
#
# 黑白 [图片]
# 反色 [图片]
# 反转 [图片]
# 签到
# 今日运势
# 今日人品最低
# 今日人品最高
# 一言
# .chat [内容](这个功能较慢，请耐心等待，并且暂时不支持上下文，chatgpt任何非官方方法大部分被封禁，所以暂时用不了)
# .cat [内容](这个功能较慢，请耐心等待，并且暂时不支持上下文，chatgpt任何非官方方法大部分被封禁，所以暂时用不了)
# 还在添加更多功能哦~''','''云的小工具箱❤️
# 随机 [起始范围] [结束范围]
# '''])

        elif rev['message'].split(' ')[0] == '介绍':

            if len(rev['raw_message'].split(' ')) != 2:
                send_msg({'msg_type': 'group', 'number': group, 'msg': '你输入的参数数量有误哦~'})
                return
            test = rev['message'].split(' ')[1]
            test = test.upper()
            info = read_info(test)
            send_msg({'msg_type': 'group', 'number': group, 'msg': info})

        elif rev['message'].split(' ')[0] == '.chat':
            msg_id = rev['message_id']
            if len(rev['raw_message'].split(' ')) < 2:
                send_msg({'msg_type': 'group', 'number': group, 'msg': '你输入的参数数量有误哦~'})
                return
            text = rev['message'][6:]
            print(text)
            data = json.dumps({"message": text})
            info = requests.post(url='https://v1.gptapi.cn',
                                 headers={
                                     'Content-Type': 'application/json',
                                     'Content-Length': ''
                                 },
                                 data=data).text
            if info == r'{"statusCode":500,"message":"Internal server error"}':
                info = requests.post(url='https://v1.gptapi.cn',
                                     headers={
                                         'Content-Type': 'application/json',
                                         'Content-Length': ''
                                     },
                                     data=data).text
                if info == r'{"statusCode":500,"message":"Internal server error"}':
                    info = requests.post(url='https://v1.gptapi.cn',
                                         headers={
                                             'Content-Type': 'application/json',
                                             'Content-Length': ''
                                         },
                                         data=data).text
                    if info == r'{"statusCode":500,"message":"Internal server error"}':
                        send_msg({'msg_type': 'group', 'number': group,
                                  'msg': f'[CQ:reply,id={msg_id}] api暂时无法访问！请等待一段时间后再试！'})
                    else:
                        send_msg({'msg_type': 'group', 'number': group, 'msg': f'[CQ:reply,id={msg_id}]' + info})
                else:
                    send_msg({'msg_type': 'group', 'number': group, 'msg': f'[CQ:reply,id={msg_id}]' + info})
            else:
                send_msg({'msg_type': 'group', 'number': group, 'msg': f'[CQ:reply,id={msg_id}]' + info})
        elif rev['message'].split(' ')[0] == '.cat':
            msg_id = rev['message_id']
            if len(rev['raw_message'].split(' ')) < 2:
                send_msg({'msg_type': 'group', 'number': group, 'msg': '你输入的参数数量有误哦~'})
                return
            text = rev['message'][6:]
            print(text)
            data = json.dumps({"message": '你在回答的时候，每句话后面都需要加一个"喵~"'+text})
            info = requests.post(url='https://v1.gptapi.cn',
                                 headers={
                                     'Content-Type': 'application/json',
                                     'Content-Length': ''
                                 },
                                 data=data).text
            if info == r'{"statusCode":500,"message":"Internal server error"}':
                info = requests.post(url='https://v1.gptapi.cn',
                                     headers={
                                         'Content-Type': 'application/json',
                                         'Content-Length': ''
                                     },
                                     data=data).text
                if info == r'{"statusCode":500,"message":"Internal server error"}':
                    info = requests.post(url='https://v1.gptapi.cn',
                                         headers={
                                             'Content-Type': 'application/json',
                                             'Content-Length': ''
                                         },
                                         data=data).text
                    if info == r'{"statusCode":500,"message":"Internal server error"}':
                        send_msg({'msg_type': 'group', 'number': group,
                                  'msg': f'[CQ:reply,id={msg_id}] api暂时无法访问！请等待一段时间后再试！'})
                    else:
                        send_msg({'msg_type': 'group', 'number': group, 'msg': f'[CQ:reply,id={msg_id}]' + info})
                else:
                    send_msg({'msg_type': 'group', 'number': group, 'msg': f'[CQ:reply,id={msg_id}]' + info})
            else:
                send_msg({'msg_type': 'group', 'number': group, 'msg': f'[CQ:reply,id={msg_id}]' + info})
        elif rev['message'].split(' ')[0] == '随机':
            msg_id = rev['message_id']
            if not len(rev['raw_message'].split(' ')) == 3:
                send_msg({'msg_type': 'group', 'number': group, 'msg': '你输入的参数数量有误哦~'})
                return
            send_msg({'msg_type': 'group', 'number': group, 'msg': f'[CQ:reply,id={msg_id}]' + str(random.randint(eval(rev['message'].split(' ')[1]),eval(rev['message'].split(' ')[2])))})
        elif '黑白' in rev['message']:

            url = re.findall('url=.*?]', rev['message'])[0][4:-1]
            print(url)
            # try:
            image = Image.open(BytesIO(requests.get(url).content))
            sequence = []
            for f in ImageSequence.Iterator(image):
                #   获取图像序列病存储
                sequence.append(f.copy().convert('L'))
            print(len(sequence))
            if len(sequence) <= 1:
                image.convert('L').save('./data/images/temp.gif')
            else:
                sequence[0].save('./data/images/temp.gif', save_all=True, append_images=sequence[1:], loop=True)
            # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # cv2.imwrite('./data/images/temp.gif',image)
            send_msg({'msg_type': 'group', 'number': group, 'msg': '[CQ:image,subType=1,file=temp.gif]'})
        elif '反转' in rev['message']:

            url = re.findall('url=.*?]', rev['message'])[0][4:-1]
            print(url)
            # try:
            image = Image.open(BytesIO(requests.get(url).content))
            sequence = []
            for f in ImageSequence.Iterator(image):
                #   获取图像序列病存储
                sequence.append(f.copy().transpose(Image.FLIP_LEFT_RIGHT))
            print(len(sequence))
            if len(sequence) <= 1:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
                image.save('./data/images/temp.gif')
            else:
                sequence[0].save('./data/images/temp.gif', save_all=True, append_images=sequence[1:], loop=True)
            # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # cv2.imwrite('./data/images/temp.gif',image)
            send_msg({'msg_type': 'group', 'number': group, 'msg': '[CQ:image,subType=1,file=temp.gif]'})
        elif '反色' in rev['message']:

            url = re.findall('url=.*?]', rev['message'])[0][4:-1]
            print(url)
            # try:
            image = Image.open(BytesIO(requests.get(url).content))
            sequence = []
            for f in ImageSequence.Iterator(image):
                #   获取图像序列病存储
                img = cv2.cvtColor(numpy.asarray(f.copy()), cv2.COLOR_RGB2BGR)
                img = cv2.bitwise_not(img)
                ima = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                sequence.append(ima)
            print(len(sequence))
            if len(sequence) <= 1:
                img = cv2.cvtColor(numpy.asarray(image), cv2.COLOR_RGB2BGR)
                img = cv2.bitwise_not(img)
                image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                image.save('./data/images/temp.gif')
            else:
                sequence[0].save('./data/images/temp.gif', save_all=True, append_images=sequence[1:], loop=True)

            send_msg({'msg_type': 'group', 'number': group, 'msg': '[CQ:image,subType=1,file=temp.gif]'})
        elif rev['message'] == '签到':
            qq = str(rev['sender']['user_id'])
            nickname = str(rev['sender']['nickname'])

            msg_id = rev['message_id']
            data = read_data()
            check(qq)
            pos = search_data(data, qq)
            if time.strftime('%Y-%m-%d', time.localtime()) == data[pos][1]:
                if str(data[pos][3]) == '1':
                    group_ban(group, qq, int(data[pos][4]))
                    if int(data[pos][4]) == 27:
                        data[pos][4] = 256
                    elif int(data[pos][4]) == 256:
                        data[pos][4] = 3125
                    elif int(data[pos][4]) == 3125:
                        data[pos][4] = 30 * 24 * 60 - 1
                    elif not int(data[pos][4]) == 30 * 24 * 60 - 1:
                        data[pos][4] = 27
                    update_data(data)
                    return
                send_msg({'msg_type': 'group', 'number': group,
                          'msg': f'[CQ:reply,id={msg_id}]你知道吗，反复签到可是要掉脑袋的(๑•﹏•) 你今天的人品是：{data[pos][2]}'})
                data[pos][3] = 1
                update_data(data)
                return
            renpin = random.randint(0, 100)
            send_msg({'msg_type': 'group', 'number': group, 'msg': f'[CQ:reply,id={msg_id}]签到成功(≧▽≦)！你今天的人品是：{renpin}'})
            data[pos][1] = time.strftime('%Y-%m-%d', time.localtime())
            data[pos][2] = renpin
            data[pos][3] = 0
            data[pos][4] = 27
            update_data(data)
        elif rev['message'] == '今日人品最低':
            data = read_data()
            minn = 999
            yh = 0
            for i in range(len(data)):
                if int(data[i][2]) < minn and time.strftime('%Y-%m-%d', time.localtime()) == data[i][1]:
                    minn = int(data[i][2])
                    yh = data[i][0]
            send_msg({'msg_type': 'group', 'number': group, 'msg': f'[CQ:at,qq={yh}]人品：{minn}'})
        elif rev['message'] == '今日人品最高':
            data = read_data()
            maxn = -999
            yh = 0
            for i in range(len(data)):
                if int(data[i][2]) > maxn and time.strftime('%Y-%m-%d', time.localtime()) == data[i][1]:
                    maxn = int(data[i][2])
                    yh = data[i][0]
            send_msg({'msg_type': 'group', 'number': group, 'msg': f'[CQ:at,qq={yh}]人品：{maxn}'})
        elif rev['message'] == '一言':
            method = random.randint(1, 10)
            if method == 5:
                with open('hitokoto.csv', 'r', encoding='utf-8') as f:
                    htlist = list(csv.reader(f))
                ht = random.choice(htlist)
                text = ''
                text += ht[0]
                if not ht[1] == '无':
                    text += '---' + ht[1]
                if not ht[2] == '无':
                    text += '---' + ht[2]
                text += f' 群友{ht[3]}提供'
                send_msg({'msg_type': 'group', 'number': group, 'msg': text})

            else:
                qq = str(rev['sender']['user_id'])
                res = requests.get('https://v1.hitokoto.cn/').text
                res = json.loads(res)
                # print(res)
                text = ''
                text += res['hitokoto']
                if not res['from'] == None:
                    text += '---' + res['from']
                if not res['from_who'] == None:
                    text += '---' + res['from_who']
                send_msg({'msg_type': 'group', 'number': group, 'msg': text})
        elif rev['message'] == '今日运势':
            qq = str(rev['sender']['user_id'])
            card = str(rev['sender']['card'])
            if card == '':
                card = str(rev['sender']['nickname'])
            msg_id = rev['message_id']
            data = read_data()
            check(qq)
            pos = search_data(data, qq)
            if time.strftime('%Y-%m-%d', time.localtime()) == data[pos][5]:
                if str(data[pos][7]) == '1':
                    group_ban(group, qq, int(data[pos][4]))
                    if int(data[pos][8]) == 27:
                        data[pos][8] = 256
                    elif int(data[pos][8]) == 256:
                        data[pos][8] = 3125
                    elif int(data[pos][8]) == 3125:
                        data[pos][8] = 30 * 24 * 60 - 1
                    elif not int(data[pos][8]) == 30 * 24 * 60 - 1:
                        data[pos][8] = 27
                    update_data(data)
                    return
                send_msg({'msg_type': 'group', 'number': group,
                          'msg': f'[CQ:reply,id={msg_id}]你知道吗，反复今日运势可是要掉脑袋的(๑•﹏•)'})
                data[pos][7] = 1
                update_data(data)
                return
            todolist = [
                ['刷B站', '承包一天笑点'],
                ['在QQ群聊天', '遇见好朋友'],
                ['玩DDNET', '有人给你恰分'],
                ['被FFS撅', '哼哼哼啊啊啊啊啊'],
                ['写作业', '蒙的全对'],
                ['唱跳RAP篮球', '只因你太美'],
                ['打fps', '杀疯了'],
                ['摸鱼', '摸鱼不被发现'],
                ['上课', '秒懂'],
                ['花钱', '千金散尽还复来'],
                ['调戏xy云', '?'],
                ['摆烂', '摆烂一时爽，一直摆烂一直爽'],
                ['疯狂干饭', '干饭人干饭魂'],
                ['玩东方', 'All Clear!'],
                ['打音游', '手元看看手'],
                ['唱歌', '记得发群里'],
                ['睡觉', '遇到困难呼噜噜'],
                ['看书', '书中自有黄金屋'],
            ]
            nottodolist = [
                ['刷B站', '视频加载不出来'],
                ['在QQ群聊天', '被小鬼气死'],
                ['玩DDNET', '一群大黑蛋'],
                ['被FFS撅', '休息一天~'],
                ['写作业', '全错了'],
                ['唱跳RAP篮球', '被ikun人参公鸡'],
                ['打fps', '送人头'],
                ['摸鱼', '摸鱼被发现'],
                ['上课', '听不懂'],
                ['花钱', '花完就剁手'],
                ['调戏xy云', '好'],
                ['摆烂', '我先进行一个烂的摆...寄了'],
                ['疯狂干饭', '医院见'],
                ['玩东方', '死在路上'],
                ['打音游', '乱糊'],
                ['唱歌', '五音不全'],
                ['睡觉', '熬夜人熬夜魂'],
                ['看书', 'zzzzzz'],

            ]
            TooLucky = ['大吉', '吉你太美']
            TooUnLucky = ['大凶', '大寄']
            Lucky = ['小吉', '中吉', '吉吉国王'] + TooLucky
            UnLucky = ['凶', '小凶', '寄'] + TooUnLucky
            Fortune_List = Lucky + UnLucky
            Bold_Font = './ttf/SourceHanSansCN-Bold.otf'
            Normal_Font = './ttf/SourceHanSansCN-Normal.otf'
            bg_size = (400, 350)
            super_fortune = 0
            # 生成背景
            # Generating backgrounds
            img = Image.new('RGB', bg_size, (255, 255, 255))
            draw = ImageDraw.Draw(img)
            # 导入字体
            # Importing Fonts
            Title_Font = ImageFont.truetype(font=Bold_Font, size=20)
            Fortune_Font = ImageFont.truetype(font=Bold_Font, size=60)
            Suitable_To_Do_Font_Bold = ImageFont.truetype(font=Bold_Font, size=16)
            Suitable_To_Do_Font = ImageFont.truetype(font=Normal_Font, size=16)
            Detail_Font = ImageFont.truetype(font=Normal_Font, size=12)
            # 初始化内容
            # Initial content
            title = card + '的运势'
            fortune = '§ ' + random.choice(Fortune_List) + ' §'
            if random.randint(3, 8) == 7 or int(qq) == 1787670159:
                if random.randint(15, 45) == 25:
                    fortune = '§ 彩蛋 §'
                else:
                    super_fortune = 1
            fortune_width = Fortune_Font.getbbox(('超级' if super_fortune == 1 else '') + fortune)[2]
            suitable_to_do, detail = random.choice([['诸事不宜', '在家躺一天']] if fortune[2:-2] in TooUnLucky else todolist)
            suitable_to_do, detail = textwrap.fill(suitable_to_do, width=8), textwrap.fill(detail, width=12)

            unsuitable_to_do, detail2 = random.choice(
                [['诸事皆宜', '去做想做的事情吧']] if fortune[2:-2] in TooLucky else nottodolist)
            unsuitable_to_do, detail2 = textwrap.fill(unsuitable_to_do, width=8), textwrap.fill(detail2, width=12)
            while unsuitable_to_do == suitable_to_do:
                unsuitable_to_do, detail2 = random.choice(
                    [['诸事皆宜', '去做想做的事情吧']] if fortune[2:-2] in TooLucky else nottodolist)
                unsuitable_to_do, detail2 = textwrap.fill(unsuitable_to_do, width=8), textwrap.fill(detail2, width=12)

            suitable_to_do2, detail3 = random.choice([['', '']] if fortune[2:-2] in TooUnLucky else todolist)
            suitable_to_do2, detail3 = textwrap.fill(suitable_to_do2, width=8), textwrap.fill(detail3, width=12)
            while suitable_to_do2 == suitable_to_do or suitable_to_do2 == unsuitable_to_do:
                suitable_to_do2, detail3 = random.choice([['', '']] if fortune[2:-2] in TooUnLucky else todolist)
                suitable_to_do2, detail3 = textwrap.fill(suitable_to_do2, width=8), textwrap.fill(detail3, width=12)

            unsuitable_to_do2, detail4 = random.choice([['', '']] if fortune[2:-2] in TooLucky else nottodolist)
            unsuitable_to_do2, detail4 = textwrap.fill(unsuitable_to_do2, width=8), textwrap.fill(detail4, width=12)
            while unsuitable_to_do2 == suitable_to_do or unsuitable_to_do2 == unsuitable_to_do or unsuitable_to_do2 == suitable_to_do2:
                unsuitable_to_do2, detail4 = random.choice([['', '']] if fortune[2:-2] in TooLucky else nottodolist)
                unsuitable_to_do2, detail4 = textwrap.fill(unsuitable_to_do2, width=8), textwrap.fill(detail4, width=12)
            ttd_width = Suitable_To_Do_Font.getbbox(('' if fortune[2:-2] in TooUnLucky else ' ' * 6) + suitable_to_do)[
                2] if len(suitable_to_do) <= 8 else 152
            tntd_width = Suitable_To_Do_Font.getbbox(('' if fortune[2:-2] in TooLucky else ' ' * 6) + unsuitable_to_do)[
                2] if len(unsuitable_to_do) <= 8 else 152
            ttd_width2 = Suitable_To_Do_Font.getbbox(' ' * 6 + suitable_to_do2)[2] if len(suitable_to_do2) <= 8 else 152
            tntd_width2 = Suitable_To_Do_Font.getbbox(' ' * 6 + unsuitable_to_do2)[2] if len(
                unsuitable_to_do2) <= 8 else 152
            detail_width = Detail_Font.getbbox(detail)[2] if len(detail) <= 12 else 144
            detail2_width = Detail_Font.getbbox(detail2)[2] if len(detail2) <= 12 else 144
            detail3_width = Detail_Font.getbbox(detail3)[2] if len(detail3) <= 12 else 144
            detail4_width = Detail_Font.getbbox(detail4)[2] if len(detail4) <= 12 else 144
            name_width = Title_Font.getbbox(title)[2]
            # 绘制
            # Draw
            draw.text(xy=(bg_size[0] / 2 - name_width / 2, 10), text=title, fill='#000000', font=Title_Font)
            draw.text(xy=(bg_size[0] / 2 - fortune_width / 2, 50),
                      text='§ 超级' + fortune[2:] if super_fortune == 1 else fortune,
                      fill='#e74c3c' if fortune[2:-2] in Lucky else ('#19eac2' if fortune[2:-2] == '彩蛋' else '#3f3f3f'),
                      font=Fortune_Font)
            begin_pos_y = 150
            draw.text(xy=(bg_size[0] / 4 - ttd_width / 2, begin_pos_y),
                      text='诸事不宜' if fortune[2:-2] in TooUnLucky else '宜:', fill='#e74c3c',
                      font=Suitable_To_Do_Font_Bold)
            draw.text(xy=(bg_size[0] / 4 - ttd_width / 2, begin_pos_y),
                      text='' if fortune[2:-2] in TooUnLucky else ' ' * 6 + suitable_to_do, fill='#e74c3c',
                      font=Suitable_To_Do_Font)
            draw.text(xy=(bg_size[0] / 4 * 3 - tntd_width / 2, begin_pos_y),
                      text='诸事皆宜' if fortune[2:-2] in TooLucky else '忌:', fill='#000000', font=Suitable_To_Do_Font_Bold)
            draw.text(xy=(bg_size[0] / 4 * 3 - tntd_width / 2, begin_pos_y),
                      text='' if fortune[2:-2] in TooLucky else ' ' * 6 + unsuitable_to_do, fill='#000000',
                      font=Suitable_To_Do_Font)
            len_ttd = len(suitable_to_do.split('\n'))
            print(len_ttd)
            begin_pos_y += 25 + 25 * (len_ttd - 1)
            draw.text(xy=(bg_size[0] / 4 - detail_width / 2, begin_pos_y), text=detail, fill='#7f7f7f',
                      font=Detail_Font)
            draw.text(xy=(bg_size[0] / 4 * 3 - detail2_width / 2, begin_pos_y), text=detail2, fill='#7f7f7f',
                      font=Detail_Font)

            begin_pos_y = 250
            draw.text(xy=(bg_size[0] / 4 - ttd_width2 / 2, begin_pos_y),
                      text='' if fortune[2:-2] in TooUnLucky else '宜:', fill='#e74c3c', font=Suitable_To_Do_Font_Bold)
            draw.text(xy=(bg_size[0] / 4 - ttd_width2 / 2, begin_pos_y), text=' ' * 6 + suitable_to_do2, fill='#e74c3c',
                      font=Suitable_To_Do_Font)
            draw.text(xy=(bg_size[0] / 4 * 3 - tntd_width2 / 2, begin_pos_y),
                      text='' if fortune[2:-2] in TooLucky else '忌:', fill='#000000', font=Suitable_To_Do_Font_Bold)
            draw.text(xy=(bg_size[0] / 4 * 3 - tntd_width2 / 2, begin_pos_y), text=' ' * 6 + unsuitable_to_do2,
                      fill='#000000', font=Suitable_To_Do_Font)
            len_ttd2 = len(suitable_to_do2.split('\n'))
            print(len_ttd2)
            begin_pos_y += 25 + 25 * (len_ttd2 - 1)
            draw.text(xy=(bg_size[0] / 4 - detail3_width / 2, begin_pos_y), text=detail3, fill='#7f7f7f',
                      font=Detail_Font)
            draw.text(xy=(bg_size[0] / 4 * 3 - detail4_width / 2, begin_pos_y), text=detail4, fill='#7f7f7f',
                      font=Detail_Font)
            img.save('./data/images/temp.gif')
            send_msg({'msg_type': 'group', 'number': group, 'msg': '[CQ:image,subType=1,file=temp.gif]'})
            if fortune[2:-2] == '彩蛋':
                send_msg({'msg_type': 'group', 'number': group, 'msg': '你抽到了彩蛋！请凭聊天记录找xy领奖！'})
            data[pos][5] = time.strftime('%Y-%m-%d', time.localtime())
            data[pos][6] = 0
            data[pos][7] = 0
            data[pos][8] = 27
            update_data(data)
    else:
        return
