import re
import json

operation = json.load(fp=open('dic/麻醉.json', encoding='utf-8'))
drug = json.load(fp=open('dic/用药.json', encoding='utf-8'))
examine = json.load(fp=open('dic/检查.json', encoding='utf-8'))
measument = json.load(fp=open('dic/检验.json', encoding='utf-8'))
diagonal = json.load(fp=open('dic/诊断.json', encoding='utf-8'))
basic_inf = json.load(fp=open('dic/基本信息.json', encoding='utf-8'))
guanxi = json.load(fp=open('dic/其他.json', encoding='utf-8'))
filed_map = json.load(fp=open('dic/filed字段.json', encoding='utf-8'))
keshi = json.load(fp=open('dic/科室.json', encoding='utf-8'))
ind = json.load(fp=open('dic/ind.json', encoding='utf-8'))
logical = json.load(fp=open('dic/logical.json', encoding='utf-8'))
time = json.load(fp=open('dic/time.json', encoding='utf-8'))
opp = json.load(fp=open('dic/opp.json', encoding='utf-8'))



class Entity:
    field = ''
    value = ''
    operator = ''
    type = ''
    std_value = ''

    def __init__(self, field, value, operator,type,std_value):
        self.field = field
        self.value = value
        self.operator = operator
        self.type = type
        self.std_value = std_value

# class Timeindicator:

#判断是否为日期
def is_date(word):
    datetime_value = re.compile(r'\d{8}')
    try:
        return datetime_value.match(word)
    except:
        return False

def identify_datetime_value(index,word,seq_question,entitylist):

    #如果是时间
    if is_date(word):

        #判断后面是否还有时间，如果有则该词的operator是>
        if (index+2 < len(seq_question)) and (is_date(seq_question[index+2])):
            entitylist.append(Entity(field='',value=word,operator='大于',type='',std_value=word))

        #在判断前面是否有时间，如果有该词的operator是<
        elif (index >=2 ) and is_date(seq_question[index-2]):
            entitylist.append(Entity(field='', value=word, operator='小于', type='', std_value=word))

        #否则说明只有一个时间，判断是之前还是之后
        else:
            #取datetime后面一个词，判断是否为之前或者之后
            if index+1<len(seq_question):
                next_word = seq_question[index + 1]
                if next_word in ['之前', '前']:
                    entitylist.append(Entity(field='', value=word, operator='小于', type='', std_value=word))
                elif next_word in ['之后', '后']:
                    entitylist.append(Entity(field='', value=word, operator='大于', type='', std_value=word))
                else:
                    entitylist.append(Entity(field='', value=word, operator='等于', type='', std_value=word))

    #是时间且找到了operator返回1
        return 1

    #如果不是时间返回0
    else:
        return 0

#打印entitylist
def print_list(list):
    for obj in list:
        print(','.join(['%s:%s' % item for item in obj.__dict__.items()]))

#判断是否为数字
def is_num(x):
    try:
        float(x)
        return True
    except:
        return False

def identify_connection_op(index,word,seq_question,entitylist):
    #判断是否为连接词，首先应符合字典匹配，且前后都属数据或者日期类（避免 至 到这种不是连接词的情况）
    if word in ['-','~','至','到']:
        #拿到entitylist最后一个，是刚刚放进去的，如果这个词是连接词，则刚放进去的一定是数字或者日期类
        if (index>0) and index<len(seq_question)-1:
            last_word = seq_question[index - 1]
            next_word = seq_question[index + 1]
            # 如果前后都是数字：
            if is_num(last_word) and is_num(next_word):
                entitylist.append(Entity(field='', value=word, operator='', type='connection_op', std_value='-'))
                return 1
            #如果前后都是日期
            elif is_date(last_word) and is_date(next_word):
                entitylist.append(Entity(field='', value=word, operator='', type='connection_op', std_value='-'))
                return 1

    return 0




