import flask
import json 
import uuid
import ESconn
import scores
import elasticsearch
import sys
import time

import requests

def questionid():
    s_uuid=str(uuid.uuid4())
    l_uuid=s_uuid.split('-')
    s_uuid=''.join(l_uuid)
    return s_uuid

server = flask.Flask(__name__)
# flask_cors.CORS(server)

@server.route('/test', methods = ['get'])
def test():
    res = {'msg':'这是一个消息', 'msg_code':0}
    return json.dumps(res, ensure_ascii=False)

# #问答
# @server.route('/qaa', methods = ['post'])
# def qaa_service():
#     uid = questionid()

#     insertValues = flask.request.get_json()
#     x1=insertValues['question']
#     x2=insertValues['userId']
#     x3=insertValues['qaaId']
#     x4=insertValues['answerMax']
#     x5=insertValues['modelId']
#     x6=insertValues['product']

#     if x3 == 0:
#         index = "ehome_smart_qaa_total"
#     elif x3 ==1:
#         index = "ehome_smart_qaa_cs"
#     elif x3 ==2:
#         index = "ehome_smart_qaa_mc"
#     elif x3 ==3:
#         index = "ehome_smart_qaa_bt"
#     elif x3 ==4:
#         index = "ehome_smart_qaa_hr"
#     elif x3 ==5:
#         index = "ehome_smart_qaa_po"
#     elif x3 == 6:
#         index = "ehome_smart_qaa_app"

#     log_content = ''

#     q1000 = ESconn.search1000(x1, index, "question")

#     #排序
#     higher50 = []
#     nselected = []

#     toSort = {}
    
#     qsegs = scores.segment(x1)
    
#     for hit in q1000['hits']['hits']:
#         nselected.append(hit['_source'])
        
#         hsegs = scores.segment(hit['_source']['question'])
#         kscores = hit['_score']
#         for i in qsegs:
#             if i in hsegs:
#                 kscores = kscores + 7

#         qakey = '{问：'+ hit['_source']['question'] + ',' + '答：' + hit['_source']['answer'] + '}'
#         toSort[qakey] = kscores 

#         if kscores >= 25:
#             higher50.append(hit['_source'])

#     sorted_by_value = dict(sorted(toSort.items(), key=lambda item: item[1], reverse=True)[:50])
#     keylist = list(sorted_by_value.keys())
#     qaset = str(keylist)
#     toLLM = scores.formPrompt(x1,qaset)
            
#     if len(higher50) != 0:

#         qscore = scores.keyScores(higher50, qsegs)
    
#         best_index = scores.getmatch(qscore)
    
#         rest = higher50[best_index]
        
#         nselected.remove(rest)

#     related = []
#     keyword_ans = []
#     if len(nselected) == 0:
#         related = []
#         keyword_ans = []
#     # elif len(nselected) == 0:
#     #     related = []
#     #     keyword_ans = []
#     elif len(nselected) < 6:
#         for i in range(0,len(nselected)):
#             temp = {}
#             temp['question'] = nselected[i]['question']
#             temp['questionId'] = nselected[i]['id']
#             related.append(temp)
            
#             keyword_ans.append(temp['question'])
#     else:
#         for i in range(0,5):
#             temp = {}
#             temp['question'] = nselected[i]['question']
#             temp['questionId'] = nselected[i]['id']
#             related.append(temp)
            
#             keyword_ans.append(temp['question'])

#     # #反问
#     # backq = scores.AskBack(q1000, x1)
#     # if len(backq) > 0 :
#     #     log_content = log_content + 'covered, ask back\n'
#     #     res = ''
#     #     ans = ''

#     #     if len(backq) == 1:
#     #         ans = ans + backq[0]['answer']

#     #     else:
#     #         ans = ans + "根据您输入的关键词，小e找到了下面这些问题，请问您是要问这些问题吗:<br />" 
#     #         for i in backq:
#     #             ans = ans + i['question'] + '<br />'

