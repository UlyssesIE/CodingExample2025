from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import sys

import api
import helpers

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

#use for streaming output
@app.post("/stream")
async def stream_llm_response(request: Request):
    data = await request.json()
    
    userId = data.get('userId',"")
    orgId = data.get('orgId',"")
    chatId = data.get('chatId',"")
    question = data.get('question',"")
    chatTitile = data.get('chatTitile',"")
    history = data.get('history',"")

    #There are only two organizations 
    if orgId == '1':
        deptName = "organization 1"
    elif orgId == '2':
        deptName = "organization 2"
    else:
        errormsg={
            "code": "1",
            "msg": "操作失败",
            "data":{
                "result":"organization ID does not exist"
            }
        }
        return errormsg

    save_res = helpers.saveHistory(userId, orgId, chatId, role='user', title=chatTitile, content=question)
    print("user "+ str(userId) +" record status:"+str(save_res), file=sys.stderr)
    
    return EventSourceResponse(
        api.stream(userId, orgId, chatId, chatTitile, question, deptName),
        headers={
            'Content-Type': 'text/event-stream',
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

#use for create new chat id
@app.post("/newchat")
async def newchat(request: Request):
    data = await request.json()

    #Make sure the frontend apps have following messages
    userId = data.get('userId',"")
    orgId = data.get('orgId',"")
    createTime = data.get('createTime',"")

    chatId = helpers.createId()
    logId = helpers.createId()


    res = {
        "code": "0",
        "msg": "操作成功",
        "data":{
            "result":[{
                "chatId":chatId,
                "ext":None
            }],
            "logId":logId
        }
    }

    return res
#use to get a list of history chat
@app.post("/historylist")
async def hislist(request: Request):
    data = await request.json()

    userId = data.get('userId',"")
    orgId = data.get('orgId',"")
    updateTime = data.get('updateTime',"")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    chatids, updateTimes, titles = helpers.chatlist(userId)

    hostorylist = []
    
    if len(chatids) > 0:

        for i in (0,len(chatids)-1):
            temp = {}
            temp['historyId'] = chatids[i]
            temp['historyTitle'] = titles[i]
            temp['updateTime'] = updateTimes[i]
    
            hostorylist.append(temp)

    res = {
        "code": "0",
        "msg": "操作成功",
        "data":{
            "result":hostorylist
        }
    }

    return res
#use to get the content of a specific chat
@app.post("/chathistory")
async def chathis(request: Request):
    data = await request.json()

    userId = data.get('userId',"")
    orgId = data.get('orgId',"")
    chatId = data.get('chatId',"")
    updateTime = data.get('updateTime',"")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    roles,contents = helpers.allchats(userId, chatId, orgId)

    allchata = []
    
    if len(roles)>0:

        for i in range(0, len(roles)):
            temp = {}
            temp['role'] = roles[i]
            temp['content'] = contents[i]
    
            allchata.append(temp)

    res = {
        "code": "0",
        "msg": "操作成功",
        "data": {
            "result":allchata
        }
    }

    return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5759)