def identify_num(index,word,seq_question,entitylist):
    if is_num(word):
        #判断是否为A-B的中的A
        if index+2 < len(seq_question) and is_num(seq_question[index+2]) and identify_connection_op(index+1,seq_question[index+1],seq_question,entitylist):
            entitylist.append(Entity(field='',value=word,operator='大于',type='',std_value=word))
            return 1
        elif (index >=2 ) and is_num(seq_question[index-2]) and identify_connection_op(index-1,seq_question[index-1],seq_question,entitylist):
            entitylist.append(Entity(field='', value=word, operator='小于', type='', std_value=word))
            return 1
        else:
            #拿数字前面的一个词，看是否为大于，小于，拿数字后面的第一个词看是否为大 小
            if index>0:
                last_word = seq_question[index-1]
                if last_word in ['大于','>']:
                    entitylist.append(Entity(field='', value=word, operator='大于', type='', std_value=word))
                    return 1
                elif last_word in ['小于','<']:
                    entitylist.append(Entity(field='', value=word, operator='小于', type='', std_value=word))
                    return 1
                elif last_word in ['大于等于','>=']:
                    entitylist.append(Entity(field='', value=word, operator='大于等于', type='', std_value=word))
                    return 1
                elif last_word in ['小于等于','<=']:
                    entitylist.append(Entity(field='', value=word, operator='小于等于', type='', std_value=word))
                    return 1
            if index+1<len(seq_question):
                next_word = seq_question[index + 1]
                if next_word in ['大']:
                    entitylist.append(Entity(field='', value=word, operator='大于', type='', std_value=word))
                    return 1
                elif next_word in ['小']:
                    entitylist.append(Entity(field='', value=word, operator='小于', type='', std_value=word))
                    return 1

            #能执行到这里说明是数字，不是A-B类型且没有大于小于关系，就默认为等于
            entitylist.append(Entity(field='', value=word, operator='等于', type='', std_value=word))
            return 1
    else:
        return 0

#去json文件中找，只有一层迭代的函数,这种json的key是type，key对应数组的第一个词是std_value
# {
#     key1:[]
#     key2:[]
# }
#看下typestr是什么
def identify_json_one(word,entitylist,jsondata):
    for key,items in jsondata.items():
        if word == key or word in items:
            entitylist.append(Entity(field=key,value=word,operator='',type=key,std_value=items[0]))
            return 1
    return 0


#去json文件中找，有2层迭代的
# {
#     key1:{
#         key_1_1:[]
#         key_1_2:[]
#     }
#     key2:{
#         key_2_1: []
#         key_2_2: []
#     }
# }
def identify_json_two(word,entitylist,jsondata):
    for key, item in jsondata.items():
        for sub_key, sub_item in item.items():
            if (word == sub_key) or (word in sub_item):
                entitylist.append(Entity(field=filed_map[key], value=word, operator='等于', type=key, std_value=sub_key))
                return 1
    return 0

#去第一类json里面匹配并返回key值
def find_one_json_key(type,jsondata):
    for key,item in jsondata.items():
        if type == key or type in item:
            return key
    return None


#用于时间、数字类型通过后面的来判断他们具体类型
#对于时间，这里找的就是后面第一个能映射成时间的关系，再time.json中
#对于数字，这里找的就是后面第一个Ind，再Ind.json中
def find_next_Ind(index, entitylist,jsondata):
    while(index < len(entitylist)):
        entity = entitylist[index]
        key = find_one_json_key(entity.field,jsondata)
        if key is None:
            index = index + 1
            continue
        else:
            if key == "出院入院门诊时间":
                if entity.value == '出院':
                    return "出院时间",index
                elif entity.value == '门诊':
                    return "门诊时间",index
                else:
                    return "入院时间",index
            return key,index

    return None,None



