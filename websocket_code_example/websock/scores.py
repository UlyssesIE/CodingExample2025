import binascii
import os
import jieba
import math

import pickle
import random

import datetime
from pandas.tseries.offsets import BDay
import json

def segment(sentence):
        # path = os.path.join(os.path.dirname("/data/LLM_Eval/"), "stoptext.txt")
        path = os.path.join("/data/ehome/stoptext.txt")
        StopWords = [line.strip() for line in open(path, \
                encoding='utf-8').readlines()]
        
        WordCut = jieba.lcut(sentence.strip())

        output = []
        for word in WordCut:
            word = word.lower()
            if word not in StopWords and word != '\n':
                output.append(word)
        
        return output

def EuclideanDistance(x, y):
    d = 0
    for a, b in zip(x, y):  # zip将两个列表打包为元组的列表
        d += (a - b) ** 2
    return d ** 0.5

def keyScores(qdict,qkeywords):
     scores1 = []
     for i in qdict:
          score1 = 0
          for j in qkeywords:
            if j in i['question']:
                score1 +=1
          scores1.append(score1)
     return scores1

def getmatch(scores):
    maxs = max(scores)
    maxi = scores.index( maxs )
    
    return maxi

def GetTF(corpus):
        tf = {}
        total = len(corpus)
        for x in corpus:
            tf[x] = corpus.count(x) / total
        
        return tf

def GetIDF(corpus, data):
        freq = dict.fromkeys(corpus, 0)
            
        idf = {}
        total = len(data)

        for word in corpus:
            for d in data:
                if word in d:
                    freq[word] += 1

        for word in freq:
            TempIDF = total / (freq[word] + 1)
            idf[word] = math.log10(TempIDF)
        return idf

def GetTFIDF(input):
        tf = GetTF(input)
        idf = GetIDF(input, pickle.load(open('cache.pickle', 'rb')))

        result = {}
        for key, value in tf.items():
            result[key] = value * idf[key]

        return result

def GetWeight(input,weight):
        input = segment(input)
        if weight == "TFIDF":
            return GetTFIDF(input)
        elif weight == "None":
            weight = {}
            for word in input:
                weight[word] = 1
            return weight
        else:
            weight = {}
            for word in input:
                weight[word] = input.count(word)
            return weight
        
def cossim(input1, input2):
        result1 = GetWeight(input1,None)
        result2 = GetWeight(input2,None)

        WordSet = list(set(result1.keys()).union(set(result2.keys())))
        DotProduct = 0
        sq1 = 0
        sq2 = 0

        for word in WordSet:
            # Get vector value of both documents
            vector1 = result1[word] if word in result1 else 0
            vector2 = result2[word] if word in result2 else 0
            
            # Calculate Cosine Similarity for this dimension
            DotProduct += vector1 * vector2
            sq1 += pow(vector1, 2)
            sq2 += pow(vector2, 2)

        try:
            FinalResult = DotProduct / (math.sqrt(sq1) * math.sqrt(sq2))
        except ZeroDivisionError:
            FinalResult = 0.0

        return FinalResult

def jaccard(input1, input2):
        result1 = GetWeight(input1,None)
        result2 = GetWeight(input2,None)

        WordSet = list(set(result1.keys()).union(set(result2.keys())))
        TopSum = 0
        BottomSum = 0

        for word in WordSet:
            vector1 = result1[word] if word in result1 else 0
            vector2 = result2[word] if word in result2 else 0
            
            TopSum += min(vector1, vector2)
            BottomSum += max(vector1, vector2)

        return TopSum / BottomSum

# Algorithm: h(x) = (a*x + b) % c
def HashAlg(k):
        MaxHash = 2**32 - 1
        # Create a list of 'k' random values.
        RandomList = []
        
        while k > 0:
            random.seed(k)
            # Get a random shingle ID.
            RandIndex = random.randint(0, MaxHash) 
        
            # Make sure the hash is unique
            while RandIndex in RandomList:
                RandIndex = random.randint(0, MaxHash) 
            
            # Append the value
            RandomList.append(RandIndex)
            k = k - 1
            
        return RandomList

