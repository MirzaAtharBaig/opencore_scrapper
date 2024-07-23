import os
import fnmatch
import logging
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