#     #     res = {
#     #         "code": "0",
#     #         "msg": "操作成功",
#     #         "data": {
#     #             "total":1,
#     #             "result":[{
#     #                 "question": "根据您输入的关键词，小e找到了下面这些问题",
#     #                 "answer":  ans,
#     #                 "related":related,
#     #                 "ext": None
#     #             }],
#     #             "logId": uid
#     #         },
#     #         "LLM":"N"
#     #     }
#     #     return json.dumps(res, ensure_ascii=False)
#     # else:
#     url = "http://192.168.24.137:30123/open-api/oneapi/v1/chat/completions"
#     api_key = "sk-JyubfGLXR4nbxkL3C801Cc1c61F743749e40Ac1688Af870c"
#     headers = {
#         "Authorization": f"Bearer {api_key}",  # API key in the Authorization header
#         "Content-Type": "application/json"  # Specify the content type
#     }

#     payload = {
#         "messages":[{
#             "role":"user",
#             "content":toLLM
#         }],
#         "model":"deepseek-r1-distill",
#         "stream":True
#     }

#     response = requests.post(url, json=payload, headers=headers)

#     return flask.Response(scores.streamout(response, x1, related, uid), content_type='text/event-stream')
        
#         # if response.status_code == 200:
#         #     print("Message sent successfully!")

#         #     tempres = response.json()
#         #     contpart = tempres['choices'][0]['message']['content']
#         #     offthink = contpart.split('</think>\n',1)
#         #     rest = offthink[1]
            
#         #     res = {
#         #         "code": "0",
#         #         "msg": "操作成功",
#         #         "data": {
#         #             "total":1,
#         #             "result":[{
#         #                 "question": x1,
#         #                 "answer": rest,
#         #                 "related":related,
#         #                 "ext": None
#         #             }],
#         #             "logId": uid
#         #         },
#         #         "LLM":"Y"
#         #     }
#         # else:
#         #     print("Failed to send message.")
#         #     print("Status Code:", response.status_code)
#         #     print("Response:", response.text)


#         # if len(x1) <= 3 and len(keyword_ans) > 0:
#         #     answer = ''
#         #     for i in range(0, len(keyword_ans)):
#         #         answer = answer + '问题' + str(i+1) + ':' + str(keyword_ans[i]) + '<br />'
#         #     res = {
#         #         "code": "0",
#         #         "msg": "操作成功",
#         #         "data": {
#         #             "total":1,
#         #             "result":[{
#         #                 "question": "根据您输入的关键词，小e找到了下面这些问题",
#         #                 "answer": "根据您输入的关键词，小e找到了下面这些问题:<br />" + answer,
#         #                 "related":related,
#         #                 "ext": None
#         #             }],
#         #             "logId": uid
#         #         }
#         #     }
            
#         # elif len(x1) <= 3 and len(keyword_ans) == 0:
#         #     res = {
#         #         "code": "0",
#         #         "msg": "操作成功",
#         #         "data": {
#         #             "total":1,
#         #             "result":[{
#         #                 "question": "小e没能找到相关问题",
#         #                 "answer": '根据您输入的关键词，小e没能找到相关问题，请提供更多信息',
#         #                 "related":related,
#         #                 "ext": None
#         #             }],
#         #             "logId": uid
#         #         }
#         #     }

#         # elif len(x1) > 3 and len(higher50) == 0:
#         #     res = {
#         #         "code": "0",
#         #         "msg": "操作成功",
#         #         "data": {
#         #             "total":1,
#         #             "result":[{
#         #                 "question": "小e目前还没有学到您输入的问题",
#         #                 "answer": "抱歉，小e没能完全理解您的意思，或者我还没学习到您的问题",
#         #                 "related":related,
#         #                 "ext": None
#         #             }],
#         #             "logId": uid
#         #         }
#         #     }
#         # else:

