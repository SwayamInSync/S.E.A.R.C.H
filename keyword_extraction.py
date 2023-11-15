import spacy
from collections import Counter
from transformers import pipeline, AutoTokenizer
import numpy as np


def extract_keywords_huggingface(query):
    model_name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    feature_extractor = pipeline("feature-extraction", model=model_name)

    inputs = tokenizer(query, return_tensors="pt")
    outputs = feature_extractor(query)

    token_embeddings = np.squeeze(outputs, axis=0)
    avg_embeddings = np.mean(token_embeddings, axis=1)

    top_indices = avg_embeddings.argsort()[-10:][::-1]
    keywords = [tokenizer.decode([inputs.input_ids[0][idx]])
                for idx in top_indices]

    return keywords


def extract_keywords_vanilla(query):
    nlp = spacy.load("en_core_web_sm")

    doc = nlp(query)
    ner_keywords = [ent.text for ent in doc.ents]

    pos_tags = ['NOUN', 'PROPN', 'ADJ']
    key_phrases = [token.text for token in doc if token.pos_ in pos_tags]

    combined_keywords = list(set(ner_keywords + key_phrases))

    word_freq = Counter(combined_keywords)
    most_common_keywords = [word for word, freq in word_freq.most_common(10)]

    return most_common_keywords
