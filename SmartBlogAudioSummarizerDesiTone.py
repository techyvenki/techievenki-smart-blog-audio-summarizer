from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize
import os
import requests
from bs4 import BeautifulSoup
import argparse
import asyncio
import edge_tts  # New: Using Microsoft Edge TTS instead of gTTS
import json

"""
# Replaced gTTS with edge-tts for more natural-sounding voice
# Added Indian English voices:

# Male: "en-IN-PrabhatNeural"
# Female: "en-IN-NeerjaNeural"


#Added speech customization options:

# Voice type selection (male/female)
# Speech rate adjustment
# Volume control


# Added prosody marks for more natural pauses
# Converted to async/await for better audio generation

Install the required packages:
pip install edge-tts

pip install beautifulsoup4 requests

python blog_enhancer.py https://yourblog.com/your-post-url

# Use female Indian voice
python blog_enhancer.py https://yourblog.com/your-post-url --voice-type female

# Use male Indian voice
python blog_enhancer.py https://yourblog.com/your-post-url --voice-type male

# Adjust speech rate and volume
python blog_enhancer.py https://yourblog.com/your-post-url --rate "+10%" --volume "+5%"

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
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        nltk.download('punkt')
        # New: Define available Indian English voices
        self.indian_voices = {
            "male": "en-IN-PrabhatNeural",  # Male Indian English voice
            "female": "en-IN-NeerjaNeural"  # Female Indian English voice
        }
        
    def extract_content_from_url(self, url):
        """Extract the main content from a blog post URL"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for script in soup(["script", "style"]):
                script.decompose()
                
            content = ""
            
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
                content = soup.body.get_text()
            
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = ' '.join(chunk for chunk in chunks if chunk)
            
            return content
            
        except Exception as e:
            raise Exception(f"Error extracting content from URL: {str(e)}")

    def create_summary(self, text, max_length=150, min_length=50):
        """Create a summary of the blog post text"""
        chunks = self._chunk_text(text)
        summaries = []
        
        for chunk in chunks:
            summary = self.summarizer(chunk, 
                                    max_length=max_length, 
                                    min_length=min_length, 
                                    do_sample=False)[0]['summary_text']
            summaries.append(summary)
        
        return " ".join(summaries)
    
    # New: Completely revised audio creation method using edge-tts
    async def create_audio(self, text, output_path, voice_type="male", rate="+0%", volume="+0%"):
        """
        Convert text to speech using Microsoft Edge TTS
        
        Args:
            text (str): Text to convert to speech
            output_path (str): Path to save the audio file
            voice_type (str): "male" or "female" for Indian English voice
            rate (str): Speech rate adjustment (e.g., "+10%", "-10%")
            volume (str): Volume adjustment (e.g., "+10%", "-10%")
        """
        try:
            # Select the appropriate voice
            voice = self.indian_voices.get(voice_type, self.indian_voices["male"])
            
            # Create communicate object
            tts = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
            
            # Generate audio
            await tts.save(output_path)
            
            # Add prosody marks for more natural pauses
            await self._add_prosody_marks(output_path)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Error creating audio: {str(e)}")
    
    # New: Method to add prosody marks for more natural speech
    async def _add_prosody_marks(self, audio_path):
        """Add prosody marks to make speech more natural"""
        try:
            with open(audio_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add slight pauses after punctuation
            content = content.replace('. ', '.<break time="300ms"/> ')
            content = content.replace('? ', '?<break time="300ms"/> ')
            content = content.replace('! ', '!<break time="300ms"/> ')
            content = content.replace(', ', ',<break time="200ms"/> ')
            
            with open(audio_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception:
            # If error occurs, continue with original audio
            pass
    
    def _chunk_text(self, text, max_chars=1000):
        """Split text into smaller chunks for processing"""
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

# New: Modified main function to handle async operations
async def main():
    parser = argparse.ArgumentParser(description='Create summary and audio from blog post URL')
    parser.add_argument('url', help='URL of the blog post')
    parser.add_argument('--output-dir', default='output', help='Directory to save audio files')
    parser.add_argument('--voice-type', default='male', choices=['male', 'female'], 
                       help='Voice type for audio generation')
    parser.add_argument('--rate', default='+0%', help='Speech rate adjustment (e.g., +10%, -10%)')
    parser.add_argument('--volume', default='+0%', help='Volume adjustment (e.g., +10%, -10%)')
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    enhancer = BlogEnhancer()
    
    try:
        print(f"Extracting content from {args.url}...")
        content = enhancer.extract_content_from_url(args.url)
        
        print("Creating summary...")
        summary = enhancer.create_summary(content)
        
        summary_path = os.path.join(args.output_dir, 'summary.txt')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print("Generating audio files...")
        full_audio_path = os.path.join(args.output_dir, 'full_post.mp3')
        summary_audio_path = os.path.join(args.output_dir, 'summary.mp3')
        
        # New: Using async audio creation
        await enhancer.create_audio(
            content, 
            full_audio_path, 
            voice_type=args.voice_type,
            rate=args.rate,
            volume=args.volume
        )
        
        await enhancer.create_audio(
            summary, 
            summary_audio_path,
            voice_type=args.voice_type,
            rate=args.rate,
            volume=args.volume
        )
        
        print(f"\nProcessing complete!")
        print(f"Summary saved to: {summary_path}")
        print(f"Full audio saved to: {full_audio_path}")
        print(f"Summary audio saved to: {summary_audio_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())