#         #     res = {
#         #         "code": "0",
#         #         "msg": "操作成功",
#         #         "data": {
#         #             "total":1,
#         #             "result":[{
#         #                 "question": rest['question'],
#         #                 "answer": rest['answer'],
#         #                 "related":related,
#         #                 "ext": None
#         #             }],
#         #             "logId": uid
#         #         }
#         #     }


    
#     if len(q1000['hits']['hits']) != 0:

#         cur = time.localtime()
#         log_content = log_content + str(time.asctime(cur)) + '\n'
#         log_content = log_content + index + '\n'
#         log_content = log_content +'userid:'+ x2 + '\n'
#         log_content = log_content + 'question:'+ x1 + '\n'
#         log_content = log_content + 'highest question ' + str(q1000['hits']['hits'][0]['_source']['question'])+ '\n'
#         log_content = log_content + 'highest score ' + str(q1000['hits']['hits'][0]['_score'])+ '\n'
#         log_content = log_content + '##########################'+ '\n'
#         print(log_content, file = sys.stderr)
#     else:
#         cur = time.localtime()
#         log_content = log_content + str(time.asctime(cur)) + '\n'
#         log_content = log_content + index + '\n'
#         log_content = log_content +'userid:'+ x2 + '\n'
#         log_content = log_content + 'question:'+ x1 + '\n'
#         log_content = log_content + 'highest question' + ' None'+ '\n'
#         log_content = log_content + 'highest score' + ' None' + '\n'
#         log_content = log_content + '##########################'+ '\n'
#         print(log_content, file = sys.stderr)

#     with open('/data/ehome/logs.txt', 'a') as file:
#         file.write(log_content)

#     # return json.dumps(res, ensure_ascii=False)

#问题列表
@server.route('/qlist', methods = ['post'])
def qlist_service():
    uid = questionid()

    insertValues = flask.request.get_json()
    x1=insertValues['userId']
    x2=insertValues['qaaId']
    x3=insertValues['pageNumber']
    x4=insertValues['modelId']
    x5=insertValues['product']

    qaaId = int(x2)

    if qaaId == 0:
        index = "ehome_smart_qaa_total"
    elif qaaId ==1:
        index = "ehome_smart_qaa_cs"
    elif qaaId ==2:
        index = "ehome_smart_qaa_mc"
    elif qaaId ==3:
        index = "ehome_smart_qaa_bt"
    elif qaaId ==4:
        index = "ehome_smart_qaa_hr"
    elif qaaId ==5:
        index = "ehome_smart_qaa_po"
    elif qaaId == 6:
        index = "ehome_smart_qaa_app"
    elif qaaId == 8:
        index = 'ehome_smart_qaa_fa'

    qdicts = ESconn.searchPage(index, x3)

    reslist = []
    if len(qdicts) == 0:
        reslist = []
    else:
        for i in range(0,len(qdicts)):
            tempQ = {}
            tempQ['question'] = qdicts[i]['question']
            tempQ['questionId'] = qdicts[i]['id']
            tempQ["ext"]= None
            reslist.append(tempQ)

    res = {
        "code": "0",
        "msg": "操作成功",
        "data": {
            "total":len(reslist),
            "result":reslist,
            "logId": uid
        }
    }
    return json.dumps(res, ensure_ascii=False)

