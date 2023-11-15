from llama_index.node_parser import SimpleNodeParser
from typing import *
from llama_index.data_structs import Node
import requests
from collections import defaultdict
from llama_index import Document

from config import config


def load_and_parse(all_docs):
    documents = []
    for file_row in all_docs:
        url = file_row["url"]
        content = file_row["text"]
        images = file_row['images']

        metadata = defaultdict()
        metadata['URL'] = url
        metadata['images'] = images
        body_text = content
        documents.append(Document(text=body_text, metadata=dict(metadata)))
    return documents


def reader(urls, imgs_links):
    all_pages = []
    for url in urls:
        try:
            res = requests.get(url, timeout=10)
        except:
            continue
        if res.status_code == 200:
            all_pages.append((url, res.text, imgs_links))
    return all_pages


def convert_documents_into_nodes(documents):
    all_nodes = []
    for document in documents:
        parser = SimpleNodeParser.from_defaults(
            chunk_size=config.node_chunk_size, chunk_overlap=50)
        nodes = parser.get_nodes_from_documents([document])
        all_nodes.extend(nodes)
    return all_nodes
