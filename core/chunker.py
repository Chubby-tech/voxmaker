import re
import nltk
import textstat

# Ensure nltk punkt is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

def detect_chapters_and_headings(text: str) -> list:
    """
    Splits text based on large newlines to treat them as paragraphs/sections.
    """
    sections = re.split(r'\n\n+', text)
    return [s.strip() for s in sections if s.strip()]

def get_length_scale(text: str) -> float:
    """
    Returns a Piper length_scale based on reading complexity.
    Flesch Reading Ease: 
    90-100: Very easy
    60-70: Standard
    0-30: Very difficult (requires slower reading)
    
    Piper length_scale: >1.0 is slower, <1.0 is faster.
    """
    try:
        score = textstat.flesch_reading_ease(text)
        if score > 80:
            return 0.90  # Fast
        elif score < 40:
            return 1.15  # Slow
        else:
            return 1.0   # Normal
    except Exception:
        return 1.0

def chunk_text(text: str, max_words: int = 2500) -> list:
    """
    Splits text into chunks of max_words without breaking sentences.
    Detects chapters and evaluates text complexity for reading speed.
    """
    sections = detect_chapters_and_headings(text)
    
    chunks = []
    current_chunk = []
    current_word_count = 0
    is_chapter_start = False
    
    chapter_regex = re.compile(r'^(chapter\s+\d+|part\s+[ivxlcdm]+)', re.IGNORECASE)
    
    def finalize_chunk(content_list, chapter_flag):
        content = " ".join(content_list)
        if not content.strip():
            return None
        scale = get_length_scale(content)
        return {
            "content": content,
            "is_chapter_start": chapter_flag,
            "length_scale": scale
        }

    for section in sections:
        words = section.split()
        if not words:
            continue
            
        # Detect if this section is a chapter heading
        section_is_chapter = False
        if len(words) < 10 and chapter_regex.match(section):
            section_is_chapter = True
            
        # If we hit a chapter, force finalize the current chunk
        if section_is_chapter and current_chunk:
            chunk_dict = finalize_chunk(current_chunk, is_chapter_start)
            if chunk_dict:
                chunks.append(chunk_dict)
            current_chunk = []
            current_word_count = 0
            is_chapter_start = True # Next chunk will be a chapter start
            
        try:
            sentences = nltk.sent_tokenize(section)
        except Exception:
            sentences = [s + '.' for s in section.split('. ') if s]
            
        for sentence in sentences:
            sentence_word_count = len(sentence.split())
            if current_word_count + sentence_word_count > max_words:
                if current_chunk:
                    chunk_dict = finalize_chunk(current_chunk, is_chapter_start)
                    if chunk_dict:
                        chunks.append(chunk_dict)
                current_chunk = [sentence]
                current_word_count = sentence_word_count
                is_chapter_start = False # Only the first chunk of a chapter gets the flag
            else:
                current_chunk.append(sentence)
                current_word_count += sentence_word_count
                
    if current_chunk:
        chunk_dict = finalize_chunk(current_chunk, is_chapter_start)
        if chunk_dict:
            chunks.append(chunk_dict)
        
    return chunks