#指定问题
@server.route('/ans', methods = ['post'])
def ans_service():
    uid = questionid()

    insertValues = flask.request.get_json()
    x1=insertValues['userId']
    x2=insertValues['qaaId']
    x3=insertValues['pageNumber']
    x4=insertValues['keyword']
    x5=insertValues['modelId']
    x6=insertValues['product']
    x7=insertValues['questionId']
    x8=insertValues['question']

    qaaId = int(x2)

    if qaaId == 0:
        index = "ehome_smart_qaa_total"
    elif qaaId ==1:
        index = "ehome_smart_qaa_cs"
    elif qaaId ==2:
        index = "ehome_smart_qaa_mc"
    elif qaaId ==3:
        index = "ehome_smart_qaa_bt"
    elif qaaId ==4:
        index = "ehome_smart_qaa_hr"
    elif qaaId ==5:
        index = "ehome_smart_qaa_po"
    elif qaaId == 6:
        index = "ehome_smart_qaa_app"
    elif qaaId == 8:
        index = 'ehome_smart_qaa_fa'

    
    qdicts = ESconn.searchPoint(x7, index)
    q1000 = ESconn.search1000(x8, index, "question")
    related = []
    if len(q1000['hits']['hits']) == 0:
        related = []
    elif len(q1000['hits']['hits']) > 0 and len(q1000['hits']['hits']) < 6:
        for i in range(0, len(q1000['hits']['hits'])):
            temp = {}
            temp['question'] = q1000['hits']['hits'][i]['_source']['question']
            temp['questionId'] = q1000['hits']['hits'][i]['_source']['id']
            related.append(temp)
    else:
        for i in range(1,6):
            temp = {}
            print(i, file = sys.stderr)
            temp['question'] = q1000['hits']['hits'][i]['_source']['question']
            temp['questionId'] = q1000['hits']['hits'][i]['_source']['id']
            related.append(temp)

    res = {
        "code": "0",
        "msg": "操作成功",
        "data": {
            "total":1,
            "result":[{
                "question": qdicts[0]['question'],
                "answer":qdicts[0]["answer"],
                "related":related,
                "ext": None
            }],
            "logId": uid
        }
    }
    return json.dumps(res, ensure_ascii=False)

#问题搜索
# @server.route('/ans', methods = ['post'])
@server.route('/qsearch', methods = ['post'])
def qsearch_service():
    uid = questionid()

    insertValues = flask.request.get_json()
    x1=insertValues['keyword']
    x2=insertValues['userId']
    x3=insertValues['qaaId']
    x4=insertValues['answerMax']
    x5=insertValues['pageNumber']
    x6=insertValues['modelId']
    x7=insertValues['product']

    qaaId = int(x3)

    if qaaId == 0:
        index = "ehome_smart_qaa_total"
    elif qaaId ==1:
        index = "ehome_smart_qaa_cs"
    elif qaaId ==2:
        index = "ehome_smart_qaa_mc"
    elif qaaId ==3:
        index = "ehome_smart_qaa_bt"
    elif qaaId ==4:
        index = "ehome_smart_qaa_hr"
    elif qaaId ==5:
        index = "ehome_smart_qaa_po"
    elif qaaId == 6:
        index = "ehome_smart_qaa_app"
    elif qaaId == 8:
        index = 'ehome_smart_qaa_fa'

    qdicts = ESconn.searchKey(index, x1, x5, x4)
    reslist = []

    if len(qdicts) == 0:
        tempQ = {}
        tempQ['question'] = "未能检索到与您的输入匹配的问题，请重新输入"
        tempQ['questionId'] = None
        tempQ['ext'] = None

        reslist.append(tempQ)
    elif len(qdicts) >= x4:
        for i in range(0, x4):
            tempQ = {}
            tempQ['question'] = qdicts[i]['question']
            tempQ['questionId'] = qdicts[i]['id']
            tempQ['ext'] = None
            reslist.append(tempQ)
    else:
        for i in range(0, len(qdicts)):
            tempQ = {}
            tempQ['question'] = qdicts[i]['question']
            tempQ['questionId'] = qdicts[i]['id']
            tempQ['ext'] = None
            reslist.append(tempQ)

    res = {
        "code": "0",
        "msg": "操作成功",
        "data": {
            "total":1,
            "result":reslist,
            # "result":[{
            #     "question": reslist,
            #     # "answer": "申万宏源e家APP使用员工统一身份认证平台账号和密码登录",
            #     "ext": None
            # }],
            "logId": uid
        }
    }
    return json.dumps(res, ensure_ascii=False)

