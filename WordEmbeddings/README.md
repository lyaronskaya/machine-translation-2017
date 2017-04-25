# WordEmbeddings
Implementation of simple relations detections using mean of differences between two words as cluster of relation. A pair is classified as random(doesn't belong to a common relation) if it's std 

## Download data
```
wget https://www.dropbox.com/s/42ybm1ot03ygcav/hw3.tar.gz?dl=0 -O hw3.tar.gz
tar -kxvzf hw3.tar.gz
```
## Run scripts
To classify relations
```
python detect_relations.py hw3/embeddings/wiki-en/vocab-cbow-0-64-2-800.txt hw3/relational_data/en_morph.train hw3/relational_data/en_morph.train.labels hw3/relational_data/en_morph.test
```
To evaluate predictions
```
evaluate.py hw3/relational_data/en_morph.test.labels hw3/en_morph.test.my_labels
```
## Evaluation

Detecting relations scores

| Language | Precision | Recall | F1   |
|----------|-----------|--------|------|
| English  |   0.75    |   1.0  | 0.875|
| Russian  |   0.995   |   1.0  | 0.997|
| French   |   1.0     |   1.0  | 1.0  |

Detecting and labeling relations scores

| Language | Precision | Recall | F1    |
|----------|-----------|--------|-------|
| English  |   0.75    |   1.0  | 0.875 |
| Russian  |   0.941   |  0.947 | 0.944 |
| French   |   0.993   |  0.993 | 0.993 |

It looks like embeddings for french words are better trained.