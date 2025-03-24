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
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    chapters.append(item.get_content())

            total_chapters = len(chapters)
            if total_chapters == 0:
                st.error("No text chapters found in the EPUB file")
            else:
                st.write(f"Total chapters found: **{total_chapters}**")
                
                # Input for starting number
                start_number = st.number_input("Start numbering from:", 1, 1000, 1)
                
                if st.button('Convert All Chapters'):
                    with st.spinner(f"Converting {total_chapters} chapters..."):
                        zip_buffer = BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                            for idx, content in enumerate(chapters):
                                chapter_num = start_number + idx
                                filename = f"{book_name}{chapter_num:02d}.txt"
                                text = chapter_to_text(content)
                                zipf.writestr(filename, text.encode('utf-8'))
                        zip_buffer.seek(0)
                        st.success(f"✅ Successfully converted {total_chapters} chapters")
                        
                        # Download button with start number in filename
                        st.download_button(
                            label="Download ZIP",
                            data=zip_buffer,
                            file_name=f"{book_name}_chapters_starting_{start_number}.zip",
                            mime="application/zip"
                        )
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)