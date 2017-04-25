# Word alignment 

Implementation of word alignment models, evaluation on English-Czech data.

## Download data
```
wget https://www.dropbox.com/s/ng1trp7vfzto9wi/wa.tar.gz?dl=0 -O wa.tar.gz
tar -kxvzf wa.tar.gz
wget https://www.dropbox.com/s/s40tcptp4nhku93/data100K.tar.gz?dl=0 -O data100K.tar.gz
tar -xvzf data100K.tar.gz
wget https://www.dropbox.com/s/x230lw2yj616258/additional.tar.gz?dl=0 -O additional.tar.gz
tar -xvzf additional.tar.gz

```

## Implemented models
Markup : 1. IBM Model 1 
         2. IBM Model 1 with complex prior P(j | i, I, J) where I divided values of I and J by the value of bin in division by percentiles(so in total I had 10 values of I and 10 values of J).
         3. previous model with lemmas instead of tokens for chech
         4. IBM Model 1 with prior P(tag(f) | tag(e)) and lemmas for chech
         5. Second model with '_NULL_' in the beginning of every source sentence


## Evaluation
For 10K dataset:

| Model | AER |
|-------|-----|
|1.     |0.561|
|2.     |0.514|
|3.     |0.431|
|4.     |0.468|
|5.     |0.493|

You can see that the use of lemmas decreases the error.
At the same time prior model with tags works worse than the prior conditioned on source and target lengths (may be P(j | i, I, J) is more accurate than P(tag(f) | tag(e))).
It looks like the use of '_NULL_' on small dataset just adds noise to the model. 