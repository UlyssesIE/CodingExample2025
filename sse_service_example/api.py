import httpx
import json
import requests
import sys

import helpers
import config

async def stream(uid, oid, cid,  title, question, dept):
    api_key = config.api_key
    logid = helpers.createId()

    sdata = {
        
        "model": "deepseek-r1-distill",
        "deptName":dept,
        "messages": [
            {
                "role": "user", 
                "content": question
            }
        ],
        "stream":True
    
    }

    url = config.url
    send_data = json.dumps(sdata)

    async with httpx.AsyncClient() as client:
        savechat={}
        savechat['role'] = 'assist'
        savechat['content'] = ""
        try:
            async with client.stream("POST", url, data=send_data) as response:
            # async with client.stream("POST", url, headers=headers, data=send_data) as response:
                async for chunk in response.aiter_lines():
                    savechat['content'] =savechat['content'] + str(chunk)
                    output_data = {
                        "code": "0",
                        "msg": "操作成功",
                        "data":{
                            "result":[{
                                "question":"Q",
                                "answer":chunk,

                            }],
                            "card":[{
                                "type":"test",
                                "data":{"title":"【test】","summary":"test","content":"test content"},
                                "actions":{"type":"open_url","text":"test","url":"https://example.com/detail/123"}
                            }],
                            "ext": None,
                            "logId": logid
                        }
                    }

                    # yield output_data
                    if response.status_code == 200:
                        res = json.dumps(output_data)
                        yield res
                    else:
                        print('error happened', file =sys.stderr)
                        print(question)
                        print(response, file =sys.stderr)

            save_res =helpers.saveHistory(uid, oid, cid,role='assist', title=title, content=savechat['content'])
            print("assist record status:"+str(save_res), file=sys.stderr)
            
        except requests.exceptions.RequestException as e:
            print(f"请求出错: {e}")