def confirm_num_type(entitylist):
    index = 0
    length = 0
    length = len(entitylist)
    while index < length:
        entity = entitylist[index]
        #如果是时间类型，且type为null
        if is_date(entity.value) and entity.type == '':
            #如果前面存在IND且为TimeINd
            if index > 0 and (entitylist[index-1].type.find("TimeInd") > -1):
                #赋值类型,并删除该Ind
                entity.field = filed_map[entitylist[index-1].std_value]
                entity.type = entitylist[index-1].std_value
                del entitylist[index-1]
                #删除前面一个，当前的index减一
                index = index - 1
            #如果前面没有，找后面对应的关系是什么，确定时间类型
            else:
                key,index_of_next_Ind = find_next_Ind(index+1,entitylist,time)

                print(key)
                entity.field = filed_map[key]
                entity.type = key

        #如果是数字且type为null
        #再找数字和年份的类型时，都默认如果前面有一个能够指示他的ind，那么就一定紧挨着它前面，但是后面的不一定紧挨着
        elif is_num(entity.value) and entity.type == '':
            #找前面一个词
            if index > 0:
                last_entity = entitylist[index-1]
                type = ""
                #如果前面一个词是检验指标类型，则该项目就是检验结果
                if last_entity.field == filed_map["检验指标"]:
                    type = "检验指标"
                elif last_entity.field == filed_map["检查指标"]:
                    type = "检查指标"
                #是否为年龄指标
                elif (last_entity.type == "ageInd"):
                    type = "年龄"
                    del entitylist[index-1]
                    index = index - 1
                elif (last_entity.type == "weightInd"):
                    type = "体重"
                    del entitylist[index-1]
                    index = index - 1
                elif (last_entity.type == "lenthInd"):
                    type = "身高"
                    del entitylist[index-1]
                    index = index - 1
                elif (last_entity.type == "zhuyuancishuInd"):
                    type = "住院次数"
                    del entitylist[index-1]
                    index = index - 1

                #如果前面有ind可以确定则给出type和field
                if type != "":
                    entity.field = filed_map[type]
                    entity.type = type

            #找后面一个ind词
            next_Ind,index_of_next_Ind = find_next_Ind(index+1,entitylist,ind)
            if next_Ind is not None:
                #如果后面时ageInd且wordType为空，则赋值，删除
                if (next_Ind == "ageInd"):
                    if entity.type == "":
                        entity.type = "年龄"
                        entity.field = filed_map[entity.type]
                    if entity.type == "年龄":
                        del entitylist[index_of_next_Ind]
                elif (next_Ind == "weightInd"):
                    if entity.type == "":
                        entity.type = "体重"
                        entity.field = filed_map[entity.type]
                    if entity.type == "体重":
                        del entitylist[index_of_next_Ind]
                elif (next_Ind == "lenthInd"):
                    if entity.type == "":
                        entity.type = "身高"
                        entity.field = filed_map[entity.type]
                    if entity.type == "身高":
                        del entitylist[index_of_next_Ind]
                elif (next_Ind == "zhuyuancishuInd"):
                    if entity.type == "":
                        entity.type = "住院次数"
                        entity.field = filed_map[entity.type]
                    if entity.type == "住院次数":
                        del entitylist[index_of_next_Ind]

        #如果时time或这数字类型，且时A-B型，改一下后面的
        if (is_date(entity.value) or is_num(entity.value)) and (index + 2) < len(entitylist):
            # 如果是A-B类型的，给后面那个时间或数字赋值
            next_entity = entitylist[index + 1]
            next_next_entity = entitylist[index + 2]
            if next_entity.type == 'connection_op' and (
                    is_date(next_next_entity.value) or is_num(next_next_entity.value)):
                next_next_entity.field = entity.field
                next_next_entity.type = entity.type
                #删除中间的间隔符
                del entitylist[index+1]
        index = index + 1
        length = len(entitylist)

    return entitylist

def print_logical_form(entitylist):
    line = ""
    for entity in entitylist:
        if entity.field in ['or','and','not']:
            line = line + "," + entity.type
        else:
            line = line + "," + entity.type + entity.operator + entity.std_value
    print(line[1:])


def add_and_logical(entitylist):
    index = 0
    length = len(entitylist)

    while index < length:
        entity = entitylist[index]
        #查看每一个非logical词，如果他后面不是一个logical词就添加and
        if entity.field not in ['or','and','not']:
            #如果后面有词，且后面那个词不是or和and，就添加一个
            if (index + 1 < length) and (entitylist[index+1].type != 'or') and (entitylist[index+1].type != 'and'):
                entitylist.insert(index+1,Entity(field='and',value='and',operator='',type='and',std_value='且'))
        index = index + 1
        length = len(entitylist)
    return entitylist

