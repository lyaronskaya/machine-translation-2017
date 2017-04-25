import sys
from embeddings import Vocab, WordEmbedding
import numpy as np

def load_example_sets(path):
    # Loads list of pairs per line.
    return [[tuple(pair.split()) for pair in line.strip().split('\t')] for line in open(path)]

def load_labels(path):
    # Loads a label for each line (-1 indicates the pairs do not form a relation).
    return [int(label) for label in open(path)]

def label_all_examples_as_not_a_relation(examples):
    return [-1 for example in examples]

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print "Usage ./detect_relations.py vocab_file embedding_file train_data train_labels test_data"
        sys.exit(0)

    # Load vocab and embedding (these are not used yet!)
    vocab = Vocab(sys.argv[1])
    embedding = WordEmbedding(vocab, sys.argv[2])

    # Loads training data and labels.
    training_examples = load_example_sets(sys.argv[3])
    training_labels = load_labels(sys.argv[4])
    assert len(training_examples) == len(training_labels), "Expected one label for each line in training data."

    test_examples = load_example_sets(sys.argv[5])
    
    train_means = []
    train_stds = []
    for i in range(len(training_labels)):
        differences = np.array([embedding.Projection(w1.decode('utf-8')) - embedding.Projection(w2.decode('utf-8')) for w1, w2 in training_examples[i]])
        train_means.append(differences.mean(axis=0)) 
        train_stds.append(differences.std(axis=0)) 
    test_labels = []
    for i in range(len(test_examples)):
        differences = np.array([embedding.Projection(w1.decode('utf-8')) - embedding.Projection(w2.decode('utf-8')) for w1, w2 in test_examples[i]])
        example_means = differences.mean(axis=0, keepdims=True)
        example_stds = differences.std(axis=0, keepdims=True)

        mean_dists = np.linalg.norm(train_means - example_means, axis=1)
        std_dists = np.linalg.norm(train_stds - example_means, axis=1)
        if training_labels[np.argmin(std_dists)] == -1:
            label = -1
        else:
            label = training_labels[np.argmin(mean_dists)]
        test_labels.append(label)
        
    with open('en_morph.test.my_labels', 'w') as f:
        f.write('\n'.join(map(str, test_labels)))
