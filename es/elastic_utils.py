from elasticsearch import Elasticsearch
import json


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
    search_res = es.search(index="try_index", body=search_doc)
    search_res = eval(str(search_res))
    search_res_hits = search_res['hits']['hits']
    print([s['_id'] for s in search_res_hits])
    search_res_source = [s['_source'] for s in search_res_hits]
    return search_res_source


if __name__ == "__main__":
    es = Elasticsearch([{'host':'localhost', 'port':9200}])
    print(es)
    # create_index()
    store_data()
    # print("-------")