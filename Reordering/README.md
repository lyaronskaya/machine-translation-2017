# Reordering
Implementation of baseline reorderers gives at most 0.796 kendall's tau.
To achieve more that 0.8 I've also implemented reordering based on rules for SOV languages [article](http://www.aclweb.org/anthology/N09-1028).

## Download data
```
wget https://www.dropbox.com/s/dwwnv1qgak975sc/reordering.tar.gz?dl=0 -O reordering.tar.gz
tar -kxvzf reordering.tar.gz
```

## Evaluation

| Reordering       | Kendall's tau |
|------------------|---------------|
|DoNothingReorderer|     0.707     |
|ReverseReorderer  |     0.581     |
|HeadFinalReorderer|     0.796     |
|SOVReorderer      |     0.816     |
