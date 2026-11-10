import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string

# Ensure necessary NLTK data is available
import os
def download_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('tokenizers/punkt_tab')
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('punkt')
        nltk.download('punkt_tab')
        nltk.download('wordnet')

download_nltk_data()

lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    lemmatized = [lemmatizer.lemmatize(word) for word in tokens]
    return " ".join(lemmatized)

def get_best_knowledge_match(user_query, knowledge_base_items):
    if not knowledge_base_items:
        return None
    
    questions = [item[0] for item in knowledge_base_items]
    answers = [item[1] for item in knowledge_base_items]
    
    processed_query = preprocess_text(user_query)
    processed_questions = [preprocess_text(q) for q in questions]
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([processed_query] + processed_questions)
    
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    best_match_idx = cosine_similarities.argmax()
    
    if cosine_similarities[best_match_idx] > 0.6:  # Threshold for matching
        return answers[best_match_idx]
    
    return None

def extract_intent_and_entities(query):
    query_lower = query.lower()
    
    if "author" in query_lower and ("who wrote" in query_lower or "author of" in query_lower or "books by" in query_lower):
        parts = query_lower.split("by")
        if len(parts) > 1:
            return "search_author", parts[-1].strip()
        parts = query_lower.split("author of")
        if len(parts) > 1:
            return "search_title", parts[-1].strip()
            
    if "recommend" in query_lower or "suggest" in query_lower:
        words = query_lower.split()
        genre = words[-1] if len(words) > 0 else "fiction"
        return "recommend", genre
        
    if "borrow" in query_lower or "status" in query_lower or "my books" in query_lower:
        words = query_lower.split()
        user_id = words[-1] if words[-1].isdigit() else "U001"
        return "borrow_status", user_id
        
    if "available" in query_lower or "do you have" in query_lower or "search" in query_lower:
        clean_query = query_lower.replace("is", "").replace("available", "").replace("do you have", "").replace("search", "").replace("for", "").strip()
        return "search_title", clean_query
        
    return "general", query
