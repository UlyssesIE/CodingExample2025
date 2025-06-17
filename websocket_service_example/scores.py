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
     propart = "你是一个智能问答系统小e，任务是判断用户输入是否能够通过知识库中的内容得到回答。请按照以下步骤进行分析：1.仔细阅读用户输入，理解其核心内容和意图。2.判断B中是否有任一问答对在语义上与A中问题相同。3.若B中有问答对与A中问题在语义上相同，则返回B中‘答’的部分。若B中没有问答对可以与A中问题匹配，则进入下一步。4.判断B中是否有任一问答对在语义上与A中问题有关联。5.若B中有问答对与A中问题在语义上有关联，则综合所有有关联的问答对，生成一个答案。若B中没有任何问答对与A中问题在语义上有关联，则进入下一步。6.若B中没有任何问答对与A中问题在语义上有关联，则自行生成一个答案。案例1：略。案例2：略。案例3：略。" 
     bacpart = "根据上述步骤和案例，对以下用户输入A和知识库B进行分析并输出结果,在结果中不要加入你的思考过程以及A和B的内容。"
     prompt = propart + bacpart + '用户输入A：[' + qs + ']' + '知识库B：' + qaset

     return prompt