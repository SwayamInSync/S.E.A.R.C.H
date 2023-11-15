'''
This script is a demo of utilizing SOTA dense retriver: DRAGON
Using this generally does not require a ReRanker for post-processing
'''

import torch
import random
from transformers import AutoTokenizer, AutoModel

from utils import convert_documents_into_nodes
from tools import search_the_web


tokenizer = AutoTokenizer.from_pretrained('facebook/dragon-plus-query-encoder')
query_encoder = AutoModel.from_pretrained('facebook/dragon-plus-query-encoder')
context_encoder = AutoModel.from_pretrained(
    'facebook/dragon-plus-context-encoder')


def get_ctx_embedding(nodes):
    contexts = [node.text for node in nodes]
    ctx_input = tokenizer(contexts, padding=True,
                          truncation=True, return_tensors="pt", max_length=512)
    ctx_emb = context_encoder(**ctx_input).last_hidden_state[:, 0, :]
    return ctx_emb


def get_query_embedding(query):
    query = tokenizer(query, return_tensors="pt")
    query_emb = query_encoder(**query).last_hidden_state[:, 0, :]
    return query_emb


if __name__ == "__main__":
    query = "What is huggingface"
    loaded_docs = search_the_web(query, False)
    nodes = convert_documents_into_nodes(loaded_docs)
    random_nodes = random.sample(nodes, k=10)
    ctx_emb = get_ctx_embedding(random_nodes)
    query_emb = get_query_embedding(query)
    _, top_indices = torch.topk(query_emb@ctx_emb.T, k=4)
    relevant_nodes = [random_nodes[i] for i in top_indices[0]]
    print([t.text for t in relevant_nodes])
