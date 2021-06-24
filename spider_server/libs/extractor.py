# -*- ecoding: utf-8 -*-
# @ModuleName: extractor
# @Author: jason
# @Email: jasonforjob@qq.com
# @Time: 2021/2/25 10:31
# @Desc:
import re

import json


def extract_ids(text, person_info=False):
    """
    extract all ids from texts<string>
    eg: extract_ids('my ids is 150404198812011101 m and dsdsd@dsdsd.com,李林的邮箱是eewewe@gmail.com哈哈哈')


    :param: raw_text
    :return: ids_list<list>
    """
    if text == '':
        return []

    WEIGHTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    IDCHECK = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

    AREA = {"11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古", "21": "辽宁", "22": "吉林", "23": "黑龙江",
            "31": "上海", "32": "江苏", "33": "浙江", "34": "安徽", "35": "福建", "36": "江西", "37": "山东", "41": "河南", "42": "湖北",
            "43": "湖南", "44": "广东", "45": "广西", "46": "海南", "50": "重庆", "51": "四川", "52": "贵州", "53": "云南", "54": "西藏",
            "61": "陕西", "62": "甘肃", "63": "青海", "64": "宁夏", "65": "新疆", "71": "台湾", "81": "香港", "82": "澳门", "91": "国外"}

    def check_id(id):
        # 检测身份证最后的校验码是否正确
        if len(id) != 18:
            return False
        else:
            ID_check = id[17]
            ID_aXw = 0
            for i in range(len(WEIGHTS)):
                ID_aXw = ID_aXw + int(id[i]) * WEIGHTS[i]
            ID_Check = ID_aXw % 11

            if ID_check != IDCHECK[ID_Check]:
                return False
            else:
                return True

    id_pattern = r'[1-9]\d{5}(?:18|19|(?:[23]\d))\d{2}(?:(?:0[1-9])|(?:10|11|12))(?:(?:[0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]'

    result = re.findall(id_pattern, text)
    data = []
    for id in result:
        if check_id(id):
            if person_info:
                birth = id[6:14]
                sex = id[16:17]
                sex = int(sex)
                area = AREA.get(id[0:2])
                data.append((id, area, birth, sex))
            else:
                data.append(id)
    return data





def extract_url(text, restr=''):
    pattern = re.compile(
        r'(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]',
        re.IGNORECASE)
    text = re.findall(pattern, restr, text)  # 去除网址
    return text


def extract_html(text, tag=None):
    """
    提取HTML标签 TODO 嵌套 bug
    :param text:
    :param tag:
    :return:
    """
    if tag:
        start_tag = tag
        end_tag = tag
    else:
        start_tag = '[A-Za-z]{1,}'
        end_tag = '[A-Za-z]{1,}'
    result = re.findall(f"<{start_tag}.*?>(.*)</{end_tag}>", text)  # 前后标签必须一样才能匹配
    return result


def extract_json(text):
    """
    TODO 简单提取json字符串
    :param text:
    :return:
    """
    result = re.findall(r'[{].*[}]', text)  # 最大匹配
    return result


def extract_json_to_dict(text):
    """
    提取json字符串并转成字典
    :param text:
    :return:
    """
    result = re.findall(r'[{].*[}]', text)  # 最大匹配
    try:
        result = json.loads(result[0])
    except Exception:
        return None
    return result


def most_common(content_list):
    """
    return the most common element in a list
    eg: extract_time(['王龙'，'王龙'，'李二狗'])


    :param: content_list<list>
    :return: name<string> eg: '王龙'
    """
    if content_list == []:
        return None
    if len(content_list) == 0:
        return None
    return max(set(content_list), key=content_list.count)


