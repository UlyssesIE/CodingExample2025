# import requests
import elasticsearch


# def embeddingMsg(sentence):
#     url = 'http://192.168.24.137:9998/v1/embeddings'
#     myobj = {"input":[sentence],
#         "model":"bge-m3-local"}
    
#     x = requests.post(url, json = myobj)
#     res = x.json()["data"][0]["embedding"]
    
#     return res

def search1000(searchKey, searchIndex, searchCol):
     es = elasticsearch.Elasticsearch(
        #  hosts = ['http://172.17.172.149:9200'],
        #  basic_auth = ('es2_zntj', 'Zzty240603!@#')
          hosts=['http://192.168.152.47:9292'],
          basic_auth=('ai', 'Aireccontent@123')
        )


     query = {
          "query": {
               "match": {
                    searchCol: searchKey
                    }
                },
            "size": 500
    }
     
     results = es.search(index=searchIndex, body=query)
    #  results = es.search(index="jcs_smart_qaa", body=query)
    

     return results

def searchPage(index, pageNumber):
    es = elasticsearch.Elasticsearch(
        #  hosts = ['http://172.17.172.149:9200'],
        # #  basic_auth = ('es2_zntj', 'Zzty240603!@#')
        hosts=['http://192.168.152.47:9292'],
        basic_auth=('ai', 'Aireccontent@123')
    )
    index_name = index
    page_size = 10
    page_number = pageNumber  # Adjust the page number as needed

    query = {
        "query": {
            "bool": {
              "must": [
                {
                  "match_all": {}
                }
              ],
              "must_not": [
                {
                  "wildcard": {
                    "id": "fa*" 
                  }
                }
              ]
            }
        },
        "sort": [
            {"hot": {"order": "desc"}}
        ],
        "size": page_size,
        "from": (page_number - 1) * page_size
    }

    response = es.search(index=index_name, body=query)

    res = []

    for hit in response['hits']['hits']:
        res.append(hit['_source'])
        # print(hit['_source']['id'])
    return res

def searchKey(idx, key, pageNumber, pageSize):
    es = elasticsearch.Elasticsearch(
        #  hosts = ['http://172.17.172.149:9200'],
        # #  basic_auth = ('es2_zntj', 'Zzty240603!@#')
        hosts=['http://192.168.152.47:9292'],
        basic_auth=('ai', 'Aireccontent@123')
    )
        
    keyword = key
    index = idx
    query = {
        "size" : pageSize,
        "from": (pageNumber - 1) * pageSize,

        "query": {
            "match": {
                "question": keyword
            }
        }
    }

    response = es.search(index=index, body=query)

    res = []
    for hit in response['hits']['hits']:
        res.append(hit['_source'])
        # print(hit['_source']['id'])
    return res

def searchPoint(qsid, idx):
    es = elasticsearch.Elasticsearch(
        #  hosts = ['http://172.17.172.149:9200'],
        # #  basic_auth = ('es2_zntj', 'Zzty240603!@#')
        hosts=['http://192.168.152.47:9292'],
        basic_auth=('ai', 'Aireccontent@123')
    )

    id = qsid
    index = idx
    query = {
        "size" : 1,

        "query": {
            "match": {
                "id": id
            }
        }
    }

    response = es.search(index=index, body=query)

    res = []
    for hit in response['hits']['hits']:
        res.append(hit['_source'])
        # print(hit['_source']['answer'])
    return res

def createIndex(i, indexI):
    content = {}
    content["_index"] = indexI
    
    # content["_index"] = ""jcs_smart_qaa""
    content["_id"] = str(i)
    index = {"index":content}
    return index

# def bulkToEs():
#     es = elasticsearch.Elasticsearch(
#         hosts=['http://192.168.152.47:9292'],
#         basic_auth=('ai', 'Aireccontent@123')
#         )
    
