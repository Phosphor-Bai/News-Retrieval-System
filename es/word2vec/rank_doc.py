import numpy as np
from gensim.models import Word2Vec


def rank_doc(keywords, ids, scores):
    top_score = scores[0]
    scores = [s/top_score for s in scores]     # 归一化
    print("Load model...")
    model = Word2Vec.load("./es/models/model_word2vec")
    model_vocab = list(model.wv.vocab.keys())

    print("Load doc vectors...")
    doc_vectors = np.load("./es/models/doc_vectors.npy")

    print("Generate DESM score...")
    desm_scores = {}
    for index, id in enumerate(ids):
        doc_vector = doc_vectors[int(id), :]
        word_count = 0
        desm_score = 0
        for keyword in keywords:
            if keyword not in model_vocab:
                continue
            query_vector = model.wv[keyword] / np.linalg.norm(model.wv[keyword])
            desm_score += np.dot(query_vector, doc_vector)
            word_count += 1
        if word_count > 0:
            desm_score /= word_count
        desm_scores[id] = desm_score * 0.3 + scores[index] * 0.7
    # 根据DESM相关度与elasticsearch使用的Lucene Practical Scoring Function相关度（已归一化）之和排序返回结果
    desm_scores_item = sorted(desm_scores.items(), key=lambda d:d[1], reverse=True)
    ids_by_desm = [d[0] for d in desm_scores_item]
    return ids_by_desm

