"""
NLP-based Answer Evaluation Module
Uses NLTK and scikit-learn for AI-powered answer evaluation

This module implements:
1. Text preprocessing using NLTK
2. TF-IDF vectorization for semantic analysis
3. Cosine similarity for comparing user answers with ideal answers
4. Keyword extraction and matching
5. Sentiment-based feedback generation
"""

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# Initialize stemmer for word normalization
stemmer = PorterStemmer()

# Expected keywords for different question types (fallback when ideal answer not available)
EXPECTED_KEYWORDS = {
    'HR': {
        'Tell me about yourself': ['experience', 'education', 'skills', 'background', 'work', 'career'],
        'strengths': ['strength', 'skill', 'ability', 'talent', 'expertise', 'proficient'],
        'weaknesses': ['weakness', 'improve', 'challenge', 'develop', 'learn', 'growth'],
        'Why do you want to work here': ['company', 'culture', 'values', 'opportunity', 'growth', 'interest'],
        'Where do you see yourself': ['goal', 'career', 'future', 'plan', 'aspiration', 'growth']
    },
    'Technical': {
        'Python': ['python', 'programming', 'language', 'syntax', 'object-oriented', 'interpreted'],
        'list': ['mutable', 'ordered', 'changeable', 'brackets', '[]'],
        'tuple': ['immutable', 'ordered', 'unchangeable', 'parentheses', '()'],
        'SQL': ['database', 'query', 'structured', 'relational', 'table', 'select'],
        'normalization': ['database', 'redundancy', 'normal forms', '1nf', '2nf', '3nf', 'integrity'],
        'Flask': ['framework', 'python', 'web', 'micro', 'routing', 'decorator'],
        'REST': ['representational', 'state', 'transfer', 'http', 'api', 'stateless', 'resource']
    }
}


def preprocess_text(text):
    """
    Preprocess text for NLP analysis
    Steps: Convert to lowercase, remove special characters, normalize whitespace
    """
    if not text:
        return ""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters but keep spaces and basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_keywords(text, question_type):
    """
    Extract relevant keywords from text using NLTK
    Steps: Tokenize, remove stopwords, stem words
    """
    processed_text = preprocess_text(text)
    tokens = word_tokenize(processed_text)
    
    # Remove stopwords (common words like 'the', 'is', etc.)
    stop_words = set(stopwords.words('english'))
    keywords = [word for word in tokens if word not in stop_words and len(word) > 2]
    
    # Stem keywords (reduce words to root form: running -> run)
    stemmed_keywords = [stemmer.stem(word) for word in keywords]
    
    return stemmed_keywords


def calculate_tfidf_similarity(user_answer, ideal_answer):
    """
    Calculate semantic similarity using TF-IDF and Cosine Similarity
    
    TF-IDF (Term Frequency-Inverse Document Frequency):
    - Measures how important a word is in a document
    - Words that appear frequently in one document but rarely in others get higher scores
    
    Cosine Similarity:
    - Measures the angle between two vectors
    - Returns value between 0 (completely different) and 1 (identical)
    - Higher values indicate more similar content
    """
    try:
        # Create TF-IDF vectorizer
        # max_features: limit vocabulary size for efficiency
        # stop_words: remove common English words
        # ngram_range: consider single words and word pairs
        vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2),  # Unigrams and bigrams
            min_df=1
        )
        
        # Combine texts for vectorization
        texts = [preprocess_text(user_answer), preprocess_text(ideal_answer)]
        
        # Transform texts to TF-IDF vectors
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Calculate cosine similarity between the two vectors
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Convert to percentage (0-100)
        similarity_score = similarity * 100
        
        return similarity_score, True
    except Exception as e:
        # Fallback if TF-IDF fails (e.g., empty text, insufficient words)
        return 0, False


