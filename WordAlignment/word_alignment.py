#!/usr/bin/python
import os, sys, codecs, utils
import argparse
from math import log
from models import *

def get_posterior_distribution_for_trg_token(trg_index, src_tokens, trg_tokens,
                                             prior_model, translation_model):
    "Compute the posterior distribution over alignments for trg_index: P(a_j = i|f_j, e)."
    assert False, "I've never used this."
    # marginal_prob = p(f_j|e) 
    # posterior_probs[i] = p(a_j = i|f_j, e)

def compute_prior_for_model(prior_model, src_idx, trg_idx, src_len, trg_len, src_tokens, trg_tokens, src_tags, trg_tags):
    if prior_model.__class__.__name__ == 'TagsPriorModel':
        return prior_model.get_prior_prob(src_tags[src_idx], trg_tags[trg_idx])
    elif prior_model.__class__.__name__ == 'SourcePOSPriorModel':
        return prior_model.get_prior_prob(src_tags[src_idx], src_tokens[src_idx], trg_tokens[trg_idx]) 
    elif prior_model.__class__.__name__ == 'ComplexPriorModel':
        return  prior_model.get_prior_prob(src_idx, trg_idx, src_len, trg_len)
    else:
        assert False, "Not implemented model"
    
def get_posterior_alignment_matrix(src_tokens, trg_tokens, prior_model, translation_model, src_tags=None, trg_tags=None):
    "For each target token compute the posterior alignment probability: p(a_j=i | f_j, e)"
    # 1. Prior model assumes that a_j is independent of all other alignments.
    # 2. Translation model assume each target word is generated independently given its alignment.

    J = len(trg_tokens)
    I  = len(src_tokens)
    
    posterior_matrix = np.array([[compute_prior_for_model(prior_model, i, j, I, J, src_tokens, trg_tokens, src_tags, trg_tags) * translation_model.get_conditional_prob(src_tokens[i], trg_tokens[j]) for i in range(I)] for j in range(J)])
    posterior_matrix = posterior_matrix / (np.sum(posterior_matrix, axis=-1, keepdims=True) + 1e-15)
    
    log_t_matrix = np.log(posterior_matrix + 1e-15)
    sentence_marginal_log_likelihood = np.sum(posterior_matrix * log_t_matrix)
    return sentence_marginal_log_likelihood, posterior_matrix



def collect_expected_statistics(src_corpus, trg_corpus, prior_model, translation_model, src_corpus_tags=None, trg_corpus_tags=None):
    "Infer posterior distribution over each sentence pair and collect statistics: E-step"
    corpus_marginal_log_likelihood = 0.0
    # 1. Infer posterior
    # 2. Collect statistics in each model.
    # 3. Update log prob
    for i, (e, f) in enumerate(zip(src_corpus, trg_corpus)):
        if src_corpus_tags != None:
            sentence_log_likelihood, posterior_matrix = get_posterior_alignment_matrix(e, f, prior_model, translation_model, src_corpus_tags[i], trg_corpus_tags[i])
        else:
            sentence_log_likelihood, posterior_matrix = get_posterior_alignment_matrix(e, f, prior_model, translation_model)

        prior_model.collect_statistics(len(e), len(f), posterior_matrix)
        translation_model.collect_statistics(e, f, posterior_matrix)
        corpus_marginal_log_likelihood += sentence_log_likelihood
    return corpus_marginal_log_likelihood

def reestimate_models(prior_model, translation_model):
    "Recompute parameters of each model: M-step"
    prior_model.recompute_parameters()
    translation_model.recompute_parameters()

def estimate_models(src_corpus, trg_corpus, prior_model, translation_model, num_iterations):
    "Estimate models iteratively."
    for iteration in range(num_iterations):
        corpus_log_likelihood = collect_expected_statistics(
            src_corpus, trg_corpus, prior_model, translation_model)
        reestimate_models(prior_model, translation_model)
        if iteration > 0:
            print "corpus log likelihood: %1.3f" % corpus_log_likelihood
    return prior_model, translation_model

def align_sentence_pair(src_tokens, trg_tokens, prior_probs, translation_probs):
    "For each target token, find the src_token with the highest posterior probability."
    # Compute the posterior distribution over alignments for all target tokens.
    corpus_log_prob, posterior_matrix = get_posterior_alignment_matrix(
        src_tokens, trg_tokens, prior_probs, translation_probs)
    # For each target word find the src index with the highest posterior probability.
    alignments = []
    for trg_index, posteriors in enumerate(posterior_matrix):
        best_src_index = np.argmax(posteriors)
        alignments.append((best_src_index, trg_index))
    return alignments

def align_corpus_given_models(src_corpus, trg_corpus, prior_model, translation_model):
    "Align each sentence pair in the corpus in turn."
    alignments = []
    for i in range(len(src_corpus)):
        these_alignments = align_sentence_pair(
            src_corpus[i], trg_corpus[i], prior_model, translation_model)
        alignments.append(these_alignments)
    return alignments

def align_corpus(src_corpus, trg_corpus, num_iterations, prior_model, translation_model):
    "Learn models and then align the corpus using them."
    prior_model, translation_model = estimate_models(
        src_corpus, trg_corpus, prior_model, translation_model, num_iterations)
    return align_corpus_given_models(src_corpus, trg_corpus, prior_model, translation_model)

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print "Usage: python word_alignment.py src_corpus trg_corpus iterations output_prefix PriorModelClass [1 if use NULL] [filename to dump translational probas]."
        sys.exit(0)
    src_corpus = utils.read_all_tokens(sys.argv[1])
    trg_corpus = utils.read_all_tokens(sys.argv[2])
    num_iterations = int(sys.argv[3])
    output_prefix = sys.argv[4]
    assert len(src_corpus) == len(trg_corpus), "Corpora should be same size!"
    prior_model_name = sys.argv[5]
    use_null = len(sys.argv) > 6
    dump_translational_model = len(sys.argv) > 7
    
    if use_null:
        src_corpus = [['_NULL_'] + e for e in src_corpus]
        
    prior_model = eval(prior_model_name)()
    translation_model = TranslationModel(src_corpus, trg_corpus)
    
    alignments = align_corpus(src_corpus, trg_corpus, num_iterations, prior_model, translation_model)
    
    #remove NULL alignment
    if use_null:
        alignments = [[(a[0] - 1, a[1]) for a in alignment if a[0] > 0] for alignment in alignments]
       
    if dump_translational_model:
        with open(sys.argv[7], 'w') as f:
            f.write('\n'.join([' '.join([e, f, str(prob)]) for e, d in translation_model._trg_given_src_probs.iteritems() for f, prob in d.iteritems()]))

    utils.output_alignments_per_test_set(alignments, output_prefix)
