import streamlit as st
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from pathlib import Path
from io import BytesIO
import zipfile
import tempfile
import os

blocklist = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script']

def chapter_to_text(chap_content):
    soup = BeautifulSoup(chap_content, 'html.parser')
    text = []
    for t in soup.find_all(text=True):
        if t.parent.name not in blocklist and not t.isspace():
            text.append(t.strip())
    return '\n\n'.join(text)

st.title("EPUB to Text Chapters Converter")

uploaded_file = st.file_uploader("Upload an EPUB file", type="epub")

if uploaded_file is not None:
    with st.spinner("Processing EPUB..."):
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.epub') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        try:
            # Read EPUB from temporary file path
            book = epub.read_epub(tmp_file_path)
            book_name = Path(uploaded_file.name).stem

            # Process chapters
            chapters = []
            for i, item in enumerate(book.get_items()):
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    chapter_content = chapter_to_text(item.get_content())
                    chapter_num = f"{i+1:03d}"
                    chapter_title = f"{book_name}_chapter_{chapter_num}.txt"
                    chapters.append((chapter_title, chapter_content))

            # Create ZIP archive
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                for title, content in chapters:
                    zipf.writestr(title, content.encode('utf-8'))
            zip_buffer.seek(0)

            st.success(f"✅ Processed {len(chapters)} chapters successfully!")
            
            # Provide download link
            st.download_button(
                label="Download Chapters ZIP",
                data=zip_buffer,
                file_name=f"{book_name}_chapters.zip",
                mime="application/zip"
            )
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)