def calculate_keyword_similarity(user_answer, ideal_answer, question_type):
    """
    Calculate similarity based on keyword matching
    Extracts keywords from both answers and finds common terms
    """
    # Extract keywords from both answers
    user_keywords = set(extract_keywords(user_answer, question_type))
    ideal_keywords = set(extract_keywords(ideal_answer, question_type))
    
    if not ideal_keywords:
        return 0, []
    
    # Find common keywords
    common_keywords = user_keywords.intersection(ideal_keywords)
    
    # Calculate match ratio
    match_ratio = len(common_keywords) / len(ideal_keywords) if ideal_keywords else 0
    keyword_score = match_ratio * 100
    
    return keyword_score, list(common_keywords)[:10]  # Return top 10 matched keywords


def calculate_length_score(user_answer, ideal_answer):
    """
    Evaluate answer completeness based on length
    Compares user answer length with ideal answer length
    """
    user_words = len(word_tokenize(user_answer))
    ideal_words = len(word_tokenize(ideal_answer))
    
    if ideal_words == 0:
        return 50  # Default score if no ideal answer
    
    # Calculate length ratio
    length_ratio = user_words / ideal_words if ideal_words > 0 else 0
    
    # Score based on how close the length is to ideal
    if length_ratio < 0.3:
        # Too short - significant penalty
        length_score = length_ratio * 60
    elif length_ratio > 2.0:
        # Too long - slight penalty
        length_score = 100 - ((length_ratio - 2.0) * 10)
    else:
        # Good length range
        length_score = 50 + (min(length_ratio, 1.0) * 50)
    
    # Ensure score is between 0 and 100
    return max(0, min(100, length_score))


def calculate_fallback_score(user_answer, question_text, question_type):
    """
    Fallback scoring method when ideal answer is not available
    Uses keyword matching with expected keywords
    """
    answer_lower = user_answer.lower()
    question_lower = question_text.lower()
    
    # Extract keywords from user answer
    answer_keywords = extract_keywords(user_answer, question_type)
    
    # Get expected keywords based on question
    expected_keywords_list = []
    for key, keywords in EXPECTED_KEYWORDS.get(question_type, {}).items():
        if any(keyword in question_lower for keyword in key.lower().split()):
            expected_keywords_list.extend([kw.lower() for kw in keywords])
    
    # If no specific match, use general keywords for the type
    if not expected_keywords_list:
        all_keywords = []
        for keywords in EXPECTED_KEYWORDS.get(question_type, {}).values():
            all_keywords.extend([kw.lower() for kw in keywords])
        expected_keywords_list = all_keywords
    
    # Stem expected keywords
    expected_stemmed = [stemmer.stem(kw.lower()) for kw in expected_keywords_list]
    
    # Calculate keyword match ratio
    matched_keywords = [kw for kw in answer_keywords if kw in expected_stemmed]
    keyword_score = (len(matched_keywords) / len(expected_stemmed) * 100) if expected_stemmed else 0
    
    # Calculate length score
    word_count = len(word_tokenize(user_answer))
    if word_count < 10:
        length_score = word_count * 5
    elif word_count > 200:
        length_score = 100
    else:
        length_score = min(100, 50 + (word_count - 10) * 0.5)
    
    # Combined score
    final_score = (keyword_score * 0.6 + length_score * 0.4)
    final_score = min(100, max(0, final_score))
    
    return final_score, matched_keywords


