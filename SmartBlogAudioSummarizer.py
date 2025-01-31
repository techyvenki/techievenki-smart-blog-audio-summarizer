from transformers import pipeline
from gtts import gTTS
import nltk
from nltk.tokenize import sent_tokenize
import os

"""
Install the required packages:
pip install transformers nltk gTTS

The script provides two main features:

Text summarization using Facebook's BART model
Audio generation using Google's Text-to-Speech (gTTS)

To use it with your blog, you can:

Pass your blog post text to create a summary
Generate audio files for both the full post and summary
Upload the generated MP3 files to your blog's media library

Would you like me to explain any specific part of the implementation 
or help you integrate it with your particular blog platform? I can also 
help you modify the code to work with different summarization models or 
audio generation services if you have specific preferences.


"""
class BlogEnhancer:
    def __init__(self):
        # Initialize the summarization pipeline
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        # Download required NLTK data
        nltk.download('punkt')
    
    def create_summary(self, text, max_length=150, min_length=50):
        """
        Create a summary of the blog post text
        
        Args:
            text (str): The blog post content
            max_length (int): Maximum length of summary in words
            min_length (int): Minimum length of summary in words
            
        Returns:
            str: Summarized text
        """
        # Ensure text isn't too long for the model
        chunks = self._chunk_text(text)
        summaries = []
        
        for chunk in chunks:
            summary = self.summarizer(chunk, 
                                    max_length=max_length, 
                                    min_length=min_length, 
                                    do_sample=False)[0]['summary_text']
            summaries.append(summary)
        
        return " ".join(summaries)
    
    def create_audio(self, text, output_path, lang='en'):
        """
        Convert text to speech and save as MP3
        
        Args:
            text (str): Text to convert to speech
            output_path (str): Path to save the audio file
            lang (str): Language code (default: 'en' for English)
            
        Returns:
            str: Path to the generated audio file
        """
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_path)
        return output_path
    
    def _chunk_text(self, text, max_chars=1000):
        """
        Split text into smaller chunks for processing
        
        Args:
            text (str): Text to split
            max_chars (int): Maximum characters per chunk
            
        Returns:
            list: List of text chunks
        """
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            if current_length + len(sentence) <= max_chars:
                current_chunk.append(sentence)
                current_length += len(sentence)
            else:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = len(sentence)
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks

def main():
    # Example usage
    blog_post = """
    Your blog post content goes here. This can be a long article
    that you want to summarize and convert to audio.
    """
    
    enhancer = BlogEnhancer()
    
    # Create summary
    summary = enhancer.create_summary(blog_post)
    print("Summary created:", summary)
    
    # Create audio files for both full post and summary
    full_audio_path = enhancer.create_audio(blog_post, "full_post.mp3")
    summary_audio_path = enhancer.create_audio(summary, "summary.mp3")
    
    print(f"Full audio created at: {full_audio_path}")
    print(f"Summary audio created at: {summary_audio_path}")

if __name__ == "__main__":
    main()