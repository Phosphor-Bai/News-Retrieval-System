import numpy as np
from gensim.models import Word2Vec
import tqdm


def main():
    print("Load model...")
    model = Word2Vec.load("./models/model_word2vec")
    print("Generate vectors...")
    doc_vectors = np.zeros((100000, 100), dtype=float)
    model_vocab = list(model.wv.vocab.keys())
    with open("./data/corpus.txt", "r", encoding="utf-8") as f:
        line = f.readline()
        for line_id in tqdm.tqdm(range(1, 100000)):
            line = eval(line)
            buffer = np.zeros((1, 100), dtype=float)
            word_count = 0
            for word in line:
                if word not in model_vocab:
                    continue
                # 根据DESM公式需要对词向量进行归一化
                buffer += model.wv[word] / np.linalg.norm(model.wv[word])
                word_count += 1
            if word_count > 0:
                buffer /= word_count
                doc_vectors[line_id, :] = buffer
            line = f.readline()
    print("Save vectors...")
    np.save("./models/doc_vectors.npy", doc_vectors)


if __name__ == "__main__":
    main()

