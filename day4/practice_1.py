import re
cac = "-1-2*((-60-30+(-40.0/5)*(-9-2*5/3+7/3*99/4*2998+10*568/14))-(-4*3)/(-16-3*2))"


def bracket_handler(expression):
    bracket = re.compile(r"\([^()]+\)")
    # k = re.compile(r"\(([+\-\*\/]*\d+\.?\d*)+\)")
    # kk = re.compile('\(([\+\-\*\/]*\d+\.*\d*){1,}\)')
    if bracket.search(expression):
        old_exp = bracket.search(expression).group()
        exp = re.sub(r"[()]{1}", "", old_exp)
        ret = compute(exp)
        new_exp = expression.replace(old_exp, str(ret))
        return bracket_handler(new_exp)
    else:
        return compute(expression)


def multiply_divide_handler(expression):
    multiply_divide = re.compile(r"\d+\.?\d*[\*\/]+[+\-]?\d+\.?\d*")
    ret = multiply_divide.search(expression)
    if ret:
        exp = ret.group()
        if re.search("\*", exp):
            ret = float(exp.split("*")[0]) * float(exp.split("*")[1])
            new_exp = expression.replace(exp, str(ret))
        else:
            ret = float(exp.split("/")[0]) / float(exp.split("/")[1])
            new_exp = expression.replace(exp, str(ret))
        return multiply_divide_handler(new_exp)
    else:
        return expression


def plug_subtract_handler(expression):
    plug_subtract = re.compile(r"[+\-]?\d+\.?\d*[+\-]+\d+\.?\d*")
    expression = format_add_sub(expression)
    ret = plug_subtract.search(expression)
    if ret:
        exp = ret.group()
        if re.search("\+", exp):
            ret = float(exp.split("+")[0]) + float(exp.split("+")[1])
            new_exp = expression.replace(exp, str(ret))
        else:
            if exp.startswith('-'):
                sub_exp = re.split("-", exp)
                ret = -(float(sub_exp[1]) + float(sub_exp[2]))
            else:
                ret = float(exp.split("-")[0]) - float(exp.split("-")[1])
            new_exp = expression.replace(exp, str(ret))
        return plug_subtract_handler(new_exp)
    else:
        return expression


def compute(expression):
    expression = multiply_divide_handler(expression)
    expression = plug_subtract_handler(expression)
    return expression


def formatter(expression):
    return re.sub("\s*", "", expression)


def format_add_sub(string):
    string = string.replace('--', '+')
    string = string.replace('-+', '-')
    string = string.replace('+-', '-')
    string = string.replace('++', '+')
    return string

if __name__=="__main__":
    print(bracket_handler(cac))
    print(eval(cac))

