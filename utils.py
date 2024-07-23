import os
import fnmatch
import logging
import zipfile
import tarfile
# This function searches for all vhdl files and check if they have a keyword in it. 
# Intended to search all signle module vhdl source files
def search_files(directory, keyword):
    # Configure logging
    logging.basicConfig(filename='search_log.log', level=logging.INFO, format='%(message)s')
    
    # List to keep track of files where the keyword was not found
    files_without_keyword = []
    
    # Walk through directory and subdirectories
    for root, dirs, files in os.walk(directory):
        for filename in fnmatch.filter(files, '*.vhd'):
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    if keyword not in file.read():
                        files_without_keyword.append(file_path)
            except Exception as e:
                logging.error(f"Error reading file {file_path}: {e}")
    
    # Log files where the keyword was not found
    for file_path in files_without_keyword:
        logging.info(file_path)


# extract all compressed files in a directory and subdirectories, extract them all at
# the same location.
def extract_compressed_files(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                if filename.endswith('.zip'):
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(root)
                    print(f"Extracted {file_path}")
                elif filename.endswith('.tar') or filename.endswith('.tar.gz') or filename.endswith('.tgz'):
                    with tarfile.open(file_path, 'r') as tar_ref:
                        tar_ref.extractall(root)
                    print(f"Extracted {file_path}")
            except Exception as e:
                print(f"Failed to extract {file_path}: {e}")