#给一个entity的operator取反
def operator_opp(entity):
    for opp_operator,now_operator in opp.items():
        if entity.operator == now_operator:
            entity.operator = opp_operator
            return opp_operator

def not_to_operator(entitylist):
    #找到每一个not，获得not判断后面有没有相同类型的且后面的相同类型前面没有not的，也给它not
    index = 0
    length = len(entitylist)
    while index < length:
        entity = entitylist[index]

        #只有not才可以进来
        if entity.type == "not":
            #取下一个entity，修改operator取反
            entitylist[index + 1].operator = operator_opp(entitylist[index + 1])

            #找后面同类型的词，并修改operator
            type = entitylist[index + 1].type
            startindex = index + 2
            startlength = len(entitylist)
            while startindex < startlength:
                if entitylist[startindex].field not in ['or','and','not']:
                    if entitylist[startindex].type != type:
                        break

                    if entitylist[startindex-1].type != 'not':
                        entitylist[startindex].operator = operator_opp(entitylist[startindex])
                startindex = startindex + 1
                startlength = len(entitylist)

            #删除该not
            del entitylist[index]

        index = index + 1
        length = len(entitylist)
    return entitylist

def recurrence(entitylist):
    #如果entitylist的长度为1，则返回该entity，作为递归的一部分出口
    if len(entitylist) == 1:
        return entitylist[0]

    #如果不止一个元素，遍历entitylist找or节点
    index = 0
    length = len(entitylist)
    while index < length:
        entity = entitylist[index]
        #如果是or节点
        if entity.field == 'or':
            #取or左边的节点
            or_left = entitylist[index - 1]
            left_type = or_left.type

            orlist = []
            #向后遍历，or节点且or后面是同样type的，一旦不满足立即退出
            orindex = index
            #如果越界，且是or且下一个type相同
            while orindex < length and entitylist[orindex].field == 'or' and entitylist[orindex+1].type == left_type:
                orlist.append(entitylist[orindex+1])
                orindex = orindex + 2

            #看orlist是否为空
            #如果orlist不为空，说明存在服用A或B或C这种情况，创建一个or节点，将orlist中的entity全部放进去,并且删除这些entity和or
            if orlist != []:
                #不要忘记加上最原始的那个节点
                orlist.append(or_left)
                orentity = Entity(field='logicalor',value=orlist,type='',std_value='',operator='')
                #删除连续的entity和or，第一个entity的index为index-1，结束的entity的下表是orindex-1，删除index-1位置一共（orindex-index次）
                for _ in range(orindex-index+1):
                    del entitylist[index-1]
                #再index那个地方插入新的元素
                entitylist.insert(index-1,orentity)

            #如果list为空，说明该or是一个分隔节点，生成一个or节点，左右list进入递归，该or节点中只有两个元素
            else:
                left_entitylist = entitylist[0:index]
                right_entitylist = entitylist[index+1:]
                or_left_entity = recurrence(left_entitylist)
                or_rithe_entity = recurrence(right_entitylist)
                orentity = Entity(field='logicalor',value=[or_left_entity,or_rithe_entity],type='',std_value='',operator='')
                return orentity
        index = index + 1
        length = len(entitylist)


    #循环完了一定没有or节点了
    addentity = Entity(field='logicaland',value=[],type='',std_value='',operator='')
    for items in entitylist:
        if items.field not in ['or','and']:
            addentity.value.append(items)

    return addentity



