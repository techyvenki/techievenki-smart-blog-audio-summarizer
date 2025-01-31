# Smart Blog Audio Summarizer

![Image](https://github.com/user-attachments/assets/f1ab4f4a-4bb4-409a-9d6b-35d525b574c5)

![Image](https://github.com/user-attachments/assets/2ad884a1-e332-43dc-8094-317c5dea4026)

## Overview
Smart Blog Audio Summarizer is an innovative tool designed to enhance the accessibility and engagement of blog content. By leveraging advanced natural language processing techniques, this project enables users to summarize lengthy blog posts and convert them into audio format, making it easier for readers to consume content on-the-go.

## Key Features
- **Text Summarization:** Utilizes state-of-the-art models (like Facebook's BART) to generate concise and coherent summaries of blog posts, ensuring that essential information is retained while reducing reading time.
- **Audio Generation:** Converts both the full blog content and the generated summaries into high-quality audio files using Google’s Text-to-Speech (gTTS) technology, allowing users to listen to their favorite articles.
- **Web Crawling:** Automatically extracts content from specified blog URLs, streamlining the process of summarization and audio generation directly from online sources.
- **User-Friendly Interface:** Simple command-line interface that allows users to specify URLs, output directories, and language options for audio generation.

## Installation
To install the required packages, run:
```bash
pip install transformers nltk gTTS
``` 

## Usage
To use Smart Blog Audio Summarizer, follow these steps:
1. Install the required packages: `pip install transformers nltk gTTS`
2. Install the required packages if want to run SmartBlogAudioSummarizerDesiTone.py: `pip install transformers nltk edge_tts`
3. Run the script: `python blog_enhancer.py https://yourblog.com/your-post-url --output-dir my_audio_files --lang es`   
4. You are all set! You can now listen to your blog posts on the go!

## Examples


### Crawl a Blog and Generate Audio for Posts
```bash
python blog_enhancer.py https://yourblog.com/ --output-dir my_audio_files
```bash
python blog_enhancer.py https://yourblog.com/ --output-dir my_audio_files --lang es


python BlogEnhancerNativeTone.py https://yourblog.com/ --output-dir my_native_audio_files --rate "+10%" --volume "+5%" --voice-type male/female

```


Happy hacking!