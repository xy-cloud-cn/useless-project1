# -*- coding: utf-8 -*-
'''
@Author   : xy_cloud
@IDE      : PyCharm
@Project  : Python Project
@File     : func.py
@Time     : 2022/12/9 14:45
'''
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
can_exit=0
can_update=0
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


def search_data(data, qq):
    for i in range(len(data)):
        if qq == data[i][0]:
            return i
    return -1
def main(rev):
    global groupid, player_list, data, admin,can_exit,can_update
    random.seed(time.time())
    # print(rev) #需要功能自己DIY
    if rev["message_type"] == "private":  # 私聊
        qq = rev['sender']['user_id']
        if qq in admin:
            if rev['message'] == 'help':
                send_msg({'msg_type': 'private', 'number': qq, 'msg': '私聊\n'
                                                                      'get\n'
                                                                      '审核 [编号] [通过/不通过] [不通过原因]\n'
                                                                      '添加管理员 [qq](xy专属)\n'
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

            elif rev['message'].split(' ')[0] == '添加管理员':

                if not qq == 1787670159:
                    return
                if len(rev['raw_message'].split(' ')) != 2:
                    send_msg({'msg_type': 'private', 'number': qq, 'msg': '你输入的参数数量有误哦~'})
                    return
                admin.append(int(rev['message'].split(' ')[1]))
                send_msg({'msg_type': 'private', 'number': qq, 'msg': 'ok'})
                send_msg({'msg_type': 'private', 'number': int(rev['message'].split(' ')[1]), 'msg': '你被xy_cloud提升为管理员！快私聊help来看看有什么功能吧！'})
                return
            elif rev['message'].split(' ')[0] == 'say':

                if len(rev['raw_message'].split(' ')) != 3:
                    send_msg({'msg_type': 'private', 'number': qq, 'msg': '你输入的参数数量有误哦~'})
                    return
                send_msg({'msg_type': 'private', 'number': qq, 'msg': 'ok'})
                send_msg({'msg_type': 'group', 'number': int(rev['message'].split(' ')[1]), 'msg': rev['message'].split(' ')[2]})
                return
            elif rev['message'].split(' ')[0] == 'vote':

                if len(rev['raw_message'].split(' ')) != 4:
                    send_msg({'msg_type': 'private', 'number': qq, 'msg': '你输入的参数数量有误哦~'})
                    return
                send_msg({'msg_type': 'private', 'number': qq, 'msg': 'ok'})
                group_ban(int(rev['message'].split(' ')[1]),int(rev['message'].split(' ')[2]),int(rev['message'].split(' ')[3]))
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
            send_msg({'msg_type': 'group', 'number': group, 'msg': '''可爱AI主人(指主人可爱):xy_cloud
私聊功能

问卷 (SDS/EQ/敬请期待)
例如: 问卷 SDS
添加一言 [一言] [来源/出处] [作者/说这话的人]
私聊请加机器人好友，机器人不接受临时会话

私聊/群聊功能

介绍 (SDS/EQ/敬请期待)
例如: 介绍 SDS

群聊功能

黑白 [图片]
反色 [图片]
反转 [图片]
签到
今日运势
今日人品最低
今日人品最高
一言
还在添加更多功能哦~'''})

        elif rev['message'].split(' ')[0] == '介绍':

            if len(rev['raw_message'].split(' ')) != 2:
                send_msg({'msg_type': 'group', 'number': group, 'msg': '你输入的参数数量有误哦~'})
                return
            test = rev['message'].split(' ')[1]
            test = test.upper()
            info = read_info(test)
            send_msg({'msg_type': 'group', 'number': group, 'msg': info})
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
                        data[pos][4] = 30*24*60-1
                    elif not int(data[pos][4]) == 30*24*60-1:
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
            method=random.randint(1,10)
            if method==5:
                with open('hitokoto.csv', 'r', encoding='utf-8') as f:
                    htlist = list(csv.reader(f))
                ht=random.choice(htlist)
                text = ''
                text += ht[0]
                if not ht[1] == '无':
                    text += '---' + ht[1]
                if not ht[2] == '无':
                    text += '---' + ht[2]
                text+=f' 群友{ht[3]}提供'
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
            if card=='':
                card=str(rev['sender']['nickname'])
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
            TooUnLucky = ['大凶']
            Lucky = ['小吉', '中吉','吉吉国王'] + TooLucky
            UnLucky = ['凶', '小凶'] + TooUnLucky
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
            if random.randint(1,10)==7 or int(qq)==1787670159:
                if random.randint(1,100)==25:
                    fortune = '§ 彩蛋 §'
                else:
                    super_fortune=1
            fortune_width = Fortune_Font.getbbox(('超级' if super_fortune==1 else '')+fortune)[2]
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
            draw.text(xy=(bg_size[0] / 2 - fortune_width / 2, 50), text=('超级' if super_fortune==1 else '')+fortune,
                      fill='#e74c3c' if fortune[2:-2] in Lucky else ('#19eac2' if fortune[2:-2] == '彩蛋' else '#3f3f3f'), font=Fortune_Font)
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
