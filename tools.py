import markdown2
from serpapi import GoogleSearch
import threading

from utils import reader, load_and_parse
from parsing_data import chunk_webpage
from config import config


def fetch_search_results(params, output):
    search = GoogleSearch(params)
    output.append(search.get_dict())


def search_the_web(query, include_images):
    params_c = {
        "api_key": config.serp_api,
        "engine": "google",
        "q": query,
        "location": "Delhi, India",
        "google_domain": "google.co.in",
        "gl": "in",
        "hl": "en"
    }
    params_imgs = {
        "api_key": config.serp_api,
        "engine": "google_images",
        "q": query,
        "location": "Delhi, India",
        "google_domain": "google.co.in",
        "gl": "in",
        "hl": "en"
    }

    if include_images:
        results = []
        img_results = []

        thread1 = threading.Thread(
            target=fetch_search_results, args=(params_c, results))

        thread2 = threading.Thread(
            target=fetch_search_results, args=(params_imgs, img_results))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        search_results = results[0] if results else None
        image_results = img_results[0] if img_results else None
    else:
        results = []
        fetch_search_results(params_c, results)
        search_results = results[0] if results else None

    if "organic_results" not in search_results:
        raise Exception("Error in Googling")

    content_links = [item.get('link', None)
                     for item in search_results['organic_results']]

    if include_images:
        imgs_links = [item.get('original', None)
                      for item in image_results['images_results']]
        imgs_links = list(set(imgs_links))

    all_pages = reader(
        content_links[:5], imgs_links[:2] if include_images else None)
    all_docs = [{"url": doc[0], "content": doc[1], "images": doc[2]}
                for doc in all_pages]
    all_chunks = chunk_webpage(all_docs)
    loaded_docs = load_and_parse(all_chunks)
    return loaded_docs


def get_html_content(markdown_text):
    html_content = markdown2.markdown(markdown_text)
    return html_content
