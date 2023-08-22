import json
import os

import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urljoin, urlparse
from custom_llm import CustomLLM
from llama_index.text_splitter import TokenTextSplitter
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

BROWSERLESS_API = os.environ.get("BROWSERLESS_API")
URL = os.environ.get("URL_ENDPOINT")


def scrape_website(url: str):
    print("Scraping website...")
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    data = {
        "url": url,
        "elements": [{"selector": "body"}]
    }

    data_json = json.dumps(data)

    post_url = f"https://chrome.browserless.io/scrape?token={BROWSERLESS_API}"
    response = requests.post(post_url, headers=headers, data=data_json)

    if response.status_code == 200:
        print("scraping completed successfully")
        result = response.content
        data_str = result.decode('utf-8')
        data_dict = json.loads(data_str)
        html = data_dict['data'][0]['results'][0]['html']
        return html
    else:
        print(f"HTTP request failed with status code {response.status_code}")


def html_to_markdown(html):
    convertor = html2text.HTML2Text()
    convertor.ignore_links = False
    markdown = convertor.handle(html)
    markdown = markdown.replace("\n\n", "<br>")
    # markdown = markdown.replace("\n", "")
    return markdown


def get_base_url(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url


def convert_to_absolute_url(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')

    for img_tag in soup.find_all('img'):
        if img_tag.get('src'):
            src = img_tag.get('src')
            if src.startswith(('http://', 'https://')):
                continue
            absolute_url = urljoin(base_url, src)
            img_tag['src'] = absolute_url
        elif img_tag.get('data-src'):
            src = img_tag.get('data-src')
            if src.startswith(('http://', 'https://')):
                continue
            absolute_url = urljoin(base_url, src)
            img_tag['data-src'] = absolute_url

    for link_tag in soup.find_all('a'):
        href = link_tag.get('href')
        if href is not None:
            if href.startswith(('http://', 'https://')):
                continue
            absolute_url = urljoin(base_url, href)
            link_tag['href'] = absolute_url

    updated_html = str(soup)

    return updated_html


def get_markdown_from_url(url):
    base_url = get_base_url(url)
    html = scrape_website(url)
    updated_html = convert_to_absolute_url(html, base_url)
    markdown = html_to_markdown(updated_html)
    return markdown


def retrieve_chunk(markdown, query):
    print("Implementing RAG")
    text_splitter = TokenTextSplitter(
        separator="\n",
        chunk_size=1024,
        chunk_overlap=20,
        backup_separators=["\n\n", ".", ","]
    )
    texts = text_splitter.split_text(markdown)
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    context_embeddings = model.encode(texts)
    query_embedding = model.encode([query])
    num_relevant = 5
    similarities = cosine_similarity(query_embedding, context_embeddings)[0]
    # using only 3 most relevant chunk
    most_similar_indices = np.argsort(similarities)[-num_relevant:][::-1][:3]
    retrieved_text = [texts[i] for i in most_similar_indices]
    print("RAG performed successfully")
    # Other more effective but slow method below
    '''
    from InstructorEmbedding import INSTRUCTOR
    from langchain.embeddings import HuggingFaceInstructEmbeddings

    model_name = "hkunlp/instructor-large"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    hf = HuggingFaceInstructEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs)
    db_instructEmbedd = FAISS.from_texts(texts, hf)
    retriever = db_instructEmbedd.as_retriever(search_kwargs={"k": 3})
    docs = retriever.get_relevant_documents(query)
    retrieved_text = [doc.page_content for doc in docs]
    '''
    return retrieved_text


def generate_answer(query, max_tokens, retrieved_text):

    model = CustomLLM(url=urljoin(URL, "generate"), max_tokens=max_tokens)
    template = """SYSTEM: {docs}
You are a helpful assistant, above is some context, 
Please answer the question, and make sure you follow ALL of the rules below:
1. Answer the questions only based on context provided, do not make things up
2. Answer questions in a helpful manner that straight to the point, with clear structure & all relevant information that might help users answer the question
3. Answer should be formatted in Markdown
4. If there are relevant images, video, links, they are very important reference data, please include them as part of the answer
5. Please include the images, videos and links as part of the answer

User: {query}
Assistant (formatted in Markdown):
    """
    prompt = template.format(docs=retrieved_text, query=query)
    res = model(prompt)
    return res.replace("\n", "<br>")


def run(query, url, max_tokens=None):
    markdown = get_markdown_from_url(url)
    retrieved_text = retrieve_chunk(markdown, query)
    # passing one below because it might get over the context length
    # answer = generate_answer(query, max_tokens, retrieved_text[:1])
    return retrieved_text
