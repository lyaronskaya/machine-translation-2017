# Models for word alignment
from collections import defaultdict
from copy import deepcopy
import numpy as np

class TranslationModel(object):
    "Models conditional distribution over trg words given a src word."

    def __init__(self, src_corpus, trg_corpus):
        self._src_trg_counts = defaultdict(lambda: defaultdict(lambda: 0)) # Statistics
        self._trg_given_src_probs = defaultdict(lambda: defaultdict(lambda: 1.)) # Parameters

    def get_conditional_prob(self, src_token, trg_token):
        "Return the conditional probability of trg_token given src_token."
        return self._trg_given_src_probs[src_token][trg_token]

    def collect_statistics(self, src_tokens, trg_tokens, posterior_matrix):
        "Accumulate fractional alignment counts from posterior_matrix."
        assert len(posterior_matrix) == len(trg_tokens)
        for posterior in posterior_matrix:
            assert len(posterior) == len(src_tokens)
        for i, e_i in enumerate(src_tokens):
            for j, f_j in enumerate(trg_tokens):
                self._src_trg_counts[e_i][f_j] += posterior_matrix[j][i] 

    def recompute_parameters(self):
        "Reestimate parameters from counts then reset counters"
        #assert False, "Recompute parameters in self._trg_given_src_probs here."
        self._trg_given_src_probs = deepcopy(self._src_trg_counts)
        for e, d in self._trg_given_src_probs.iteritems():
            norm_constant = sum(d.values())
            for k in d.keys():
                d[k] = d[k] / (norm_constant + 1e-10)
        self._src_trg_counts = defaultdict(lambda: defaultdict(lambda: 0))
        

class PriorModel(object):
    "Models the prior probability of an alignment given only the sentence lengths and token indices."

    def __init__(self):
        "Add counters and parameters here for more sophisticated models."
        self._distance_counts = defaultdict(lambda: defaultdict(lambda: 0))
        self._distance_probs = defaultdict(lambda: defaultdict(lambda: 1))

    def get_prior_prob(self, src_index, trg_index, src_length, trg_length):
        "Returns a uniform prior probability."
        return 1.0 / src_length

    def collect_statistics(self, src_length, trg_length, posterior_matrix):
        "Extract the necessary statistics from this matrix if needed."
        pass

    def recompute_parameters(self):
        "Reestimate the parameters and reset counters."
        pass
    
    
class ComplexPriorModel(PriorModel):
    "Models the prior probability of an alignment given only the source and target sentences' lengths and source token indices."

    def __init__(self):
        super(ComplexPriorModel, self).__init__()
        
    src_percentiles = np.array([6.0, 10.0, 14.0, 17.0, 21.0, 25.0, 30.0, 35.0, 44.0, 99.0])
    trg_percentiles = np.array([5.0, 9.0, 12.0, 15.0, 18.0, 22.0, 26.0, 31.0, 39.0, 91.0])
    
    @staticmethod
    def src_len_to_idx(sent_len):
        return np.cumsum(np.array(ComplexPriorModel.src_percentiles) <= sent_len)[-1]

    @staticmethod
    def trg_len_to_idx(sent_len):
        return np.cumsum(np.array(ComplexPriorModel.trg_percentiles) <= sent_len)[-1]

    def get_prior_prob(self, src_index, trg_index, src_length, trg_length):
        return self._distance_probs[(src_index, ComplexPriorModel.src_len_to_idx(src_length), ComplexPriorModel.trg_len_to_idx(trg_length))][trg_index]

    def collect_statistics(self, src_length, trg_length, posterior_matrix):
        "Extract the necessary statistics from this matrix if needed."
        for i in range(src_length):
            for j in range(trg_length):
                self._distance_counts[(i, ComplexPriorModel.src_len_to_idx(src_length), ComplexPriorModel.trg_len_to_idx(trg_length))][j] += posterior_matrix[j][i] 


class TagsPriorModel(PriorModel):
    "Models the prior probability of an alignment given source POS and target POS"
    
    def __init__(self, src_tags, trg_tags):
        super(TagsPriorModel, self).__init__()
        
        for e_tags, f_tags in zip(src_tags, trg_tags):
            for e_tag in e_tags:
                for f_tag in f_tags:
                    self._distance_counts[e_tag][f_tag] += 1
                    
        for e, d in self._distance_counts.iteritems():
            norm_constant = sum(d.values())
            for k in d.keys():
                d[k] /= norm_constant + 1e-10
                
        self._distance_probs = self._distance_counts

    def get_prior_prob(self, src_tag, trg_tag):
        return self._distance_probs[src_tag][trg_tag]
    
    
class SourcePOSPriorModel(PriorModel):
    "Models the prior probability of an alignment given source token POS and index"
    
    def __init__(self, src_tags, trg_tags, src_corpus, trg_corpus):
        super(SourcePriorModel, self).__init__()
        
        for i in range(len(src_corpus)):
            for j, e_tag in enumerate(src_tags[i]):
                for k, f_tag in enumerate(trg_tags[i]):
                    self._distance_counts[(e_tag, src_corpus[i][j])][trg_corpus[i][k]] += 1
                    
        for e, d in self._distance_counts.iteritems():
            norm_constant = sum(d.values())
            for k in d.keys():
                d[k] /= norm_constant + 1e-10
                
        self._distance_probs = self._distance_counts

    def get_prior_prob(self, src_tag, src_token, trg_token):
        return self._distance_probs[(src_tag, src_token)][trg_token]

