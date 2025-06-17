from pydantic import BaseModel, Field,field_validator # 假设使用 Pydantic
from typing import Union, List,Dict
from config import product_dict,modelID_dict,kb_name_dict,model_name

class chat_request(BaseModel):
    modelId:str=Field(...,title="模块标识")
    product:int=Field(...,title="终端标识")
    question:str=Field(...,title="查询或问题")
    history_len:int=Field(-1,title="历史长度")
    history:List[Dict]=Field(None,title="对话历史")
    userId:str=Field(...,title="用户唯一标识")
    stream:bool=Field(False,title="是否流式传输")
    temperature:float=Field(0.7,title="采样温度")
    max_tokens:int=Field(None,title="最大token数量")
    prompt_name:str=Field("default",title="prompt模板名称")
    score_threshold:float=Field(1,title="召回信息的相似度阈值")
    kbName:int=Field(None,title="知识库名称")
    top_k:int=Field(3,title="参考知识库数量")
    model_name:str=Field(model_name,title="模型名称")
    fileName:str=Field(None,title="检索文件名称")


    @field_validator("modelId")
    @classmethod
    def check_modelId(cls, modelId) -> str:
        if modelId!=modelID_dict["chat"]:
            raise ValueError("{} is not a valid modelId for bigmode chat.".format(modelId))
        return modelId

    @field_validator("product")
    @classmethod
    def check_product(cls, product) -> int:
        if product != product_dict["ty_platform"]:
            raise ValueError("{} is not a valid product for bigmode chat.".format(product))
        return product

class ws_chat_request(BaseModel):
    modelId:str=Field(...,title="模块标识")
    product:int=Field(...,title="终端标识")
    question:str=Field(...,title="查询或问题")
    history_len:int=Field(-1,title="历史长度")
    history:List[Dict]=Field(None,title="对话历史")
    userId:str=Field(...,title="用户唯一标识")
    stream:bool=Field(False,title="是否流式传输")
    temperature:float=Field(0.7,title="采样温度")
    max_tokens:int=Field(None,title="最大token数量")
    prompt_name:str=Field("default",title="prompt模板名称")
    score_threshold:float=Field(1,title="召回信息的相似度阈值")
    kbName:int=Field(None,title="知识库名称")
    top_k:int=Field(3,title="参考知识库数量")
    model_name:str=Field(model_name,title="模型名称")
    fileName:str=Field(None,title="检索文件名称")


    @field_validator("modelId")
    @classmethod
    def check_modelId(cls, modelId) -> str:
        if modelId!=modelID_dict["ws_chat"]:
            raise ValueError("{} is not a valid modelId for bigmode chat.".format(modelId))
        return modelId

    @field_validator("product")
    @classmethod
    def check_product(cls, product) -> int:
        if product != product_dict["ty_platform"]:
            raise ValueError("{} is not a valid product for bigmode chat.".format(product))
        return product

    modelId: str = Field(..., title="模块标识")
    product: int = Field(..., title="终端标识")
    kbName: int = Field(..., title="知识库名称")
    userId: str = Field(..., title="用户唯一标识")
    fileList: List[str] = Field(..., title="删除文档列表")
    delete_content: bool=Field(True,title="是否删除原文件")
    not_refresh_vs_cache: bool=Field(False,title="暂不保存向量库（用于FAISS）")

    @field_validator("modelId")
    @classmethod
    def check_modelId(cls, modelId) -> str:
        if modelId != modelID_dict["delete_docs"]:
            raise ValueError("{} is not a valid modelId for delete docs.".format(modelId))
        return modelId

    @field_validator("product")
    @classmethod
    def check_product(cls, product) -> int:
        if product != product_dict["ty_platform"]:
            raise ValueError("{} is not a valid product for knowledge delete docs.".format(product))
        return product