import uuid
import elasticsearch
from datetime import datetime
import config

def createId():
    s_uuid=str(uuid.uuid4())
    l_uuid=s_uuid.split('-')
    s_uuid=''.join(l_uuid)
    return s_uuid

def saveHistory(uid, oid, cid, role, title, content):
    es = elasticsearch.Elasticsearch(
        #  hosts = ['http://172.17.172.149:9200'],
        #  basic_auth = ('es2_zntj', 'Zzty240603!@#')
          hosts=config.es_host,
          basic_auth=config.es_auth
        )
    
    esindex = 'oa_history'
    
    insertv = {}

    cur = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    insertv['userId'] = uid
    insertv['orgId'] = oid
    insertv['chatId'] = cid
    insertv['role'] = role
    insertv['title'] = title
    insertv['content'] = content
    insertv['updataTime'] = cur
    
    res = es.index(index=esindex, document=insertv)

    return res['result']

def distinctsearch():

    es = elasticsearch.Elasticsearch(
        #  hosts = ['http://172.17.172.149:9200'],
        #  basic_auth = ('es2_zntj', 'Zzty240603!@#')
          hosts=config.es_host,
          basic_auth=config.es_auth
        )
    
    esindex = 'oa_history'

    query = {
        "size": 0,
        "aggs": {
            "distinct_titles": {
                "terms": {
                    "field": "title.keyword", 
                    "size": 100
                }
            }
        }
    }
    results = es.search(index=esindex, body=query)

    return results

def chatlist(userid):
    es = elasticsearch.Elasticsearch(
        #  hosts = ['http://172.17.172.149:9200'],
        #  basic_auth = ('es2_zntj', 'Zzty240603!@#')
          hosts=config.es_host,
          basic_auth=config.es_auth
        )

    query = {
        
        "size": 0,  
        "query": {
            "term": {
                "userId": userid
            }
        },
        "aggs": {
            "group_by_title": {
                "terms": {
                    "field": "title.keyword",  
                    "size": 100  
                },
                "aggs": {
                    "latest_doc": {
                        "top_hits": {  
                            "size": 1,  
                            "sort": [
                            {
                                "updataTime.keyword": {  
                                    "order": "desc"
                                }
                            }
                            ]
                        }
                    }
                }
            }
        }
        
    }

    esindex = 'oa_history'

    results = es.search(index=esindex, body=query)

    chatids = []
    updateTimes = []
    titles = []
    for i in results['aggregations']['group_by_title']['buckets']:
        print(i['latest_doc']['hits']['hits'][0]['_source'])
        temp = i['latest_doc']['hits']['hits'][0]['_source']
        chatids.append(temp['chatId'])
        updateTimes.append(temp['updataTime'])
        titles.append(temp['title'])
        print('#############')

    return chatids, updateTimes, titles

def allchats(userid, chatid, orgid):
    es = elasticsearch.Elasticsearch(
        #  hosts = ['http://172.17.172.149:9200'],
        #  basic_auth = ('es2_zntj', 'Zzty240603!@#')
          hosts=config.es_host,
          basic_auth=config.es_auth
        )
    
    query = {
        "query": {
            "bool": {
                "must": [
                    { "term": { "userId": userid }},
                    { "term": { "chatId": chatid }},
                    { "term": { "orgId": orgid }}
                ]
            }
        }
    }

    esindex = 'oa_history'

    results = es.search(index=esindex, body=query)

    roles = []
    contents = []

    for i in results['hits']['hits']:
        temp = i['_source']

        roles.append(temp['role'])
        contents.append(temp['content'])

    return roles, contents