from django import template
from django.utils.html import format_html
register = template.Library()


@register.simple_tag
def render_data(model_obj, fields):
    """
    :param model_obj:  数据查询对象
    :param fields: 表字段
    :return:
    """
    html_td = ""
    for field in fields:
        if hasattr(model_obj, field):
            field_data = getattr(model_obj, field)  # 获取字段的值
            if field == "id":
                html_td += "<td name='%s'><a href='%s'>%s</a></td>" % (field, field_data, field_data)
                continue
            field_obj = model_obj._meta.get_field(field)  # 获取字段对象
            if field_obj.is_relation:  # 如果表存在关系映射
                if field_obj.one_to_many:
                    pass
                elif field_obj.many_to_one:
                    pass
                elif field_obj.many_to_many:
                    field_many = field_data.select_related()
                    many_field_data = []
                    for field_many_obj in field_many:
                        many_field_data.append(str(field_many_obj))
                    field_data = ",".join(many_field_data)
                if not field_obj.concrete:  # 如果字段不是在model定义时创建的，即django自己映射生成的字段反向查找字段
                    remote_name = field_obj.related_model._meta.model_name  # 获取关联的外键model名字
                    local_name = model_obj._meta.model_name  # 获取本地的model名字
                    if remote_name == local_name:  # 如果外键关联的是本地字段，则不进行操作
                        continue
            try:
                if field_obj.choices:  # 如果是选择字段，尝试获取字段描述名
                    field_data = getattr(model_obj, "get_%s_display" % field)()
            except AttributeError:
                continue
            html_td += "<td>%s</td>" % field_data
    return format_html(html_td)


@register.simple_tag
def get_page(current_page, total_page):
    page_html = []
    if current_page <= 1:
        prev = """<li class="">
                 <a href="?page=%s" aria-label="Previous">
                <span aria-hidden="true">&laquo;</span></a></li>""" % (1, )
    else:
        prev = """<li class="">
                <a href="?page=%s" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span></a></li>""" % (current_page-1,)
    page_html.append(prev)
    for i in range(1, total_page+1):
        offset = abs(current_page - i)
        if offset < 3:
            if current_page == i:
                page_ele = '''<li class='active'><a href="?page= %s">%s</a></li>''' % (i, i)
            else:
                page_ele = '''<li><a href="?page=%s">%s</a></li>''' % (i, i)
            page_html.append(page_ele)
        else:
            page_html = page_html
    if current_page >= total_page:
        next = """<li class="">
                <a href="?page=%s" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span></a></li>""" % (total_page,)
    else:
        next = """<li class="">
                <a href="?page=%s" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span></a></li>""" % (current_page+1,)
    page_html.append(next)
    return format_html(''.join(page_html))