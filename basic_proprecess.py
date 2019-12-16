import jieba
import json
import re
import os

operation = json.load(fp=open('dic/麻醉.json', encoding='utf-8'))
drug = json.load(fp=open('dic/用药.json', encoding='utf-8'))
examine = json.load(fp=open('dic/检查.json', encoding='utf-8'))
disease = json.load(fp=open('dic/诊断.json', encoding='utf-8'))
basic_inf = json.load(fp=open('dic/基本信息.json', encoding='utf-8'))
guanxi = json.load(fp=open('dic/其他.json', encoding='utf-8'))

cdm_name_map={
        "手术名称":"operation_name",
        "麻醉方式":"anesthesia_name",
        "药品名称":"drug_name",
        "用药途径":"route_source_value",
        "诊断类别":"diagnose_class_name",
        "诊断名称":"disease_name",
        "诊断类型":"diagnose_type_name",
        "检查名称":"examine_name",
        "检查类型":"et_concept_id",
        "仪器名称":"equipment_id",
        "检查方法":"em_source_value",
        "检验项目":"measurement_name",
        "检验标本":"specimen_name",
        "日期":"visit_start_datetime",
        "住院科室":"dept_name",
        "性别":"gender_name",
        "年龄":"age_years",
        "身高":"physical_exam_name",
        "体重":"physical_exam_name",
        "住院次数":"hospitalized_times",
        "检验结果":"value_source_value",
        "统计":"",
        "关系":"",
        "-":""
}

def is_num(x):
    try:
        float(x)
        return True
    except:
        return False

def identify_operation(word,dict_type,lexical_array):
    standard=dict()
    sub_standard=dict()
    lexical_length = len(lexical_array)
    for key, item_dict in dict_type.items():
        for subkey, values in item_dict.items():
            if word == subkey or word in values:
                sub_standard['usr_name']=word
                sub_standard['type']=key
                sub_standard['field']=cdm_name_map[key]
                standard[subkey]=sub_standard
    if len(standard)!=0:
        print(standard)
    return standard

def base_propress(seq_que):
    lexical_array = []
    dict_type=[operation,drug,examine,disease,basic_inf,guanxi]
    statistics_word = ['平均', '最大', '最小']  # 前置统计词后置预处理
    for i in range(len(seq_que)):  #如果jieba分词没有将例如“平均年龄”拆分开，则拆分成“平均 年龄”
        for x in statistics_word:
            index = seq_que[i].find(x)
            if index != -1 and seq_que[i] != x:
                seq_que.insert(i, seq_que[i][index+2:len(seq_que[i])])
                seq_que.insert(i, x)
                del seq_que[i + 2]
    for index, word in enumerate(seq_que):  # 获取下标和值
        transfer_flag = 0       # 单词识别完成标识
        # 识别Concept: 病人/医嘱详情/手术详情/化验详情/疾病详情
        if is_num(word):
            lexical_array.append(word)
        for d_type in dict_type:
            if transfer_flag == 0:
                lexical = identify_operation(word,d_type,lexical_array)
                if len(lexical) != 0:
                    lexical_array.append(list(lexical.keys())[0])
                    transfer_flag = 1
    return lexical_array