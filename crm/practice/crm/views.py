from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models.base import ModelBase
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from crm import forms
from crm import models
from crm import permissions
from crm.templatetags import field_handle
import collections
import json
# Create your views here.


@login_required(login_url="/")
def index(request):
    tables = collections.OrderedDict()  # 定义有序字典
    for i in dir(models):  # 循环models下自己创建的表的表名（字符串），过滤出来表名
        if isinstance(getattr(models, i), ModelBase):
            field_name = getattr(models,i)._meta.verbose_name  # 获取表的别名
            tables[field_name] = (getattr(models, i).__name__)
    #         print(field_name)
    # print(tables)
    return render(request, 'crm/index.html', {'tables': tables,
                                              'user': request.user})


@permissions.check_permission
def show_class_info(request, model_name):
    model_obj = get_model(model_name)
    model_data = model_obj.objects.all()  # 获取所有数据
    paginator = Paginator(model_data, 2)
    # 前端提交的需要取哪一行
    page = request.GET.get('page')
    try:
        model_data = paginator.page(page)
    # 如果输入的不是数字，就返回第一页
    except PageNotAnInteger:
        model_data = paginator.page(1)
    # 若果超出了就显示最后一页
    except EmptyPage:
        model_data = paginator.page(paginator.num_pages)
    field_names, field_verbose_names, class_verbose_name = get_all_field_names(model_name)
    if request.method == "POST":
        id_list = json.loads(request.POST["data"])
        print(id_list)
        # ID: {'search': '1'}
        # ID: {'id': ['3']}
        for k, v in id_list.items():
            if k == "id":
                # delete handle
                del_flag = False
                for ID in v:
                    model_data = model_obj.objects.filter(id=int(ID))
                    if model_data:
                        model_data.delete()
                        del_flag = True
                    else:
                        del_flag = False
                        break
                if del_flag:
                    return HttpResponse("True")
                else:
                    return HttpResponse("False")
            else:
                # search handle
                try:
                    model_data = model_obj.objects.filter(id=int(v))
                    result = []
                    field_names = get_all_field_names(model_name)[0]
                    for model in model_data:
                        result.append(field_handle.render_data(model, field_names))
                except Exception as e:
                    print(e)
                    result = ""
                return HttpResponse(json.dumps(result))

    return render(request, 'crm/show_field_info/field_dis_model.html', {
                                                        'field_verbose_name': field_verbose_names,
                                                        'class_verbose_name': class_verbose_name,
                                                        'field_names': field_names,
                                                        'table_name': model_name,
                                                        'model_obj': model_data,
                                                        'Request': request})


@permissions.check_permission
def add(request, model_name):
    if hasattr(models, model_name):
        model_obj = getattr(models, model_name)  # 获取model_obj
        modelform_obj = forms.modelform(model_obj)()  # 实例化modelform
        class_verbose_name = model_obj._meta.verbose_name_plural  # 获取自定义表名
        if request.method == "POST":
            modelform_obj = forms.modelform(model_obj)(request.POST)  # 实例化modelform
            if modelform_obj.is_valid():
                modelform_obj.save()
                base_url = "/".join(request.path.split("/")[:-2])
                return redirect(base_url)
        return render(request, 'crm/detail.html', {'model_obj': modelform_obj, 'table_name': model_name,
                                                   'class_verbose_name': class_verbose_name})


@permissions.check_permission
def change(request, model_name, t_id):
    if hasattr(models, model_name):
        model_obj = getattr(models, model_name)
        model_data = model_obj.objects.get(id=t_id)
        modelform_obj = forms.modelform(model_obj)(instance=model_data)
        if request.method == "POST":
            modelform_obj = forms.modelform(model_obj)(request.POST, instance=model_data)
            if modelform_obj.is_valid():
                modelform_obj.save()
                base_url = "/".join(request.path.split("/")[:-2])
                return redirect(base_url)
        return render(request, 'crm/detail.html', {'model_obj': modelform_obj,
                                                   'table_name': model_name,
                                                   'id': t_id,
                                                   })


def acc_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        passwd = request.POST['password']
        print("用户名：%s 密码:%s" % (username, passwd))
        user = authenticate(username=username, password=passwd)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/crm')
        else:
            log_error = 'Wrong user or Password'
            return render(request, 'crm/login/index.html', {'log_error': log_error})
    return render(request, 'crm/login/index.html')


def acc_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def get_model(model_name):
    if hasattr(models, model_name):
        model_obj = getattr(models, model_name)  # 获取model_obj
        return model_obj


def get_all_field_names(model_name):
    field_names = []
    field_verbose_names = []
    model_obj = get_model(model_name)
    class_verbose_name = model_obj._meta.verbose_name_plural
    try:
        fields_list = model_obj._meta._get_fields()
        for field in fields_list:
            if hasattr(field, 'verbose_name'):
                field_verbose_names.append(field.verbose_name)  # 别名字段(head)
            field_names.append(field.name)  # 原生字段(body)
    except AttributeError:
        pass
    """
    verbose: ['ID', 'QQ号', '姓名', '手机号', '学号', '客户来源', '转介绍自学员', '咨询课程', '班级类型',
    '客户咨询内容详情', '状态', '课程顾问', '咨询日期', '已报班级']
    normal: ['internal_referral', 'consultrecord', 'studyrecord', 'id', 'qq', 'name', 'phone', 'stu_id', 'source',
    'referral_from', 'course', 'class_type', 'customer_note', 'status', 'consultant', 'date', 'class_list']
    internal_referral
    'ManyToOneRel' object has no attribute 'verbose_name'
    consultrecord
    'ManyToOneRel' object has no attribute 'verbose_name'
    studyrecord
    'ManyToOneRel' object has no attribute 'verbose_name'
    """
    return field_names, field_verbose_names, class_verbose_name



