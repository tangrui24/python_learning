#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.core.urlresolvers import resolve
from django.shortcuts import render

# 权限控制字典，url别名，提交方法，属性综合判断那种权限
perm_dic = {
    'view_customer_list': ['show', 'GET', []],
    'view_customer_info': ['change', 'GET', []],
    'edit_customer_info': ['change', 'POST', []],
    'view_new_customer': ['add', 'GET', []],
    'add_new_customer': ['add', 'POST', []],
    'del_customer_info': ["show", "POST", ["data", ]],
}


# 权限控制主要逻辑函数
def perm_check(*args, **kwargs):
    # views函数中的request
    request = args[0]
    url_resovle_obj = resolve(request.path_info)
    # url别名
    current_url_namespace = url_resovle_obj.url_name
    # 匹配标识符
    matched_flag = False
    # 匹配的key值
    matched_perm_key = None
    # url别名存在
    if current_url_namespace is not None:
        print("find perm...")
        # 遍历权限字典
        for perm_key in perm_dic:
            # 权限字典的值
            perm_val = perm_dic[perm_key]
            # 权限的值个数必须为3个
            if len(perm_val) == 3:
                # url别名，提交方法，属性列表分别赋值
                url_namespace, request_method, request_args = perm_val
                # url别名匹配
                if url_namespace == current_url_namespace:
                    # 提交方式匹配
                    if request.method == request_method:
                        # 属性列表为空就匹配上了，跳出循环
                        if not request_args:  # if empty , pass
                            matched_flag = True
                            matched_perm_key = perm_key
                            print('matched...')
                            break
                        else:
                            for request_arg in request_args:
                                request_method_func = getattr(request,request_method)
                                if request_method_func.get(request_arg) is not None:
                                    matched_flag = True
                                else:
                                    matched_flag = False
                                    print("request arg [%s] not matched" % request_arg)
                                    break
                            if matched_flag:
                                print("--passed permission check--")
                                matched_perm_key = perm_key
                                break

    else:
        return True
    if matched_flag:
        perm_str = "crm.%s" % (matched_perm_key)  # crm.view_customer_list
        if request.user.has_perm(perm_str):
            print("\033[42;1m--------passed permission check----\033[0m")
            return True
        else:
            print("\033[41;1m ----- no permission ----\033[0m")
            print(request.user, perm_str)
            return False
    else:
        print("\033[41;1m ----- no matched permission  ----\033[0m")


def check_permission(func):
    def wrapper(*args, **kwargs):
        print('---start check perm---')
        if perm_check(*args, **kwargs) is not True:
            return render(args[0], 'crm/403.html')
        return func(*args, **kwargs)
    return wrapper