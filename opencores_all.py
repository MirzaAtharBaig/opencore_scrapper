import os
import requests
import tarfile
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from getpass import getpass
from tqdm import tqdm

def extract_name_and_form_link(url):
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Extract query parameters
    query_params = parse_qs(parsed_url.query)
    
    # Extract 'repname' parameter from the query
    repname = query_params.get('repname', [None])[0]
    
    if repname:
        # Form the new link
        new_url = f"https://opencores.org/download/{repname}"
        return new_url
    else:
        raise ValueError("URL does not contain 'repname' parameter.")

def sanitize_filename(filename):
    # Replace invalid characters with underscores
    return re.sub(r'[: ]', '_', filename)

def download_file(session, url, save_folder):
    file_name = url.split('/')[-1] + '.tar.gz'  # Ensure the file has the .tar.gz extension
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    file_path = os.path.join(save_folder, file_name)
    
    try:
        response = session.get(url, stream=True)
        response.raise_for_status()
        
        # Get the total file size
        total_size = int(response.headers.get('content-length', 0))
        
        with open(file_path, 'wb') as file, tqdm(
                desc=file_name,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                bar.update(len(chunk))
        
        print(f"Downloaded and saved {file_name} to {save_folder}.")
        return file_path
    except requests.RequestException as e:
        print(f"Failed to download {url}. Reason: {e}")
        return None

def extract_file(file_path, extract_folder):
    if not os.path.exists(extract_folder):
        os.makedirs(extract_folder)
    try:
        with tarfile.open(file_path, 'r:gz') as tar:
            tar.extractall(path=extract_folder)
        print(f"Extracted {file_path} to {extract_folder}.")
    except tarfile.TarError as e:
        print(f"Failed to extract {file_path}. Reason: {e}")

def get_all_form_fields(soup):
    fields = {}
    for input_tag in soup.find_all('input'):
        if input_tag.get('name'):
            fields[input_tag['name']] = input_tag.get('value', '')
    return fields

def login(session, login_url, username, password):
    response = session.get(login_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Get all form fields
    form_fields = get_all_form_fields(soup)
    print("Form fields found:", form_fields)
    
    # Update form fields with username and password
    form_fields['user'] = username
    form_fields['pass'] = password
    
    response = session.post(login_url, data=form_fields)
    response.raise_for_status()
    
    # Check if login was successful
    if "Login failed" in response.text:
        print("Login failed. Please check your credentials.")
        exit(1)
    
    # Print cookies and headers for inspection
    print("Cookies:", session.cookies)
    print("Headers:", response.headers)
    
    return session

# Define the URL of the webpage
url = "https://opencores.org/websvn/index?repname=1000base-x&path=%2F1000base-x%2F"

# Send a GET request to the webpage
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the section containing the repository links
    repository_section = soup.find('div', id='websvn')
    
    # Extract all links within the repository section
    repository_links = repository_section.find_all('a', href=True)
    
    # Loop through the links and print their URLs
    counter = 0
    download_links = []
    for i, link in enumerate(repository_links):
        if i < 2:  # Skip the first two invalid entries
            continue
        
        href = link['href']
        full_url = f"https://opencores.org{href}"
        try:
            new_link = extract_name_and_form_link(full_url)
            download_links.append(new_link)
            counter += 1
        except ValueError as e:
            print(f"Skipping invalid URL: {full_url} due to error: {e}")
    
    print(f"There are {counter} repositories on opencores.org")
    
    # Prompt for username and password
    username = "xxxxxxx"
    password = "xxxxxxxxxx"
    
    # Create a session
    session = requests.Session()
    
    # Login
    try:
        session = login(session, "https://opencores.org/login", username, password)
    except requests.RequestException as e:
        print(f"Login failed. Reason: {e}")
        exit(1)
    
    # Download and extract files from the links
    for link in download_links:
        file_path = download_file(session, link, "downloads")
        if file_path:
            extract_file(file_path, os.path.join("extracted", link.split('/')[-1]))
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")