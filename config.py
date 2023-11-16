from dataclasses import dataclass, field
from argparse import ArgumentParser
import os


@dataclass
class Config:
    serp_api: str = field(default_factory=lambda: os.getenv("SERP_API"))
    cohere_api: str = field(default_factory=lambda: os.getenv("COHERE_API"))
    retriver_top_k: int = 25
    reranker_top_k: int = 10
    node_chunk_size: int = 8000


parser = ArgumentParser(description="Configuration for the application")

parser.add_argument("--serp_api", type=str,
                    default=os.getenv("SERP_API"), help="SERP API key")
parser.add_argument("--cohere_api", type=str,
                    default=os.getenv("COHERE_API"), help="Cohere API key")
parser.add_argument("--retriver_top_k", type=int,
                    default=25, help="Top K for Retriever")
parser.add_argument("--reranker_top_k", type=int,
                    default=10, help="Top K for Reranker")
parser.add_argument("--node_chunk_size", type=int,
                    default=8000, help="Node chunk size")

args = parser.parse_args()

config = Config(
    serp_api=args.serp_api,
    cohere_api=args.cohere_api,
    retriver_top_k=args.retriver_top_k,
    reranker_top_k=args.reranker_top_k,
    node_chunk_size=args.node_chunk_size
)
