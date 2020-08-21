# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import base64
import copy
import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import View
from home_application.models import SelectScript, Doinfo
from blueking.component.shortcuts import get_client_by_user
from blueking.component.shortcuts import get_client_by_request
import logging

client = get_client_by_user('test')
logger = logging.getLogger(__name__)

bk_app_code='test-blue'
bk_app_secret= 'fbb41929-84aa-481b-be62-34020549870f'
bk_token='q6tEw9T5Jp6Q3et23xNhhtHWbzMFCklVSYtF0AYcdCM'
from .celery_tasks import  async_status

# 查询业务
def get_biz_info():
    kwargs = {
        'bk_app_code':bk_app_code,
        'bk_app_secret':bk_app_secret,
        'bk_token':bk_token,
        'fields':[
            "bk_biz_id",
            "bk_biz_name"
        ]}
    res=client.cc.search_business(kwargs)
    biz_name=[]
    biz_id=[]
    info={}
    if res.get('result',False):
        for i in res['data']['info']:
            biz_name.append(i['bk_biz_name'])
            biz_id.append(i['bk_biz_id'])
            info=dict(zip(biz_name,biz_id))
    else:
        logger.error(u"请求业务列表失败：%s"%res.get('message'))
        info={}
    return info

# 根据条件查询主机
def ser_host(biz_id):
    kwargs = {
        'bk_token': bk_token,
        'bk_biz_id':biz_id
    }
    res = client.cc.search_host(kwargs)
    hosts=[]
    if res.get('result'):
        for host_info in res['data']['info']:
            hosts.append({
                'ip':host_info['host']['bk_host_innerip'],
                'os':host_info['host']['bk_os_name'],
                'host_id':host_info['host']['bk_host_id'],
                'name':host_info['host']['bk_host_name'],
                'cloud_id':host_info['host']['bk_cloud_id'][0]['id'],
            })
    else:
        logger.error(u"请求业务列表失败：%s"%res.get('message'))
        hosts=[]
    return hosts

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
def home(request):
    """
    首页
    """
    return render(request, 'home_application/index_home.html')


def dev_guide(request):
    """
    开发指引
    """
    return render(request, 'home_application/dev_guide.html')


def contact(request):
    """
    联系页
    """
    return render(request, 'home_application/contact.html')

def hello(request):
    return HttpResponse('Hello World')

def task(request):
    tasks=SelectScript.objects.all()
    data={'tasks':tasks,
          'info':get_biz_info().items(),
          'data':ser_host(2)
          }
    return render(request,'task.html',data)

# 根据业务查询主机接口
def get_host(request):
    biz_id = request.GET.get('biz_id')
    if biz_id:
        biz_id = int(biz_id)
    else:
        return JsonResponse({'result':False,'message':'must provide biz_id to get hosts'})
    data= ser_host(biz_id)
    table_data= render_to_string('execute_tbody.html',{'data':data})

    return JsonResponse({'result': True, 'message': 'sucess','data':table_data})

def execute_script(request):
    biz_id=request.POST.get('biz_id')
    script_id=request.POST.get('script_id')
    script_obj = SelectScript.objects.get(pk=script_id)
    objtest = base64.b16encode(script_obj.scriptcontent.encode('utf-8'))
    ip_id=request.POST.getlist('ip_id[]')
    ips = {'bk_cloud_id':0,'ip':0}
    ip_info=[]
    for i in ip_id:
        ips['ip']=i
        ip_info.append(copy.deepcopy(ips))
    kwargs = {
        'bk_token': bk_token,
        'bk_biz_id':biz_id,
        'script_content':str(objtest,'utf-8'),
        'account':'root',
        'script_type':1,
        'ip_list':ip_info
    }
    execute_data=client.job.fast_execute_script(kwargs)
    if execute_data.get('result',False):
        data=execute_data['data']
        result = True
        message = str(execute_data.get('message'))
        async_status.apply_async(args=[client,data,biz_id,script_obj,ip_id],kwargs={})
    else:
        data=[]
        result =False
        message = 'False'
        logger.error(u'查询主机列表失败：%s'%execute_data.get('message'))
    return JsonResponse({'result':result,'message':message,'data':data})

def get_usernames():
    kwargs={
        'bk_token': bk_token,
    }
    res=client.bk_login.get_all_users(kwargs)
    usernames=[]
    if res.get('result',False):
        for i in res['data']:
            usernames.append((i['bk_username']))
    else:
        logger.error(u'查询所有用户列表失败：%s'%res.get('messgae'))
    return usernames


def record(request):

    tasks=SelectScript.objects.all()
    doinfos = Doinfo.objects.all()
    data={
        'info':get_biz_info().items(),
        'usernames':get_usernames(),
        'tasks':tasks,
        'doinfos':doinfos
    }
    return render(request,'record.html',data)

def inquiry(request):
    try:
        biz_id = request.POST.get('biz_id')
        username = request.POST.get('username')
        script_id = request.POST.get('script_id')
        time = request.POST.get('time')   #"2020/03/27 - 2020/03/27"
        doinfo = Doinfo.objects.all()
        doinfo = doinfo.filter(businessname=int(biz_id)).filter(username=username).filter(script_id=int(script_id))
        starttime,endtime= time.split('-')
        starttime=starttime.strip().replace('/','-')+' 00:00:00'
        endtime = endtime.strip().replace('/','-')+' 23:59:00'
        start_time = datetime.strptime(starttime,'%Y-%m-%d %H:%M:%S')
        endt_ime = datetime.strptime(endtime,'%Y-%m-%d %H:%M:%S')

        doinfo = doinfo.filter(starttime__range=(start_time,endt_ime))
        data=[ info.to_dirct() for info in doinfo]

        table_data = render_to_string('record_tbody.html',{'doinfos':data})
        result= True
        message = 'success'

    except Exception as err:
        table_data=[]
        result = False
        message = str(err)
    return JsonResponse({'result':result,'message':message,'data':table_data})