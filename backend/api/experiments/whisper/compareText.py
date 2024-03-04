from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def preprocess_text(text):
    # Example preprocessing steps: converting to lowercase and removing punctuation
    text = text.lower()
    text = text.replace('.', ' ').replace(',', ' ').replace('?', ' ').replace('!', ' ')
    return text

def calculate_similarity(file1_path, file2_path):
    # Read the contents of the files
    text1 = read_file(file1_path)
    text2 = read_file(file2_path)

    # Preprocess the text
    text1 = preprocess_text(text1)
    text2 = preprocess_text(text2)

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform the texts
    tfidf_matrix = vectorizer.fit_transform([text1, text2])

    # Calculate cosine similarity
    similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

    return similarity_score



if __name__ == "__main__":
    file_fasit      = 'text/fasit.txt'
    file_tiny       = 'text/test_tiny.txt'
    file_base       = 'text/test_base.txt'
    file_small      = 'text/test_small.txt'
    file_medium     = 'text/test_medium.txt'
    file_large      = 'text/test_large.txt'
    file_large_v2   = 'text/test_large-v2.txt'
    file_large_v3   = 'text/test_large-v3.txt'
    file_small_chunk = 'text/compiled_transcriptions.txt'

    similarity_score_tiny   = calculate_similarity(file_fasit, file_tiny)
    similarity_score_base   = calculate_similarity(file_fasit, file_base)
    similarity_score_small  = calculate_similarity(file_fasit, file_small)
    similarity_score_medium = calculate_similarity(file_fasit, file_medium)
    similarity_score_large  = calculate_similarity(file_fasit, file_large)
    similarity_score_large_v2  = calculate_similarity(file_fasit, file_large_v2)
    similarity_score_large_v3  = calculate_similarity(file_fasit, file_large_v3)
    similarity_score_small_chunk = calculate_similarity(file_fasit, file_small_chunk)
    
    # write the result to a text file named result.txt
    with open('result/result.txt', 'w') as file:
        file.write(f"Similarity score between fasit and tiny: {similarity_score_tiny}\n")
        file.write(f"Similarity score between fasit and base: {similarity_score_base}\n")
        file.write(f"Similarity score between fasit and small: {similarity_score_small}\n")
        file.write(f"Similarity score between fasit and medium: {similarity_score_medium}\n")
        file.write(f"Similarity score between fasit and large: {similarity_score_large}\n")
        file.write(f"Similarity score between fasit and large-v2: {similarity_score_large_v2}\n")
        file.write(f"Similarity score between fasit and large-v3: {similarity_score_large_v3}\n")
        file.write(f"Similarity score between fasit and small_chunk: {similarity_score_small_chunk}\n")



