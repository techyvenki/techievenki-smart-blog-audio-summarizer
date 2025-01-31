from transformers import pipeline
from gtts import gTTS
import nltk
from nltk.tokenize import sent_tokenize
import os
import requests
from bs4 import BeautifulSoup
import argparse

"""
Install the required packages:
pip install transformers nltk gTTS

pip install beautifulsoup4 requests

python blog_enhancer.py https://yourblog.com/your-post-url

# Specify output directory
python blog_enhancer.py https://yourblog.com/your-post-url --output-dir my_audio_files

# Specify different language (e.g., Spanish)
python blog_enhancer.py https://yourblog.com/your-post-url --lang es


The script will:

Crawl the provided URL and extract the main content
Generate a summary
Create audio files for both the full content and summary
Save everything in the specified output directory (defaults to 'output')

Note: You might need to adjust the possible_content_selectors in the extract_content_from_url method based on your website's HTML structure.

"""
class BlogEnhancer:
    def __init__(self):
        # Initialize the summarization pipeline
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        # Download required NLTK data
        nltk.download('punkt')
    
    def extract_content_from_url(self, url):
        """
        Extract the main content from a blog post URL
        
        Args:
            url (str): The URL of the blog post
            
        Returns:
            str: The extracted content
        """
        try:
            # Send request to the URL
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Try to find the main content
            # This might need adjustment based on your website's structure
            content = ""
            
            # Common content selectors - adjust these based on your website
            possible_content_selectors = [
                'article',
                '.post-content',
                '.entry-content',
                '.content',
                'main',
                '#content'
            ]
            
            for selector in possible_content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    content = content_element.get_text()
                    break
            
            if not content:
                # Fallback to body if no specific content container found
                content = soup.body.get_text()
            
            # Clean up the text
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = ' '.join(chunk for chunk in chunks if chunk)
            
            return content
            
        except Exception as e:
            raise Exception(f"Error extracting content from URL: {str(e)}")

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
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Create summary and audio from blog post URL')
    parser.add_argument('url', help='URL of the blog post')
    parser.add_argument('--output-dir', default='output', help='Directory to save audio files')
    parser.add_argument('--lang', default='en', help='Language code for audio generation')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    enhancer = BlogEnhancer()
    
    try:
        # Extract content from URL
        print(f"Extracting content from {args.url}...")
        content = enhancer.extract_content_from_url(args.url)
        
        # Create summary
        print("Creating summary...")
        summary = enhancer.create_summary(content)
        
        # Save summary to file
        summary_path = os.path.join(args.output_dir, 'summary.txt')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        # Create audio files
        print("Generating audio files...")
        full_audio_path = os.path.join(args.output_dir, 'full_post.mp3')
        summary_audio_path = os.path.join(args.output_dir, 'summary.mp3')
        
        enhancer.create_audio(content, full_audio_path, args.lang)
        enhancer.create_audio(summary, summary_audio_path, args.lang)
        
        print(f"\nProcessing complete!")
        print(f"Summary saved to: {summary_path}")
        print(f"Full audio saved to: {full_audio_path}")
        print(f"Summary audio saved to: {summary_audio_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()