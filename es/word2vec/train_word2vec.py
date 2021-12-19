import json
import tqdm
from gensim.models import Word2Vec

    
class MyCorpus:
    def __iter__(self):
        f = open('./data/corpus.txt', 'r', encoding='utf-8')
        line = f.readline()
        while line:
            yield eval(line)
            line = f.readline()

def build_dataset_single_doc(line_content):
    doc = []
    for s in line_content:
        sentence = s[0].split()
        for w in sentence:
            if w.find('_') == 0:
                continue    # white_space
            w = w.split('_')
            if len(w) == 2:
                all_chinese = True
                for ch in w[0]:
                    if not '\u4e00' <= ch <= '\u9fff':
                        all_chinese = False
                        break
                if all_chinese:
                    doc.append(w[0])
    return doc

def build_dataset():
    print("Process news data...")
    data_path = "./data/rmrb_2000-2015.jsonl"
    g = open('./data/corpus.txt', 'w', encoding='utf-8')
    with open(data_path, 'r', encoding='utf-8') as f:
        line = f.readline()
        for counter in tqdm.tqdm(range(1, 100000)):
            line_data = json.loads(line)
            line_content = line_data['content'][1:]
            g.write(str(build_dataset_single_doc(line_content)))
            g.write('\n')
            line = f.readline()
    g.close()

def train_word2vec():
    print("Get corpus...")
    sentences = MyCorpus()
    print("Train model...")
    model = Word2Vec(sentences=sentences, size=100, window=5, min_count=5, sg=1, hs=1, alpha=0.025, min_alpha=0.0001)
    model.save('./models/model_word2vec')

if __name__ == "__main__":
    build_dataset()
    train_word2vec()