import jieba
import relation
import re

from basic_proprecess import base_propress

"""对question进行预处理
1: 非标准时间(2017年1月11日) --> 标准时间格式(201701011)
2:
"""
def preprocess(question):
    print('预处理前:' + question)
    question = question.strip(' ')
    datetime_pattern = re.compile('(([12][0-9]{3})[年|/|\-|\.]?([01]?[0-9](?=\D))?[月|/|\-|\.]?([0-3]?[0-9](?=\D))?[日|号]?)')
    tuples = datetime_pattern.findall(question)
    for i in range(len(tuples)):
        date = ''
        for j in range(len(tuples[i])):
            if j == 0:
                continue
            # 月日，如果是0-9，补0.例如，9-》09
            if (j == 2 or j == 3) and len(tuples[i][j]) == 1:
                date = date + ('0' + tuples[i][j])
            # 如果月日为空，补00
            elif len(tuples[i][j]) == 0:
                date = date + '00'
            else:
                date = date + tuples[i][j]
        # date = '[' + date + ']'
        str = tuples[i][0]
        if str[-1] == '-':
            str = str[0:len(tuples[i][0])-1]
        question = question.replace(str, date)
    print('预处理后:' + question)
    return question

def remove_stopwords(seq_que):
    stop_words_list = ['为', '了', '的', '在', '之间', '中', '做', '做了', "那些", "多少", "什么",
                       "?", "？", "过", "有","，","。"]
    seq_stopwords = []
    for word in seq_que:
        if word in stop_words_list:
            seq_stopwords.append(word)
    for item in seq_stopwords:
        seq_que.remove(item)
    return seq_que

def parsing(question):
    print("输入问题：" + question)
    print("***************************")

    #预处理时间
    pre_question = preprocess(question)

    #jieba分词
    jieba.load_userdict('dic/jiebadic')
    seq_question = list(jieba.cut(pre_question))
    print("分词结果" + str(seq_question))
    print("****************************")

    #去停用词
    seq_question = remove_stopwords(seq_question)
    print("去停用词分词结果" + str(seq_question))
    print("****************************")

    #关系抽取
    relation.extraction(seq_question)





#药 葡萄糖 氯化钠 水合氯醛
#用药方式 肛塞
#检查 B超检查
#科室 外科
#疾病 急性肾盂肾炎 肝脏功能异常
#检验指标 淋巴细胞数
#手术 "输尿管膀胱吻合术" "腹腔镜检查


question = "2018-2019期间没有患有肝脏功能异常疾病或急性肾盂肾炎的身高为180cm体重大于50kg的女病人"
parsing(question)