@server.route('/qedit', methods = ['post'])
def edit_service():
    uid = questionid()

    insertValues = flask.request.get_json()
    dataset = insertValues['data']

    es = elasticsearch.Elasticsearch(
        # hosts = ['http://172.17.172.149:9200'],
        # basic_auth = ('es2_zntj', 'Zzty240603!@#')
        hosts=['http://192.168.152.47:9292'],
        basic_auth=('ai', 'Aireccontent@123')
        )
    
    
    builactions = []
    
    bulkactions = []
    
    cur = time.localtime()
    
    for i in dataset:
        if i['orderId'] == 'Add' or i['orderId'] == 'Edit':
        
        
        ########向total添加###########
            index = ESconn.createIndex(i['questionId'], "ehome_smart_qaa_total")
            builactions.append(index)

            insertv = {}

            insertv['id'] = i['questionId']
            insertv['firstLevelDirectory'] = i['firstLevelDirectory']
            insertv['secondLevelDirectory'] = i['secondLevelDirectory']
            insertv['thirdLevelDirectory'] = i['thirdLevelDirectory']
            insertv['question'] = i['question']
            insertv['answer'] = i['answer']
            insertv['keyword'] = i['keyword']
            insertv['hot'] = 0
            insertv["updateTime"] =str(time.asctime(cur))
            # insertv['updateTime'] = i['updateTime']
            insertv["searhShow"] = "1"
            insertv["modelId"] = "1"
            insertv["extendIssues"] = []
            insertv["showScope"] = "2"
            insertv["auditStatus"] =  "2"
            insertv["question_embedding"] =ESconn.embeddingMsg(i['question'])
        

            builactions.append(insertv)
        
            response=es.bulk(body = builactions)

            ####################
            if i["qaaId"] == 0:
            # 0：无分类
                res = {
                "code": "0",
                "msg": "操作成功"}
            # elif i["qaaId"] == "1":
            # # 1：客服中心
            # elif i["qaaId"] == "2":
            # # 2：运营中心
            
            # 3：商旅
            elif i["qaaId"] == "3":
                index = ESconn.createIndex(i['questionId'], "ehome_smart_qaa_bt")
                bulkactions.append(index)
                bulkactions.append(insertv)
                response=es.bulk(body = bulkactions)

                res = {
                "code": "0",
                "msg": "操作成功"}
            # 4：人力
            elif i["qaaId"] == 4:
                index = ESconn.createIndex(i['questionId'], "ehome_smart_qaa_hr")
                bulkactions.append(index)
                bulkactions.append(insertv)
                response=es.bulk(body = bulkactions)

                res = {
                "code": "0",
                "msg": "操作成功"}
            # 5：党办
            elif i["qaaId"] == 5:
                index = ESconn.createIndex(i['questionId'], "ehome_smart_qaa_po")
                bulkactions.append(index)
                bulkactions.append(insertv)
                response=es.bulk(body = bulkactions)

                res = {
                "code": "0",
                "msg": "操作成功"}
            elif i["qaaId"] == 6:
                index = ESconn.createIndex(i['questionId'], "ehome_smart_qaa_app")
                bulkactions.append(index)
                bulkactions.append(insertv)
                response=es.bulk(body = bulkactions)

                res = {
                "code": "0",
                "msg": "操作成功"}
            #财务
            elif i["qaaId"] == 8:
                index = ESconn.createIndex(i['questionId'], "ehome_smart_qaa_fa")
                bulkactions.append(index)
                bulkactions.append(insertv)
                response=es.bulk(body = bulkactions)

                res = {
                "code": "0",
                "msg": "操作成功"}

            else:
                res = {
                "code": "1",
                "msg": "操作失败，qaaId错误"}

        else:
            res = {
                "code": "1",
                "msg": "操作失败，orderId错误"}

    return json.dumps(res, ensure_ascii=False)
    

# if __name__ == "__main__":
server.run(host= '0.0.0.0', port=8521, debug=True)