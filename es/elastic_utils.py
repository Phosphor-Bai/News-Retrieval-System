import json
import jieba
from elasticsearch import Elasticsearch

from . import word2vec


def store_data():
    data_path = "./data/rmrb_2000-2015.jsonl"
    counter = 1
    with open(data_path, 'r', encoding='utf-8') as f:
        line = f.readline()
        while line:
            if not es.exists(index='try_index', id=counter):
                line_data = json.loads(line)
                line_content = line_data['content']
                word = []
                type = []
                for s in line_content:
                    sentence = s[0].split()
                    s_word = []
                    s_type = []
                    for w in sentence:
                        if w.find('_') == 0:
                            continue    # white_space
                        w = w.split('_')
                        if len(w) != 2:
                            print('error', w)
                        else:
                            s_word.append(w[0])
                            s_type.append(w[1])
                    if len(s_word) > 0:
                        word += s_word
                        word += ['\n']
                        type += s_type
                        type += ['endl']
                line_data['content'] = word
                line_data['word_type'] = type
                # print(line_data)
                res = es.create(index='try_index', id=counter, body=line_data)
                # print(res)
            if counter % 100 == 0:
                print(counter)
            counter += 1
            if counter > 100000:
                break
            line = f.readline()


def search_more(keywords_str, yearmonth1, yearmonth2):
    es = Elasticsearch([{'host':'localhost', 'port':9200}])
    search_doc = {
        "query": {
            "bool":{
                "should": [],
                "minimum_should_match": 1,
                "filter":{"range":{"date":{
                    "gte": yearmonth1,
                    "lte": yearmonth2,
                    "format": "yyyy-MM"
                }}}
            }
        }
    }
    # 使用jieba进行分词
    # 将分词结果都设为关键词避免检索时elastic search自动逐字分词
    # lcut_for_search分得更细，适合基于倒排索引检索，但可能存在冗余（例如'北京晚报'会被切割为['北京', '晚报', '北京晚报']）
    # 检索时使用should，即“or”，先模糊查询之后再重排序
    keywords = jieba.lcut_for_search(keywords_str)
    print(keywords)
    for keyword in keywords:
        keyword_term = {"term": {"content.keyword": keyword}}
        search_doc["query"]["bool"]["should"].append(keyword_term)
    # 加个filter_path可以避免返回无用数据
    search_res = es.search(index="try_index", body=search_doc, filter_path=['hits.hits._id', 'hits.hits._source', 'hits.hits._score'], size=50)
    search_res = eval(str(search_res))
    search_res = search_res['hits']['hits']
    search_res_raw = [s['_source'] for s in search_res]
    ids = [s['_id'] for s in search_res]
    scores = [s['_score'] for s in search_res]
    ids_ranked = word2vec.rank_doc(keywords=keywords, ids=ids, scores=scores)
    search_res_ranked = [search_res_raw[ids.index(i)] for i in ids_ranked]
    return search_res_raw[:10], search_res_ranked[:10]


