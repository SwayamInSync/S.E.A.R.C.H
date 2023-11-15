from dataclasses import dataclass
import os


@dataclass
class Config:
    serp_api = os.getenv("SERP_API")
    cohere_api = os.getenv("COHERE_API")
    retriver_top_k = 25
    reranker_top_k = 10
    node_chunk_size = 8000


config = Config()
