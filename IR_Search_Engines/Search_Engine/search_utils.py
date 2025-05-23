import nltk
import math
import logging
from collections import defaultdict, Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

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
            processed = [
                self.stemmer.stem(token)
                for token in tokens
                if token.isalnum() and len(token) >= self.min_word_length and token not in self.stop_words
            ]
            return processed
        except Exception as e:
            logger.error(f"Text processing error: {e}")
            return []

text_processor = TextProcessor()

def build_inverted_index(documents):
    inverted_index = defaultdict(lambda: {'df': 0, 'postings': defaultdict(list)})
    document_lengths = {}
    unique_terms = set()

    for doc in documents:
        try:
            content = getattr(doc, 'content', '') or getattr(doc, 'text', '')
            tokens = text_processor.preprocess(content)
            doc_id = doc.id
            document_lengths[doc_id] = len(tokens)
            term_freqs = Counter(tokens)
            unique_terms.update(term_freqs.keys())

            for position, term in enumerate(tokens):
                inverted_index[term]['postings'][doc_id].append(position)

            for term in term_freqs:
                inverted_index[term]['df'] += 1

        except Exception as e:
            logger.error(f"Error processing document {doc.id}: {e}")

    return inverted_index, document_lengths, unique_terms

def calculate_tfidf(inverted_index, total_docs):
    tfidf_index = defaultdict(dict)
    tf_values = defaultdict(dict)
    idf_values = {}

    for term, data in inverted_index.items():
        idf = math.log10((total_docs + 1) / (data['df'] + 0.5))
        idf_values[term] = idf
        for doc_id, positions in data['postings'].items():
            tf = 1 + math.log10(len(positions)) if positions else 0
            tf_values[term][doc_id] = tf
            tfidf_index[term][doc_id] = tf * idf

    return tfidf_index, tf_values, idf_values

def search(query, tfidf_index, document_lengths, top_n=10):
    query_terms = text_processor.preprocess(query)
    if not query_terms:
        return []

    if len(query_terms) < 3:
        query_terms = (query_terms * 3)[:3]

    scores = defaultdict(float)

    for term in query_terms:
        if term in tfidf_index:
            for doc_id, weight in tfidf_index[term].items():
                scores[doc_id] += weight

    doc_norms = defaultdict(float)
    for term, postings in tfidf_index.items():
        for doc_id, weight in postings.items():
            doc_norms[doc_id] += weight ** 2

    results = []
    for doc_id in document_lengths:
        norm = math.sqrt(doc_norms[doc_id]) + 1e-6
        similarity = scores[doc_id] / norm if doc_id in scores else 0.0
        results.append((doc_id, similarity))

    return sorted(results, key=lambda x: x[1], reverse=True)[:top_n]

def compute_probabilities(query, tfidf_index, document_lengths):
    query_terms = text_processor.preprocess(query)
    probabilities = defaultdict(dict)

    for term in query_terms:
        if term in tfidf_index:
            for doc_id, weight in tfidf_index[term].items():
                probabilities[term][doc_id] = weight

    return probabilities
