import os
from pathlib import Path
import tempfile
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import streamlit as st
from io import BytesIO
import zipfile

# Define HTML tags to ignore during text extraction.
blocklist = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script']

def chapter_to_text(chap):
    """
    Convert a chapter's HTML content into plain text.
    
    Args:
        chap (bytes): The HTML content of the chapter.
        
    Returns:
        str: The plain text extracted from the HTML.
    """
    output = ''
    soup = BeautifulSoup(chap, 'html.parser')
    text_nodes = soup.find_all(text=True)
    prev = ''
    for t in text_nodes:
        if t.parent.name not in blocklist:
            if not t.isspace():
                # Add extra newlines if needed for formatting.
                if not (str(prev).endswith(' ') or str(t).startswith(' ')):
                    output += '\n\n'
                output += '{}'.format(t)
            prev = t
    return output

def convert_epub_to_text(epub_file):
    """
    Convert an uploaded EPUB file (as a file-like object) to plain text.
    
    Args:
        epub_file (file-like object): The uploaded EPUB file.
        
    Returns:
        tuple: The book name (derived from the file name) and the extracted text.
    """
    # If the file is a file-like object (from Streamlit uploader), write it to a temporary file.
    if hasattr(epub_file, 'read'):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".epub") as tmp_file:
            tmp_file.write(epub_file.read())
            tmp_path = tmp_file.name
        book = epub.read_epub(tmp_path)
        os.remove(tmp_path)
    else:
        book = epub.read_epub(epub_file)

    # Use the file's name if available; otherwise, assign a default name.
    if hasattr(epub_file, 'name'):
        book_name = Path(epub_file.name).stem
    else:
        book_name = "converted_book"
    
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_content())
    
    text_output = ""
    for chapter in chapters:
        text_output += chapter_to_text(chapter) + "\n"
    
    return book_name, text_output

def main():
    st.title("EPUB to Text Converter")
    st.write("Upload one or more EPUB files and download a ZIP file containing the converted text files.")

    # Allow users to upload multiple EPUB files.
    uploaded_files = st.file_uploader("Choose EPUB files", type="epub", accept_multiple_files=True)
    
    if uploaded_files:
        # Create an in-memory ZIP file.
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for uploaded_file in uploaded_files:
                # Convert each uploaded EPUB to text.
                book_name, text_content = convert_epub_to_text(uploaded_file)
                # Add each text file to the ZIP archive.
                zip_file.writestr(book_name + ".txt", text_content)
        zip_buffer.seek(0)
        st.download_button(
            label="Download Converted Text Files (ZIP)",
            data=zip_buffer,
            file_name="converted_text_files.zip",
            mime="application/zip"
        )

if __name__ == '__main__':
    main()