def minhash(input1, input2):
    prime = 4294967311
    HashNums = 16
    
    result = GetWeight(input1,None)
    result2 = GetWeight(input2,None)

    coeff1 = HashAlg(HashNums)
    coeff2 = HashAlg(HashNums)

    signature = {}
    signature2 = {}

    MinhashNum = prime
    MinhashNum2 = prime
    for i in range(0, HashNums):
        for x in result.keys():
            crc = binascii.crc32(x.encode('utf-8')) & 0xffffffff
            # Generating Hash
            HashCode = (coeff1[i] * crc + coeff2[i]) % prime
            #  Track the lowest hash code seen.
            if HashCode < MinhashNum:
                MinhashNum = HashCode
                
            if MinhashNum not in signature:
                signature[MinhashNum] = result[x]

        for y in result2.keys():
            crc = binascii.crc32(y.encode('utf-8')) & 0xffffffff
            HashCode2 = (coeff1[i] * crc + coeff2[i]) % prime
            if HashCode2 < MinhashNum2:
                MinhashNum2 = HashCode2
                
            if MinhashNum2 not in signature2:
                signature2[MinhashNum2] = result2[y]
        
    intersect = 0
    total = 0
    for x, y in signature.items():
        if x in signature2:
            intersect += y
        total += y

    try:
        return intersect / total
    except ZeroDivisionError:
        return 0
    
def AskBack(callq, inputq):
     allcovered = []
     covered = []
     for i in callq['hits']['hits']:
        # print(i['_source']['question'])
        temp = str(i['_source']['question'])
        # print(temp)
        # print(testq in temp)
        
        if inputq.lower() in temp.lower():
            allcovered.append(i['_source'])


        else:
            seg = segment(inputq)
            # print(len(seg))
            temp_cover = []
            current = 0
            for j in seg:
                seg_idx = ()
                if j not in temp:
                    break
                else:
                    next = seg.index(j)
                    if next >= current:
                        current = next
                        seg_idx= (j, seg.index(j))
                        temp_cover.append(seg_idx)
                    else:
                        break
            if len(temp_cover) == len(seg):
                covered.append(i['_source'])
     if len(allcovered)>0:
        return allcovered
     else:
        return covered