# 创建树的方法
def createTree(entitylist):
    #提取出时间、身高、体重、年龄节点
    index = 0
    length = len(entitylist)
    rootentity = Entity(field='logicaland', value=[],type='',std_value='',operator='')
    # while index < length:
    #     entity = entitylist[index]
    #     if entity.field in ["visit_start_datetime","visit_end_datetime","visit_start_datetime","examine_datetime",
    #                        "measurement_datetime","operation_start_datetime","de_start_datetime","diagnose_datetime","age_years",
    #                        "gender_name","physical_exam_name","physical_exam_name","diagnose_class_name"]:
    #         #判断是第一个条件，还是最后一个条件，还是中间条件。这里默认一个规则:这些词周围都是and关系
    #         rootentity.value.append(entitylist[index])
    #         #如果该实体是第一个实体
    #         if index == 0:
    #             #删除该节点和后面的and节点
    #             del entitylist[index]
    #             del entitylist[index]
    #             #index不改，但是length需要实时更新
    #             length = len(entitylist)
    #             continue
    #         #如果是最后一个节点
    #         elif index == length - 1:
    #             #删除该节点和它前面的节点
    #             del entitylist[len(entitylist)-1]
    #             del entitylist[len(entitylist)-1]
    #
    #         else:
    #             #删除该词和该词后面的那个
    #             del entitylist[index]
    #             del entitylist[index]
    #             # index不改，但是length需要实时更新
    #             length = len(entitylist)
    #             continue
    #     index = index + 1
    #     length = len(entitylist)
    print("//*/*/*/*/*/")
    print_logical_form(entitylist)
    #让剩下的entitylist去递归，返回一个entity加入and
    #但是之前定义的rootentity可能为空，如果为空，rootentity就是递归返回的，如果不为空，递归返回的就是rootentity中value中的一个值
    if rootentity.value == []:
        rootentity = recurrence(entitylist)
    else:
        #如果字串放进去返回是一个大的and节点，可以直接把返回and的value拼接在大的root节点的value里面
        sub = recurrence(entitylist)
        if sub.field == 'logicaland':
            rootentity.value = rootentity.value + sub.value
        else:
            rootentity.value.append(sub)

    return rootentity


def print_tree(node):
    line = ''
    line = node.field[7:] + '('
    for items in node.value:
        if items.field in ['logicalor', 'logicaland']:
            logicalline = print_tree(items)
            line = line + ',' + logicalline
        else:
            line = line + ',' + items.type + items.operator + items.std_value
    line = line + ')'
    return (line.replace("(,","("))



def extraction(seq_question):
    entitylist = []
    for index,word in enumerate(seq_question):
        transfer_flag = 0
        #判断是否为时间
        transfer_flag = identify_datetime_value(index,word,seq_question,entitylist)

        #判断是否为连接符符
        if transfer_flag == 0:
            transfer_flag = identify_connection_op(index,word,seq_question,entitylist)

        #判断是否为数字
        if transfer_flag == 0:
            transfer_flag = identify_num(index,word,seq_question,entitylist)

        #判断是否为手术大类
        if transfer_flag == 0:
            transfer_flag = identify_json_two(word,entitylist,operation)

        #判断是否为用药大类
        if transfer_flag == 0:
            transfer_flag = identify_json_two(word,entitylist,drug)

        #判断是否为诊断大类
        if transfer_flag == 0:
            transfer_flag = identify_json_two(word,entitylist,diagonal)

        #判断是否为检验大类
        if transfer_flag == 0:
            transfer_flag = identify_json_two(word,entitylist,measument)

        #判断是否为检查大类
        if transfer_flag == 0:
            transfer_flag = identify_json_two(word,entitylist,examine)

        #判断是否为基本信息大类
        if transfer_flag == 0:
            transfer_flag = identify_json_two(word,entitylist,basic_inf)

        #判断是否为科室
        if transfer_flag == 0:
            transfer_flag = identify_json_two(word,entitylist,keshi)

        #检验是否为身高、体重、年龄、时间提示词
        if transfer_flag == 0:
            transfer_flag = identify_json_one(word,entitylist,ind)

        #检验是否为逻辑词
        if transfer_flag == 0:
            transfer_flag = identify_json_one(word,entitylist,logical)

    print_list(entitylist)
    print("**********************************")

    #进行第二遍筛选，确定数字的类型，删除多余词，只保留有field字段的值
    entitylist = confirm_num_type(entitylist)
    print_list(entitylist)
    print("**********************************")
    print_logical_form(entitylist)
    print("**********************************")
    #添加and关系
    entitylist = add_and_logical(entitylist)
    print_logical_form(entitylist)

    #合并not关系
    entitylist = not_to_operator(entitylist)
    print_logical_form(entitylist)
    
    rootentity = createTree(entitylist)
    line = print_tree(rootentity)
    print(line)
    return