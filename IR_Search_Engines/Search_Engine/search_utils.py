import nltk
import math
import logging
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, SnowballStemmer
from django.db.models import Count
from .models import Document, DocumentChunk

logger = logging.getLogger(__name__)

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

class TextProcessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()
        self.tokenizer = word_tokenize
        self.min_word_length = 3

    def preprocess(self, text):
        try:
            if not text:
                return []

            tokens = self.tokenizer(str(text).lower())
            processed = []
            for token in tokens:
                if token.isalnum() and len(token) >= self.min_word_length and token not in self.stop_words:
                    processed.append(self.stemmer.stem(token))
            
            return processed

        except Exception as e:
            logger.error(f"Text processing error: {e}")
            return []

text_processor = TextProcessor()

def build_inverted_index(documents):
    inverted_index = defaultdict(lambda: {'df': 0, 'postings': defaultdict(list)})
    
    for doc in documents:
        try:
            content = getattr(doc, 'content', '') or getattr(doc, 'text', '')
            tokens = text_processor.preprocess(content)
            doc_id = doc.id
            for position, term in enumerate(tokens):
                if doc_id not in inverted_index[term]['postings']:
                    inverted_index[term]['df'] += 1
                inverted_index[term]['postings'][doc_id].append(position)
                
        except Exception as e:
            logger.error(f"Error processing document {doc.id}: {e}")
    
    return inverted_index

def calculate_tfidf(inverted_index, total_docs):
    for term, data in inverted_index.items():
        for doc_id, positions in data['postings'].items():
            tf = 1 + math.log10(len(positions)) if positions else 0
            idf = math.log10((total_docs + 1) / (data['df'] + 0.5))
            data['postings'][doc_id] = tf * idf
    return inverted_index

def search(query, inverted_index, documents, top_n=10):
    query_terms = text_processor.preprocess(query)
    if not query_terms:
        return []

    scores = defaultdict(float)
    for term in query_terms:
        if term in inverted_index:
            for doc_id, weight in inverted_index[term]['postings'].items():
                scores[doc_id] += weight

    doc_lengths = defaultdict(float)
    for term, data in inverted_index.items():
        for doc_id, weight in data['postings'].items():
            doc_lengths[doc_id] += weight**2
            
    results = []
    for doc in documents:
        doc_id = doc.id
        if doc_id in scores:
           doc_lengths[doc_id] += 1e-6
           results.append((doc_id, scores[doc_id] / math.sqrt(doc_lengths[doc_id])))
        else:
            results.append((doc_id, 0.0))

    return sorted(results, key=lambda x: x[1], reverse=True)[:top_n]
