# -*- ecoding: utf-8 -*-
# @ModuleName: city_code.txt
# @Author: jason
# @Email: jasonforjob@qq.com
# @Time: 2021/4/17 14:53
# @Desc:

def get_cityCode():
    # 2018年8月中华人民共和国县以上行政区划代码
    item = {}
    with open('../src/city_code.txt','r',encoding='utf-8') as f1:
        for row in f1.readlines():
            row =row.strip()
            code,city=row.split('\t')
            item[code]=city
    return item

if __name__ == '__main__':

    print(get_cityCode())