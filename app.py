import os
from pathlib import Path
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import streamlit as st
from io import BytesIO
import zipfile

# Tags to ignore during text extraction
blocklist = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script']

def chapter_to_text(chap):
    """Converts a chapter's HTML content into plain text."""
    output = ''
    soup = BeautifulSoup(chap, 'html.parser')
    text_nodes = soup.find_all(text=True)
    prev = ''
    for t in text_nodes:
        if t.parent.name not in blocklist:
            if not t.isspace():
                # Insert extra newlines if needed for better formatting
                if not (str(prev).endswith(' ') or str(t).startswith(' ')):
                    output += '\n\n'
                output += '{}'.format(t)
            prev = t
    return output

def convert_epub_to_text(epub_file):
    """
    Reads an EPUB file (passed as a file-like object) and converts it to plain text.
    Returns the book name and the text content.
    """
    book = epub.read_epub(epub_file)
    # Try to use the file name if available; otherwise, use a default name.
    if hasattr(epub_file, 'name'):
        book_name = Path(epub_file.name).stem
    else:
        book_name = "converted_book"
    chapters = []
    # Extract all document items (chapters) from the EPUB
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_content())
    text_output = ""
    for chapter in chapters:
        text_output += chapter_to_text(chapter) + "\n"
    return book_name, text_output

def main():
    st.title("EPUB to Text Converter")
    st.write("Upload one or more EPUB files, and download a zip file containing the converted text files.")

    uploaded_files = st.file_uploader("Choose EPUB files", type="epub", accept_multiple_files=True)
    
    if uploaded_files:
        # Create an in-memory zip file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for uploaded_file in uploaded_files:
                # Convert each uploaded EPUB to text
                book_name, text_content = convert_epub_to_text(uploaded_file)
                # Add the text file to the zip archive
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