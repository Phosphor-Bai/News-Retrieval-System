from django.template import loader
from django.http import HttpResponse
from . import elastic_utils


def index(request):
    template = loader.get_template('es/index.html')
    context = {}
    return HttpResponse(template.render(context, request))

def search_results(request):
    yearmonth1 = request.POST['yearmonth1']
    yearmonth2 = request.POST['yearmonth2']
    request_dict = {
        'yearmonth1': request.POST['yearmonth1'], 'yearmonth2': request.POST['yearmonth2'],
        'include1': request.POST['include1']=="True", 'keyword1': request.POST['keyword1'],
        'operation': request.POST['operation'],
        'include2': request.POST['include2']=="True", 'keyword2': request.POST['keyword2']
    }
    
    result_list = elastic_utils.search_data(request_dict=request_dict)
    for res in result_list:
        string = ''
        res['content'] = string.join(res['content'])
    template = loader.get_template('es/search_result.html')
    if request_dict['operation'] == 'only':
        if request_dict['include1']:
            context_keywords = '<包含>' + request_dict['keyword1']
        else:
            context_keywords = '<不包含>' + request_dict['keyword1']
    else:
        if request_dict['include1']:
            context_keywords = '<包含>' + request_dict['keyword1']
        else:
            context_keywords = '<不包含>' + request_dict['keyword1']
        if request_dict['operation'] == 'and':
            context_keywords += ' 且 '
        else:
            context_keywords += ' 或 '
        if request_dict['include2']:
            context_keywords += '<包含>' + request_dict['keyword2']
        else:
            context_keywords += '<不包含>' + request_dict['keyword2']

    context = {
        'pub_year': str(yearmonth1)+' 至 '+str(yearmonth2),
        'keywords': context_keywords,
        'result_list': result_list,
    }
    return HttpResponse(template.render(context, request))

def word2vec_search_results(request):
    result_list_raw, result_list_ranked = elastic_utils.search_more(keywords_str=request.POST['keywords'], yearmonth1=request.POST['yearmonth1'], yearmonth2=request.POST['yearmonth2'])
    for res in result_list_raw:
        string = ''
        res['content'] = string.join(res['content'])
    template = loader.get_template('es/word2vec_result.html')
    for res in result_list_ranked:
        string = ''
        res['content'] = string.join(res['content'])
    template = loader.get_template('es/word2vec_result.html')

    context = {
        'pub_year': str(request.POST['yearmonth1'])+' 至 '+str(request.POST['yearmonth2']),
        'keywords': request.POST['keywords'],
        'result_list_raw': result_list_raw,
        'result_list_ranked': result_list_ranked,
    }
    return HttpResponse(template.render(context, request))
