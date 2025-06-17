import flask
import json 
import uuid
# import ESconn
# import scores
import elasticsearch
import sys
import time

import docToEs

# import requests

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

@server.route('/upload', methods = ['post'])
def uploadToEs():
    
    counter = 0
    # counter = 0
    insertValues = flask.request.get_json()
    fileName=insertValues['fileName']
    ESindex=insertValues['index']
    
    filePath = '/files/'+ str(fileName)
    
    resMsg = docToEs.ESupload(filePath, ESindex, counter)
    
    res =  {'msg':resMsg, 'msg_code':0, 'msg_status':'success'}
    
    return json.dumps(res, ensure_ascii=False)

@server.route('/table', methods = ['post'])
def tableToEs():
    counter = 0
    # counter = 0
    insertValues = flask.request.get_json()
    fileName=insertValues['fileName']
    ESindex=insertValues['index']

    filePath = '/files/'+ str(fileName)

    resMsg = docToEs.docTableUpload(filePath, ESindex, counter)

    res = {'msg':resMsg, 'msg_code':0, 'msg_status':'success'}

    return json.dumps(res, ensure_ascii=False)
# if __name__ == "__main__":
server.run(host= '0.0.0.0', port=7637, debug=True)