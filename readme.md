# 新闻检索系统

## 基础系统
需要安装elastic search、Django及elasticsearch-py包。

将jsonl格式的新闻文件放在`es/data/`路径下，运行elasticsearch后，使用python运行`es/elastic_utils.py`导入文档，导入完成后使用`python manage.py runserver`运行系统。

## word2vec重排序检索
对于基础检索结果，使用word2vec模型根据Dual Embedding Space Model（DESM）方法对检索结果进行重排序。需要安装gensim以训练word2vec模型。

### word2vec训练
以下操作均在`es`路径中完成。
使用python运行`word2vec/train_word2vec.py`训练模型（100维，使用skip-gram和hierarchical softmax），模型将存储于`models/model_word2vec`。

### 文档向量构建
DESM方法中，文档的向量表示计算方法为$vec(D) = \frac{1}{|D|}\sum_{d_j \in D} \frac{vec(d_j)}{||vec(d_j)||}$，使用python运行使用python运行`word2vec/build_doc_vector.py`，会将所有的文档向量存储为(100000, 100)的`np.array`，存储于`/es/models/doc_vectors.npy`。

### 检索结果相关性计算
word2vec检索将调用`es/elatic_utils.py`中的新函数`search_more`，获得DESM相关度（$DESM(Q, D) = \frac{1}{|Q|} \sum_{q_i \in Q} \frac{vec(q_i)^T vec(D)}{||vec(q_i)||||vec(D)||}$）与原始相关度加权平均得到的相关度结果，对检索结果重排序后返回，并分两栏展示原始结果top10和重排序后top10。​

