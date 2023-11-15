import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None


def is_valid_section(tag):
    # Heuristic to identify a valid section
    if tag.name in ["section", "article", "p"]:
        if tag.get('class', None):
            class_names = [cls.lower() for cls in tag.get('class')]
            if 'footer' in class_names or 'header' in class_names or 'menu' in class_names:
                return False
        return True
    return False


def get_text_from_section(tag):
    texts = []
    for elem in tag.descendants:
        if isinstance(elem, NavigableString):
            parent = elem.parent
            if parent.name not in ['script', 'style'] and isinstance(parent, Tag):
                texts.append(elem.strip())
    return ' '.join(texts).strip()


def fetch_image_size(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        return url, image.size[0] * image.size[1]
    except Exception as e:
        return url, 0


def get_images_from_section(tag, base_url):
    image_urls = [urljoin(base_url, img['src'])
                  for img in tag.find_all('img') if img.get('src')]

    largest_image_url = None
    max_size = 0

    with ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(
            fetch_image_size, url): url for url in image_urls}
        for future in as_completed(future_to_url):
            url, size = future.result()
            if size > max_size:
                max_size = size
                largest_image_url = url

    return [largest_image_url] if largest_image_url is not None else []


def chunk_webpage(files):
    chunks = []
    for file_row in files:
        html_content = file_row['content']
        url = file_row['url']
        g_images = file_row['images']

        soup = BeautifulSoup(html_content, 'html.parser')
        body_content = soup.body

        for section in body_content.find_all(is_valid_section):
            text = get_text_from_section(section)
            if g_images != None:
                images = get_images_from_section(section, url)
                images.extend(g_images)
            else:
                images = None
            if text or images:
                chunk = {'text': text, 'images': images, 'url': url}
                chunks.append(chunk)

    # Fallback strategy: Use the entire body content
    if not chunks:
        text = get_text_from_section(body_content)
        images = get_images_from_section(body_content, url)
        images.extend(g_images)
        if text or images:
            chunk = {'text': text, 'images': images, 'url': url}
            chunks.append(chunk)

    return chunks
