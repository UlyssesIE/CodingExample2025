import elasticsearch
import config

def search1000(searchKey, searchIndex, searchCol):
     es = elasticsearch.Elasticsearch(
          hosts=config.es_host,
          basic_auth=config.es_auth
     )


     query = {
          "query": {
               "match": {
                    searchCol: searchKey
                    }
                },
            "size": 1000
    }
     
     results = es.search(index=searchIndex, body=query)
    

     return results

def searchPage(index, pageNumber):
    es = elasticsearch.Elasticsearch(
          hosts=config.es_host,
          basic_auth=config.es_auth
    )
    index_name = index
    page_size = 10
    page_number = pageNumber  # Adjust the page number as needed

    query = {
        "query": {
            "match_all": {}
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
          hosts=config.es_host,
          basic_auth=config.es_auth
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
          hosts=config.es_host,
          basic_auth=config.es_auth
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
    return res

def createIndex(i, indexI):
    content = {}
    content["_index"] = indexI
    
    content["_id"] = str(i)
    index = {"index":content}
    return index

