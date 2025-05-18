# import streamlit as st
# import gdown
# import fitz  # PyMuPDF
# import os
# import re
# import pandas as pd

# def extract_folder_id(gdrive_link):
#     match = re.search(r'/folders/([a-zA-Z0-9_-]+)', gdrive_link)
#     if match:
#         return match.group(1)
#     else:
#         raise ValueError("Invalid Google Drive folder link.")

# def download_folder(folder_url):
#     folder_id = extract_folder_id(folder_url)
#     downloaded_path = gdown.download_folder(id=folder_id, quiet=False, use_cookies=False)
#     if isinstance(downloaded_path, list) and downloaded_path:
#         folder_name = os.path.dirname(downloaded_path[0])
#     else:
#         raise ValueError("Failed to download the folder or folder is empty.")
#     return folder_name

# def search_phrase_in_pdfs(folder_path, phrase):
#     results = []
#     for root, dirs, files in os.walk(folder_path):
#         for file in files:
#             if file.endswith('.pdf'):
#                 full_path = os.path.join(root, file)
#                 try:
#                     doc = fitz.open(full_path)
#                     for page_num in range(len(doc)):
#                         page = doc.load_page(page_num)
#                         text = page.get_text()
#                         if phrase.lower() in text.lower():
#                             results.append({
#                                 "File Name": os.path.basename(full_path),
#                                 "Page Number": page_num + 1
#                             })
#                     doc.close()
#                 except Exception as e:
#                     st.warning(f"Error reading {full_path}: {e}")
#     if not results:
#         results.append({"File Name": "No match found", "Page Number": "-"})
#     return pd.DataFrame(results)

# # Streamlit UI
# st.title("🔍 PDF Phrase Search in Google Drive Folder")
# st.markdown("Paste a **public Google Drive folder link** and a **phrase** to search through all PDF files inside.")

# gdrive_link = st.text_input("🔗 Google Drive Folder Link")
# phrase = st.text_input("🔍 Phrase to Search")

# if st.button("Search"):
#     if not gdrive_link or not phrase:
#         st.warning("Please provide both a Google Drive folder link and a phrase.")
#     else:
#         with st.spinner("Downloading and searching PDFs..."):
#             try:
#                 folder_path = download_folder(gdrive_link)
#                 df = search_phrase_in_pdfs(folder_path, phrase)
#                 st.success("Search complete!")
#                 st.dataframe(df)
#             except Exception as e:
#                 st.error(f"An error occurred: {e}")




import streamlit as st
import gdown
import fitz  # PyMuPDF
import os
import re
import pandas as pd
import zipfile
import tempfile
import shutil

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

def extract_zip(uploaded_zip):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    return temp_dir

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
st.title("🔍 PDF Phrase Search in Google Drive or ZIP Upload")
st.markdown("Paste a **Google Drive folder link** or upload a **ZIP file** of PDFs. Enter the phrase to search.")

search_option = st.radio("Select Input Source", ["Google Drive Link", "ZIP File Upload"])

gdrive_link = ""
uploaded_zip = None

if search_option == "Google Drive Link":
    gdrive_link = st.text_input("🔗 Google Drive Folder Link")
else:
    uploaded_zip = st.file_uploader("📁 Upload ZIP file of PDFs", type=["zip"])

phrase = st.text_input("🔍 Phrase to Search")

if st.button("Search"):
    if not phrase:
        st.warning("Please enter a phrase to search.")
    else:
        with st.spinner("Processing..."):
            try:
                folder_path = ""
                if search_option == "Google Drive Link":
                    if not gdrive_link:
                        st.warning("Please provide a Google Drive link.")
                        st.stop()
                    folder_path = download_folder(gdrive_link)
                else:
                    if not uploaded_zip:
                        st.warning("Please upload a ZIP file.")
                        st.stop()
                    folder_path = extract_zip(uploaded_zip)
                
                df = search_phrase_in_pdfs(folder_path, phrase)
                st.success("Search complete!")
                st.dataframe(df)

                # Cleanup if temporary
                if search_option == "ZIP File Upload":
                    shutil.rmtree(folder_path)

            except Exception as e:
                st.error(f"An error occurred: {e}")