def generate_sentiment_feedback(score, matched_keywords, user_answer, ideal_answer=None):
    """
    Generate sentiment-based feedback based on evaluation score
    Provides constructive feedback to help users improve
    """
    feedback_parts = []
    
    # Score-based sentiment
    if score >= 85:
        feedback_parts.append("🌟 Excellent answer! You demonstrated comprehensive understanding of the topic.")
    elif score >= 70:
        feedback_parts.append("✅ Good answer! You covered the main points well.")
    elif score >= 55:
        feedback_parts.append("👍 Fair answer. You're on the right track but could add more detail.")
    elif score >= 40:
        feedback_parts.append("⚠️ Your answer needs improvement. Try to be more specific and detailed.")
    else:
        feedback_parts.append("❌ Your answer is too brief or lacks relevant information. Please provide more context.")
    
    # Keyword feedback
    if matched_keywords and len(matched_keywords) > 0:
        keyword_list = ', '.join(matched_keywords[:5])
        feedback_parts.append(f"Key concepts covered: {keyword_list}.")
    else:
        feedback_parts.append("Try to include more relevant technical terms and concepts.")
    
    # Length feedback
    user_word_count = len(word_tokenize(user_answer))
    if ideal_answer:
        ideal_word_count = len(word_tokenize(ideal_answer))
        if user_word_count < ideal_word_count * 0.5:
            feedback_parts.append("Your answer is quite short. Consider expanding with examples and details.")
        elif user_word_count > ideal_word_count * 1.5:
            feedback_parts.append("Your answer is lengthy. Consider being more concise while maintaining clarity.")
    else:
        if user_word_count < 20:
            feedback_parts.append("Your answer is too short. Aim for at least 30-50 words for better evaluation.")
        elif user_word_count > 300:
            feedback_parts.append("Your answer is very long. Try to be more concise.")
    
    # Improvement suggestions
    if score < 60:
        feedback_parts.append("💡 Suggestion: Structure your answer with an introduction, main points, and conclusion. Include specific examples where relevant.")
    
    return " ".join(feedback_parts)


def evaluate_answer(question_text, user_answer, question_type='Technical', ideal_answer=None):
    """
    Main evaluation function that combines multiple NLP techniques
    
    Evaluation Process:
    1. Preprocessing: Clean and normalize text
    2. TF-IDF + Cosine Similarity: Compare semantic similarity with ideal answer
    3. Keyword Matching: Find common important terms
    4. Length Analysis: Check answer completeness
    5. Score Calculation: Weighted combination of all factors
    6. Feedback Generation: Sentiment-based constructive feedback
    
    Args:
        question_text: The interview question
        user_answer: The user's response
        question_type: 'HR' or 'Technical'
        ideal_answer: Reference answer for comparison (optional)
    
    Returns:
        dict with 'score', 'feedback', and 'keywords_matched'
    """
    # Validate input
    if not user_answer or len(user_answer.strip()) < 5:
        return {
            'score': 0,
            'feedback': 'Answer is too short. Please provide a more detailed response (minimum 5 characters).',
            'keywords_matched': []
        }
    
    # If ideal answer is provided, use advanced evaluation
    if ideal_answer and len(ideal_answer.strip()) > 10:
        # Method 1: TF-IDF + Cosine Similarity (Primary method - 50% weight)
        tfidf_score, tfidf_success = calculate_tfidf_similarity(user_answer, ideal_answer)
        
        # Method 2: Keyword Matching (30% weight)
        keyword_score, matched_keywords = calculate_keyword_similarity(
            user_answer, ideal_answer, question_type
        )
        
        # Method 3: Length Analysis (20% weight)
        length_score = calculate_length_score(user_answer, ideal_answer)
        
        # Calculate final score with weighted average
        if tfidf_success:
            # Use all three methods
            final_score = (tfidf_score * 0.5 + keyword_score * 0.3 + length_score * 0.2)
        else:
            # Fallback if TF-IDF fails
            final_score = (keyword_score * 0.6 + length_score * 0.4)
        
        # Ensure score is between 0 and 100
        final_score = max(0, min(100, final_score))
        
        # Generate feedback
        feedback = generate_sentiment_feedback(
            final_score, matched_keywords, user_answer, ideal_answer
        )
        
    else:
        # Fallback method when ideal answer is not available
        final_score, matched_keywords = calculate_fallback_score(
            user_answer, question_text, question_type
        )
        
        # Generate feedback without ideal answer reference
        feedback = generate_sentiment_feedback(
            final_score, matched_keywords, user_answer, None
        )
    
    return {
        'score': round(final_score, 2),
        'feedback': feedback,
        'keywords_matched': matched_keywords[:10] if matched_keywords else []
    }