def search_data(request_dict):
    es = Elasticsearch([{'host':'localhost', 'port':9200}])
    if request_dict['operation'] == 'only':
        if request_dict['include1']:
            search_doc = {
                "query": {
                    "bool":{
                        "must":{"term":{"content.keyword": request_dict['keyword1']}},
                        "filter":{"range":{"date":{
                            "gte": request_dict["yearmonth1"],
                            "lte": request_dict["yearmonth2"],
                            "format": "yyyy-MM"
                        }}}
                    }
                }
            }
        else:
            search_doc = {
                "query": {
                    "bool":{
                        "must_not":{"term":{"content.keyword": request_dict['keyword1']}},
                        "filter":{"range":{"date":{
                            "gte": request_dict["yearmonth1"],
                            "lte": request_dict["yearmonth2"],
                            "format": "yyyy-MM"
                        }}}
                    }
                }
            }
    elif request_dict['operation'] == 'and':
        if request_dict['include1'] and request_dict['include2']:
            search_doc = {
                "query":{
                    "bool": {
                        "must":[
                            {"term":{"content.keyword": request_dict['keyword1']}},
                            {"term":{"content.keyword": request_dict['keyword2']}},
                        ],
                        "filter":{"range":{"date":{
                            "gte": request_dict["yearmonth1"],
                            "lte": request_dict["yearmonth2"],
                            "format": "yyyy-MM"
                        }}}
                    }
                }
            }
        elif request_dict['include1'] and not request_dict['include2']:
            search_doc = {
                "query":{
                    "bool": {
                        "must":{"term":{"content.keyword": request_dict['keyword1']}},
                        "must_not":{"term":{"content.keyword": request_dict['keyword2']}},
                        "filter":{"range":{"date":{
                            "gte": request_dict["yearmonth1"],
                            "lte": request_dict["yearmonth2"],
                            "format": "yyyy-MM"
                        }}}
                    }
                }
            }
        elif not request_dict['include1'] and request_dict['include2']:
            search_doc = {
                "query":{
                    "bool": {
                        "must_not":{"term":{"content.keyword": request_dict['keyword1']}},
                        "must":{"term":{"content.keyword": request_dict['keyword2']}},
                        "filter":{"range":{"date":{
                            "gte": request_dict["yearmonth1"],
                            "lte": request_dict["yearmonth2"],
                            "format": "yyyy-MM"
                        }}}
                    }
                }
            }
        else:
            search_doc = {
                "query":{
                    "bool": {
                        "must_not":[
                            {"term":{"content.keyword": request_dict['keyword1']}},
                            {"term":{"content.keyword": request_dict['keyword2']}},
                        ],
                        "filter":{"range":{"date":{
                            "gte": request_dict["yearmonth1"],
                            "lte": request_dict["yearmonth2"],
                            "format": "yyyy-MM"
                        }}}
                    }
                }
            }
    elif request_dict['operation'] == 'or':
        if request_dict['include1'] and request_dict['include2']:
            search_doc = {
                "query":{
                    "bool": {
                        "should":[
                            {"term":{"content.keyword": request_dict['keyword1']}},
                            {"term":{"content.keyword": request_dict['keyword2']}},
                        ],
                        "filter":{"range":{"date":{
                            "gte": request_dict["yearmonth1"],
                            "lte": request_dict["yearmonth2"],
                            "format": "yyyy-MM"
                        }}}
                    }
                }
            }
        elif request_dict['include1'] and not request_dict['include2']:
            search_doc = {
                "query":{
                    "bool": {
                        "should":[
                            {"term":{"content.keyword": request_dict['keyword1']}},
                            {"bool": {"must_not": {"term":{"content.keyword": request_dict['keyword2']}}}}
                        ],
                        "filter":{"range":{"date":{
                            "gte": request_dict["yearmonth1"],
                            "lte": request_dict["yearmonth2"],
                            "format": "yyyy-MM"
                        }}}
                    }
                }
            }
        elif not request_dict['include1'] and request_dict['include2']:
            search_doc = {
                "query":{
                    "bool": {
                        "should":{"bool": {"must_not": {"term":{"content.keyword": request_dict['keyword1']}}}},
                        "should":{"term":{"content.keyword": request_dict['keyword2']}},
                        "filter":{"range":{"date":{
                            "gte": request_dict["yearmonth1"],
                            "lte": request_dict["yearmonth2"],
                            "format": "yyyy-MM"
                        }}}
                    }
                }
            }
        else:
            search_doc = {
                "query":{
                    "bool": {
                        "should":{"bool": 
                            {"must_not": [
                                {"term":{"content.keyword": request_dict['keyword1']}},
                                {"term":{"content.keyword": request_dict['keyword2']}},
                            ]
                        }},
                        "filter":{"range":{"date":{
                            "gte": request_dict["yearmonth1"],
                            "lte": request_dict["yearmonth2"],
                            "format": "yyyy-MM"
                        }}}
                    }
                }
            }
    # 加个filter_path可以避免返回无用数据
    search_res = es.search(index="try_index", body=search_doc, filter_path=['hits.hits._id', 'hits.hits._source'])
    search_res = eval(str(search_res))
    search_res = search_res['hits']['hits']
    print([s['_id'] for s in search_res])
    search_res_source = [s['_source'] for s in search_res]
    return search_res_source


if __name__ == "__main__":
    es = Elasticsearch([{'host':'localhost', 'port':9200}])
    print(es)
    # create_index()
    store_data()
    # print("-------")