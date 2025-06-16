# langchain_chatchat_ip="http://192.168.24.123:30123/open-api/langchain-chat/"
langchain_chatchat_ip= "http://192.168.24.137:30123/open-api/oneapi/v1/chat/completions"

url_dict={
    "upload_doc_bylink":"knowledge_base/upload_docs_bylink",
    "bigmodel_chat":"chat/chat",
    "knowbase_chat":"chat/knowledge_base_chat",
    "kb_search":"knowledge_base/search_docs",
    "delete_docs":"knowledge_base/delete_docs"
}

upload_to_knowledgebase_return_url= "http://192.168.24.123:30123/open-api/touyan-embedding-return/debug/"

# model_name="glm4-9b"
model_name = "deepseek-r1-distill"

modelID_dict={
    "chat":"512",
    "upload_to_knowledgebase":"505",
    "kb_search":"507",
    "ws_chat":"516",
    "delete_docs":"517"
}

product_dict={
    "ty_platform":5
}

kb_name_dict={
    1:"public",
    2:"personal"
}

#kafka日志相关配置：
kafka_ip='lab-ai-sw-1:9092,lab-ai-sw-2:9092,lab-ai-sw-3:9092'
kafka_topic="ai_rec_qa_route_log"