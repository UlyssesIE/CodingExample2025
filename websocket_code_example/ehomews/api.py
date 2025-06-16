from fastapi import FastAPI,WebSocket
import json
from datetime import datetime
import threading
import httpx
import ESconn
import scores

import sys

import config
# import ehome_service
from request_model import chat_request,ws_chat_request
import uuid

def questionid():
    s_uuid=str(uuid.uuid4())
    l_uuid=s_uuid.split('-')
    s_uuid=''.join(l_uuid)
    return s_uuid

def get_chat_request_data(chat_request):
    if chat_request.kbName==1:
        kb_name=config.kb_name_dict[1]
    elif chat_request.kbName==2:
        kb_name=chat_request.userId
    else:
        kb_name=chat_request.kbName
    if chat_request.history==None and chat_request.kbName==None:
        data = {
            "query": chat_request.question,
            "conversation_id": "",
            "history_len": chat_request.history_len,
            "stream": chat_request.stream,
            "model_name": chat_request.model_name,
            "temperature": chat_request.temperature,
            "max_tokens": chat_request.max_tokens,
            "prompt_name": chat_request.prompt_name
        }
    elif chat_request.history==None and chat_request.kbName!=None:
        data = {
            "query": chat_request.question,
            "knowledge_base_name":kb_name,
            "top_k":chat_request.top_k,
            "stream": chat_request.stream,
            "model_name": chat_request.model_name,
            "temperature": chat_request.temperature,
            "max_tokens": chat_request.max_tokens,
            "prompt_name": chat_request.prompt_name,
            "file_name": chat_request.fileName
        }
    elif chat_request.history!=None and chat_request.kbName==None:
        data = {
            "query": chat_request.question,
            # "conversation_id": "",
            "history": chat_request.history,
            "history_len": chat_request.history_len,
            "stream": chat_request.stream,
            "model_name": chat_request.model_name,
            "temperature": chat_request.temperature,
            "max_tokens": chat_request.max_tokens,
            "prompt_name": chat_request.prompt_name
        }
    else:
        data = {
            "query": chat_request.question,
            "knowledge_base_name": kb_name,
            "top_k": chat_request.top_k,
            "history": chat_request.history,
            "stream": chat_request.stream,
            "model_name": chat_request.model_name,
            "temperature": chat_request.temperature,
            "max_tokens": chat_request.max_tokens,
            "prompt_name": chat_request.prompt_name,
            "file_name": chat_request.fileName
        }
    return data