def formPrompt(qs,qaset):
     propart = "你是一个智能问答系统小e，任务是判断用户输入是否能够通过知识库中的内容得到回答。请按照以下步骤进行分析：1.仔细阅读用户输入，理解其核心内容和意图。2.判断B中是否有任一问答对在语义上与A中问题相同。3.若B中有问答对与A中问题在语义上相同，则返回B中‘答’的部分。若B中没有问答对可以与A中问题匹配，则进入下一步。4.判断B中是否有任一问答对在语义上与A中问题有关联。5.若B中有问答对与A中问题在语义上有关联，则综合所有有关联的问答对，生成一个答案。若B中没有任何问答对与A中问题在语义上有关联，则进入下一步。6.若B中没有任何问答对与A中问题在语义上有关联，则自行生成一个答案。案例1：A：[我不想再用条件单了，怎么办？]B：[{问：融资融券账户可在手机软件的业务办理菜单办理哪些业务，答：您好，使用申万宏源大赢家/申万宏源申财有道/赢家理财高端版手机软件/申万宏源财富管理微信公众号等渠道登陆融资融券资金账号后可以办理两融仓单展期、两融授信额度调整、密码修改与重置等业务。温馨提示：部分业务受理后需要审核，等待审核情况。}，{问：如何办理协助司法扣划业务？，答：您好，我司支持司法扣划，例如，通过法院拍得的股份，想划转到自己名下，原持股人和客户都在我司开过户，可以通过非交易过户-司法扣划的方式申请。具体办理流程建议咨询开户营业部。温馨提示：融资融券账户办理司法扣划，需要先了结融资融券账户的负债，然后把股份和资金划转到普通账户，再办理司法扣划}，{问：智能条件单如何终止？，答：好，1、智能条件单已触发但是未成交需要终止：（1）如果您设置的是条件单，是一次性运行的，已执行里面就没有终止按钮，只能在交易委托里手动撤单；（2）如果您设置的是网格单，可以在已执行里面进行终止、修改、重启，或者在交易委托里手动撤单。2、未执行的条件单可以通过申万宏源大赢家-交易-智能条件单-我的条件单-监控中或未监控页面进行暂停、修改或终止操作。温馨提示：智能条件单不支持批量暂停}]解答过程：第一步为，仔细阅读用户输入，理解其核心内容和意图。A中问题为我不想再用条件单了，怎么办。表达了希望条件单结束的意图。第二步，判断B中是否有任一问答对在语义上与A中问题相同。A中问题为：我不想再用条件单了，怎么办。遍历B中所有问答对，发现问答对{问：智能条件单如何终止？，答：好的。1、智能条件单已触发但是未成交需要终止：（1）如果您设置的是条件单，是一次性运行的，已执行里面就没有终止按钮，只能在交易委托里手动撤单；（2）如果您设置的是网格单，可以在已执行里面进行终止、修改、重启，或者在交易委托里手动撤单。2、未执行的条件单可以通过申万宏源大赢家-交易-智能条件单-我的条件单-监控中或未监控页面进行暂停、修改或终止操作。温馨提示：智能条件单不支持批量暂停}在语义上与A中问题相同，进入第三步。第三步为，若B中有问答对与A中问题在语义上相同，则返回B中‘答’的部分。若B中没有问答对可以与A中问题匹配，则进入下一步。因为已发现语义相同的问答对，因此返回：好的。1、智能条件单已触发但是未成交需要终止：（1）如果您设置的是条件单，是一次性运行的，已执行里面就没有终止按钮，只能在交易委托里手动撤单；（2）如果您设置的是网格单，可以在已执行里面进行终止、修改、重启，或者在交易委托里手动撤单。2、未执行的条件单可以通过申万宏源大赢家-交易-智能条件单-我的条件单-监控中或未监控页面进行暂停、修改或终止操作。温馨提示：智能条件单不支持批量暂停。案例2：A：[我不想再用条件单了，怎么办？]B：[{问：融资融券账户可在手机软件的业务办理菜单办理哪些业务，答：您好，使用申万宏源大赢家/申万宏源申财有道/赢家理财高端版手机软件/申万宏源财富管理微信公众号等渠道登陆融资融券资金账号后可以办理两融仓单展期、两融授信额度调整、密码修改与重置等业务。温馨提示：部分业务受理后需要审核，等待审核情况。}，{问：如何办理协助司法扣划业务？，答：您好，我司支持司法扣划，例如，通过法院拍得的股份，想划转到自己名下，原持股人和客户都在我司开过户，可以通过非交易过户-司法扣划的方式申请。具体办理流程建议咨询开户营业部。温馨提示：融资融券账户办理司法扣划，需要先了结融资融券账户的负债，然后把股份和资金划转到普通账户，再办理司法扣划}，{问：智能条件单如何终止？，答：好，1、智能条件单已触发但是未成交需要终止：（1）如果您设置的是条件单，是一次性运行的，已执行里面就没有终止按钮，只能在交易委托里手动撤单；（2）如果您设置的是网格单，可以在已执行里面进行终止、修改、重启，或者在交易委托里手动撤单。2、未执行的条件单可以通过申万宏源大赢家-交易-智能条件单-我的条件单-监控中或未监控页面进行暂停、修改或终止操作。温馨提示：智能条件单不支持批量暂停}]解答过程：第一步为，仔细阅读用户输入，理解其核心内容和意图。A中问题为条件单业务如何办理？其核心意图是希望办理条件单业务。第二步，判断B中是否有任一问答对在语义上与A中问题相同。A中问题为条件单业务如何办理？遍历B中所有问答对，发现没有问答对在语义上与A中问题相同，进入第三步。第三步，若B中有问答对与A中问题在语义上相同，则返回B中‘答’的部分。若B中没有问答对可以与A中问题匹配，则进入下一步。B中没有问答对可以与A中问题匹配，进入下一步。第四步，判断B中是否有任一问答对在语义上与A中问题有关联。遍历B中所有问答对，发现问答对{问：智能条件单如何终止？，答：好，1、智能条件单已触发但是未成交需要终止：（1）如果您设置的是条件单，是一次性运行的，已执行里面就没有终止按钮，只能在交易委托里手动撤单；（2）如果您设置的是网格单，可以在已执行里面进行终止、修改、重启，或者在交易委托里手动撤单。2、未执行的条件单可以通过申万宏源大赢家-交易-智能条件单-我的条件单-监控中或未监控页面进行暂停、修改或终止操作。温馨提示：智能条件单不支持批量暂停}与A中问题有关联，都有关条件单业务。第五步，若B中有问答对与A中问题在语义上有关联，则综合所有有关联的问答对，生成一个答案。若B中没有任何问答对与A中问题在语义上有关联，则进入下一步。因为B中有问答对与A中问题在语义上有关联，尝试综合问答对生成答案，有关联的问答对回答了智能条件单如何终止，A中问题为条件单业务如何办理，这两者步骤上可能有相似之处，应该就此给出建议，生成回答：我不知道如何办理条件单，但我知道终止条件单需要通过申万宏源大赢家-交易-智能条件单-我的条件单-监控中或未监控页面进行，也许办理条件单的步骤可以参考终止条件单，具体操作请联系相关业务人员咨询。案例3：A：[如何通过申万宏源e家交易？]B：[{问：融资融券账户可在手机软件的业务办理菜单办理哪些业务，答：您好，使用申万宏源大赢家/申万宏源申财有道/赢家理财高端版手机软件/申万宏源财富管理微信公众号等渠道登陆融资融券资金账号后可以办理两融仓单展期、两融授信额度调整、密码修改与重置等业务。温馨提示：部分业务受理后需要审核，等待审核情况。}，{问：如何办理协助司法扣划业务？，答：您好，我司支持司法扣划，例如，通过法院拍得的股份，想划转到自己名下，原持股人和客户都在我司开过户，可以通过非交易过户-司法扣划的方式申请。具体办理流程建议咨询开户营业部。温馨提示：融资融券账户办理司法扣划，需要先了结融资融券账户的负债，然后把股份和资金划转到普通账户，再办理司法扣划}，{问：智能条件单如何终止？，答：好，1、智能条件单已触发但是未成交需要终止：（1）如果您设置的是条件单，是一次性运行的，已执行里面就没有终止按钮，只能在交易委托里手动撤单；（2）如果您设置的是网格单，可以在已执行里面进行终止、修改、重启，或者在交易委托里手动撤单。2、未执行的条件单可以通过申万宏源大赢家-交易-智能条件单-我的条件单-监控中或未监控页面进行暂停、修改或终止操作。温馨提示：智能条件单不支持批量暂停}]解答过程：第一步为，仔细阅读用户输入，理解其核心内容和意图。A中为题为如何通过申万宏源e家交易？其核心意图是希望通过申万宏源e家进行交易操作。第二步，判断B中是否有任一问答对在语义上与A中问题相同。遍历B中所有问答对，发现没有问答对在语义上与A中问题相同，进入第三步。第三步，若B中有问答对与A中问题在语义上相同，则返回B中‘答’的部分。若B中没有问答对可以与A中问题匹配，则进入下一步。B中没有问答对可以与A中问题匹配，进入下一步。第四步，判断B中是否有任一问答对在语义上与A中问题有关联。遍历B中所有问答对，没有发现问答对与A中问题有关联。第五步，若B中有问答对与A中问题在语义上有关联，则综合所有有关联的问答对，生成一个答案。若B中没有任何问答对与A中问题在语义上有关联，则进入下一步。没有发现问答对与A中问题有关联，进入下一步。第六步，若B中没有任何问答对与A中问题在语义上有关联，则我需要自行生成一个答案。" 
     bacpart = "根据上述步骤和案例，对以下用户输入A和知识库B进行分析并输出结果,在结果中不要加入你的思考过程以及A和B的内容。"
     prompt = propart + bacpart + '用户输入A：[' + qs + ']' + '知识库B：' + qaset

     return prompt