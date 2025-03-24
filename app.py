import streamlit as st
from ebooklib import epub
from bs4 import BeautifulSoup
import zipfile
import io
import os
from pathlib import Path

# Configuration
BLOCKLIST = [
    '[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 
    'script', 'footer', 'aside', 'nav', 'form', 'button', 'style', 'link'
]
ALLOWED_TAGS = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'pre']

def extract_chapter_text(content):
    """Extract and clean text from chapter content"""
    soup = BeautifulSoup(content, 'html.parser')
    text_elements = soup.find_all(ALLOWED_TAGS)
    cleaned_text = []

    for element in text_elements:
        if element.parent.name in BLOCKLIST:
            continue
        text = element.get_text(' ', strip=True)
        if text:
            cleaned_text.append(text)
    
    return '\n\n'.join(cleaned_text)

def sanitize_filename(name):
    """Clean filenames for safe saving"""
    # Replace invalid characters with underscores
    return "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)

def process_epub(uploaded_file):
    """Process EPUB file and return ZIP buffer"""
    book = epub.read_epub(uploaded_file)
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        chapter_count = 0
        
        for item in book.get_items():
            if item.get_type() == epub.ITEM_DOCUMENT:
                chapter_count += 1
                content = item.get_content()
                text = extract_chapter_text(content)
                
                # Try to find a title for the chapter
                soup = BeautifulSoup(content, 'html.parser')
                title_tag = soup.find(['h1', 'h2', 'h3'])
                title = f"Chapter_{chapter_count}"
                if title_tag and title_tag.get_text().strip():
                    title = title_tag.get_text().strip()
                
                # Create filename
                clean_title = sanitize_filename(title)[:100]  # Limit length
                filename = f"{clean_title}.txt"
                
                # Ensure unique filenames
                counter = 1
                while filename in zipf.namelist():
                    filename = f"{clean_title}_{counter}.txt"
                    counter += 1
                
                zipf.writestr(filename, text.encode('utf-8'))
    
    return zip_buffer

def main():
    st.title("📖 EPUB to Text Converter")
    st.markdown("Convert EPUB chapters to individual text files and download as ZIP")
    
    uploaded_file = st.file_uploader("Upload EPUB file", type=['epub'])
    
    if uploaded_file:
        with st.spinner("Processing EPUB..."):
            try:
                zip_buffer = process_epub(uploaded_file)
                book_name = Path(uploaded_file.name).stem
                zip_name = f"{book_name}_chapters.zip"
                
                st.success("Conversion complete!")
                st.download_button(
                    label="📥 Download ZIP",
                    data=zip_buffer.getvalue(),
                    file_name=zip_name,
                    mime="application/zip",
                    help="Click to download the converted chapters as a ZIP file"
                )
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()