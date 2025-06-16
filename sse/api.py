import httpx
import json
import requests
import sys

import helpers
import config

async def stream(uid, oid, cid,  title, question, dept):
    api_key = config.api_key
    logid = helpers.createId()
    # headers = {
        # "Authorization": f"Bearer {api_key}", 
    #     "Content-Type": "application/json"  
    # }

    sdata = {
        
        "model": "申万宏源大模型",
        "deptName":dept,
        "messages": [
            {
                "role": "user", 
                "content": question
            }
        ]
        # "stream":True
    
    }
    # print(sdata)

    # sdata = {
    #     "model":"deepseek-r1-distill",
    #     "messages":[
    #         {
    #             "role":"user",
    #             "content":"3.11和3.9哪个数字大"
    #         }
    #     ],
    #     "stream":True
    # }

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
                                "type":"申请",
                                "data":{"title":"【审批通知】","summary":"您有1条待审批的采购申请","content":"申请人：张三\n金额：¥5,200.00\n用途：办公用品采购"},
                                "actions":{"type":"open_url","text":"查看详情","url":"https://example.com/detail/123"}
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
                        # print(response.status_code)
                        print(response, file =sys.stderr)


            # response = requests.post(url= url, headers=headers, data=send_data)
            # response.raise_for_status()  # 检查HTTP错误
            # print(response.text)
            # print(response.json()["choices"][0]["message"]["content"])
            save_res =helpers.saveHistory(uid, oid, cid,role='assist', title=title, content=savechat['content'])
            print("assist record status:"+str(save_res), file=sys.stderr)
            
        except requests.exceptions.RequestException as e:
            print(f"请求出错: {e}")
            # return None

