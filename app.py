import streamlit as st
import gdown
import fitz  # PyMuPDF
import os
import re
import pandas as pd

def extract_folder_id(gdrive_link):
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', gdrive_link)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Google Drive folder link.")

def download_folder(folder_url):
    folder_id = extract_folder_id(folder_url)
    downloaded_path = gdown.download_folder(id=folder_id, quiet=False, use_cookies=False)
    if isinstance(downloaded_path, list) and downloaded_path:
        folder_name = os.path.dirname(downloaded_path[0])
    else:
        raise ValueError("Failed to download the folder or folder is empty.")
    return folder_name

def search_phrase_in_pdfs(folder_path, phrase):
    results = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.pdf'):
                full_path = os.path.join(root, file)
                try:
                    doc = fitz.open(full_path)
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        text = page.get_text()
                        if phrase.lower() in text.lower():
                            results.append({
                                "File Name": os.path.basename(full_path),
                                "Page Number": page_num + 1
                            })
                    doc.close()
                except Exception as e:
                    st.warning(f"Error reading {full_path}: {e}")
    if not results:
        results.append({"File Name": "No match found", "Page Number": "-"})
    return pd.DataFrame(results)

# Streamlit UI
st.title("🔍 PDF Phrase Search in Google Drive Folder")
st.markdown("Paste a **public Google Drive folder link** and a **phrase** to search through all PDF files inside.")

gdrive_link = st.text_input("🔗 Google Drive Folder Link")
phrase = st.text_input("🔍 Phrase to Search")

if st.button("Search"):
    if not gdrive_link or not phrase:
        st.warning("Please provide both a Google Drive folder link and a phrase.")
    else:
        with st.spinner("Downloading and searching PDFs..."):
            try:
                folder_path = download_folder(gdrive_link)
                df = search_phrase_in_pdfs(folder_path, phrase)
                st.success("Search complete!")
                st.dataframe(df)
            except Exception as e:
                st.error(f"An error occurred: {e}")
