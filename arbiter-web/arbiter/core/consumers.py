import os
from subprocess import getoutput, Popen, PIPE, STDOUT

from channels import Group
from channels.sessions import channel_session
from .models import Run_Log
from mongoengine import *
# message.reply_channel    一个客户端通道的对象
# message.reply_channel.send(chunk)  用来唯一返回这个客户端

# 一个管道大概会持续30s


isEditFilesName = []#全局变量，保存正在被编辑的文件名
# 当连接上时，发回去一个connect字符串
@channel_session
def ws_connect(message):
    message.reply_channel.send({"accept": True})


# 将发来的信息原样返回
@channel_session
def ws_message(message):
    cmd = message.content['text']
    log_content=''
    #通过自定义字符分割需要的类型
    if (cmd.split(' ')[0] == 'runCase'):
        message.reply_channel.send({
            "text": "**********************************************开始执行***********************************************"
        }, immediately=True)
        case_name = cmd.split(' ')[1]

        # if os.name == 'nt':
        #     setenv = getoutput('set PYTHONPATH='+caseBasePath)
        #     # runcmd = Popen(['nosetests', '-vv', '-P', case_name], bufsize=0, stdout=PIPE, stderr=STDOUT)
        # else:
        #     # setenv = getoutput('export PYTHONPATH=' + caseBasePath)
        #     setenv = Popen(['/bin/sh', '-c', 'export', 'PYTHONPATH='+caseBasePath], bufsize=0, stdout=PIPE, stderr=STDOUT)

        # runcmd = Popen('nosetests -vv -P --exe  ' + case_name, bufsize=0, stdout=PIPE, stderr=STDOUT)
        runcmd = Popen(['nosetests', '-P', '--nologcapture', case_name], bufsize=0, stdout=PIPE, stderr=STDOUT)
        while True:
            line = runcmd.stdout.readline()
            if not line: break
            text = line.decode('utf-8')
            #拼接日志内容
            log_content = log_content+text

            # log_list.append(line.decode('utf-8'))
            message.reply_channel.send({
                "text": text
            }, immediately=True)
        message.reply_channel.send({
            "text": "**********************************************结束执行***********************************************"
        }, immediately=True)

        #将日志存入mysql
        # mysql 存入格式和内容需要完善
        #dic = {'case_info':case_name,'content': log_content, 'begin_time': '','run_time': 10}
        #Run_Log.objects.create(**dic)

        #mongodb
        Run_Log.objects.create(case_info=case_name)
        log = Run_Log(case_info=case_name)
        log.content ="log_content"
        log.save()

    if (cmd.split(' ')[0] == 'validateEdit'):

        if(cmd.split(' ')[1] == '0'):
            if(cmd.split(' ')[2] in isEditFilesName):
                message.reply_channel.send({
                    "text": "isBusy"
                }, immediately=True)
                isEditFilesName.append(cmd.split(' ')[2])
        if (cmd.split(' ')[1] == '1'):
            isEditFilesName.remove(cmd.split(' ')[2])



# 断开连接时发送一个disconnect字符串，当然，他已经收不到了
@channel_session
def ws_disconnect(message):
    message.reply_channel.send({"disc": True})
