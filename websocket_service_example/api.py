from fastapi import FastAPI,WebSocket
import json
from datetime import datetime

import httpx
import ESconn
import scores

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
    print("请求时间：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log_id = questionid()

    #建立流式链接
    async def forward_to_post_and_stream_response(chat_request, websocket):
        #获取大模型请求将并流式发出
        data = get_chat_request_data(chat_request)
        data = json.dumps(data)
        if_success=True
       
        url = config.langchain_chatchat_ip

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
        api_key = config.api_key
        headers = {
            "Authorization": f"Bearer {api_key}",  # API key in the Authorization header
            "Content-Type": "application/json"  # Specify the content type
        }

        jsondata = json.loads(data)
        qs = jsondata['query']
        q1000 = ESconn.search1000(qs, config.es_index, "question")

        #select hits from elasticsearch which have more than 25 scores
        higher50 = []
        nselected = []

        toSort = {}
        qsegs = scores.segment(qs)
    
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
        
        ############################################################################
        async with httpx.AsyncClient() as client:
            answer_connected=None
            try:
                async with client.stream("post", url, headers=headers,data=rest) as response:
                # async with client.stream("post", url, data=data) as response:
                    async for chunk in response.aiter_text():
                        if response.status_code == 200 and chunk_num == 0:
                            await websocket.send_text(succcedd_result_head + " || " + chunk)
                            chunk_num = chunk_num + 1
                            answer_connected=chunk
                        elif response.status_code == 200 and chunk_num != 0:
                            await websocket.send_text(chunk)
                            answer_connected=answer_connected+chunk
                        else:
                            if_success=False
                            answer_connected="问答请求失败"
                            await websocket.send_text(false_result_head + " || " + chunk)
                    if response.status_code==200:
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