# WebSocket连接集合
websocket_connections = set()
async def ws_chat(websocket:WebSocket):
    print("请求时间：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), file = sys.stderr)
    log_id = questionid()

    #建立流式链接
    async def forward_to_post_and_stream_response(chat_request, websocket):
        #获取大模型请求将并流式发出
        
        data = get_chat_request_data(chat_request)

        qaaId = int(chat_request.qaaId)

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
        
        print('data received', file = sys.stderr)
        
        data = json.dumps(data)
        if_success=True
        if chat_request.kbName == None:
            url = config.langchain_chatchat_ip #+ config.url_dict["bigmodel_chat"]
        else:
            url = config.langchain_chatchat_ip #+ config.url_dict["knowbase_chat"]
        chunk_num = 0

        succcedd_result_head = json.dumps({
            "msg": "问答请求成功！",
            "code": 0,
            "logId": log_id
        })
        false_result_head = json.dumps({
            "msg": "问答请求失败！",
            "code": "-1",
            "logId": log_id
        })
        ############################################################################
        api_key = "sk-JyubfGLXR4nbxkL3C801Cc1c61F743749e40Ac1688Af870c"
        headers = {
            "Authorization": f"Bearer {api_key}",  # API key in the Authorization header
            "Content-Type": "application/json"  # Specify the content type
        }

        jsondata = json.loads(data)
        qs = jsondata['query']
        q1000 = ESconn.search1000(qs, index, "question")
        
        # print(q1000, file = sys.stderr)
        
        print('question searched', file = sys.stderr)

        #排序
        higher50 = []
        nselected = []

        toSort = {}
        qsegs = scores.segment(qs)
        
        print('question segment', file = sys.stderr)
    
        for hit in q1000['hits']['hits']:
            nselected.append(hit['_source'])
            
            hsegs = scores.segment(hit['_source']['question'])
            kscores = hit['_score']
            for i in qsegs:
                if i in hsegs:
                    kscores = kscores + 7

            qakey = '{问：'+ hit['_source']['question'] + ',' + '答：' + hit['_source']['answer'] + '}'
            toSort[qakey] = kscores 

            if kscores >= 25:
                higher50.append(hit['_source'])

        sorted_by_value = dict(sorted(toSort.items(), key=lambda item: item[1], reverse=True)[:50])
        keylist = list(sorted_by_value.keys())
        qaset = str(keylist)
        toLLM = scores.formPrompt(qs,qaset)
        
        print('qaa sorted' , file = sys.stderr)

        # if len(higher50) != 0:

        #     qscore = scores.keyScores(higher50, qsegs)
        
        #     best_index = scores.getmatch(qscore)
        
        #     rest = higher50[best_index]
            
        #     nselected.remove(rest)

        # related = []
        # keyword_ans = []
        # if len(nselected) == 0:
        #     related = []
        #     keyword_ans = []
        # # elif len(nselected) == 0:
        # #     related = []
        # #     keyword_ans = []
        # elif len(nselected) < 6:
        #     for i in range(0,len(nselected)):
        #         temp = {}
        #         temp['question'] = nselected[i]['question']
        #         temp['questionId'] = nselected[i]['id']
        #         related.append(temp)
                
        #         keyword_ans.append(temp['question'])
        # else:
        #     for i in range(0,5):
        #         temp = {}
        #         temp['question'] = nselected[i]['question']
        #         temp['questionId'] = nselected[i]['id']
        #         related.append(temp)
                
        #         keyword_ans.append(temp['question'])
                
        # print('related generated', file = sys.stderr)

        #反问
        # backq = scores.AskBack(q1000, qs)

        # backres = {}
        # if len(backq) > 0 :
        #     print('askback progress', file = sys.stderr)
        #     # log_content = log_content + 'covered, ask back\n'
        #     # res = ''
        #     ans = ''
        #     qs = ''

        #     if len(backq) == 1:
        #         ans = ans + backq[0]['answer']
        #         qs = qs + backq[0]['question']

        #     else:
        #         print('more than one hit', file = sys.stderr)
        #         ans = ans + "根据您输入的关键词，小e找到了下面这些问题，请问您是要问这些问题吗:<br />" 
                
        #         limit_counter = 0
                
        #         for i in backq:
        #             print('enter loop', file = sys.stderr)
        #             if limit_counter < 6:
        #                 print('enter if', file = sys.stderr)
        #                 ans = ans + i['question'] + '<br />'
        #                 limit_counter = limit_counter+1
        #                 print('end if', file = sys.stderr)
                   
        #         print('loop end', file = sys.stderr)
                    
        #         qs = qs + "根据您输入的关键词，小e找到了下面这些问题"

        #     backres = {
        #         "code": "0",
        #         "msg": "操作成功",
        #         "data": {
        #             "total":1,
        #             "result":[{
        #                 "question": qs,
        #                 "answer":  ans,
        #                 "related":related,
        #                 "ext": None
        #             }],
        #             "logId": log_id
        #         },
        #         "LLM":"N"
        #     }

        res = {
            "model": str(jsondata['model_name']),
            "messages":[
                {"role":"user",
                 "content":toLLM
                }
            ],
            "stream":True
        }
        rest = json.dumps(res)
        
        # print(rest, file = sys.stderr)
        
        ############################################################################
        async with httpx.AsyncClient() as client:
            answer_connected=None
            # if backres != {}:
            #     await websocket.send_json(backres)
            # else:
            try:
                async with client.stream("post", url, headers=headers,data=rest) as response:
                    # print('request sent to llm', file = sys.stderr)
                # async with client.stream("post", url, data=data) as response:
                    async for chunk in response.aiter_text():
                        #################################################################################
                        # print('chunk received', file = sys.stderr)
                        outputd = {
                            "code": "0",
                            "msg": "操作成功",
                            "data": {
                                "total":1,
                                "result":[{
                                    "question": qs,
                                    "answer":  chunk,
                                    "related":[],
                                    "ext": None
                                }],
                                "logId": log_id
                            },
                            "LLM":"Y"
                        }
                        # print('output generated', file = sys.stderr)
                        ########################################################################################
                        if response.status_code == 200 and chunk_num == 0:
                            # await websocket.send_text(succcedd_result_head + " || " + chunk)
                            await websocket.send_json(outputd)
                            chunk_num = chunk_num + 1
                            answer_connected=chunk
                        elif response.status_code == 200 and chunk_num != 0:
                            # await websocket.send_text(chunk)
                            await websocket.send_json(outputd)
                            answer_connected=answer_connected+chunk
                        else:
                            print('error happened', file =sys.stderr)
                            if_success=False
                            answer_connected="问答请求失败"
                            await websocket.send_text(false_result_head + " || " + chunk)
                            print(response.status_code)
                    if response.status_code==200:
                        announce = "data: {\"id\":\"chatcmpl-85ff983d-305a-465f-9cd5-5bd7add22dfa\",\"object\":\"chat.completion.chunk\",\"created\":1745205449,\"model\":\"/data/deepseek-qwen-14b\",\"choices\":[{\"index\":0,\"delta\":{\"content\":\"<br>【内容仅供参考】\"},\"logprobs\":null,\"finish_reason\":null}]}\n\n"#'此答案由deepseek大模型生产，仅供参考'
                        announce_request = {
                            "code": "0",
                            "msg": "操作成功",
                            "data": {
                                "total":1,
                                "result":[{
                                    "question": qs,
                                    "answer":  announce,
                                    "related":[],
                                    "ext": None
                                }],
                                "logId": log_id
                            },
                            "LLM":"Y"
                        }
                        await websocket.send_json(announce_request)
                        
                        
                        end_message=json.dumps({"text":"messageend"})
                        await websocket.send_text(end_message)

            except Exception as e:
                print("连接RAG框架接口异常： "+str(e))
                error_json=json.dumps({
                    "msg":"连接RAG框架接口异常： "+str(e),
                    "code":"-1",
                    "logId":log_id
                })
                if_success=False
                await websocket.send_text(error_json)
                answer_connected="连接rag框架接口异常： "+str(e)
            # finally:
                # await ws_chat_kafkaSender.wsChat_send_run(request_data=chat_request,if_success=if_success,logId=log_id,connected_answer=answer_connected)

    websocket_connections.add(websocket)
    await websocket.accept()
    try:
        while True:
            data=await websocket.receive_json()
            chat_model=ws_chat_request(**data)
            print(chat_model)
            if chat_model.question!="{heartbeat}":
                await forward_to_post_and_stream_response(chat_model,websocket)
            else:
                pass
    except Exception as e:
        error_json = json.dumps({
            "msg": "请求异常： " + str(e),
            "code": "-1",
            "logId": log_id
        })
        print("错误信息： "+str(e))
    finally:
        websocket_connections.remove(websocket)
        await websocket.close()