import numpy as np
from gensim.models import Word2Vec


def main():
    print("Load model...")
    model = Word2Vec.load("./models/model_word2vec")
