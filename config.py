'''
1. SERP_API
2. retriver_top_k
3. reranker_top_k
4. node_chunk_size
5. Cohere API
'''

from dataclasses import dataclass, field


@dataclass
class Config:
    serp_api = None
    cohere_api = None
    retriver_top_k = 25
    reranker_top_k = 10
    node_chunk_size = 8000


config = Config()
