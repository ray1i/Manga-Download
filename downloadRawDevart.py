# !python3
# downloadRawDevart.py - Downloads manga from RawDevart

import requests, os, re

master_url = input('Enter the URL of the chapter list:  ')  # Url of chapter list
page_base = 'https://image.rawdevart.com/comic/'

# Load the master list.
print(f'Loading page {master_url} ...') 
master_res = requests.get(master_url)
master_res.raise_for_status()
master_res = master_res.text

# Find the title of the manga
title = re.search('<title>(.*) Raw \| Rawdevart - Raw Manga</title>', master_res)
title = title.group(1)

# Store comics in ./rawdevart_downloads/(title)
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join("rawdevart_downloads", title), exist_ok=True)

chapter_number = 1
# Save the image to ./rawdevart_downloads/(title)/(chapter).
os.makedirs(os.path.join("rawdevart_downloads", title, f'Chapter {chapter_number}'), exist_ok=True)

while True:   

    # Load the chapter.
    chapter_url = f'{master_url}chapter-{chapter_number}/' 
    chapter_res = requests.get(chapter_url)
    chapter_res.raise_for_status()
    chapter_res = chapter_res.text

    # Find the URL for all the pages in the chapter.
    page_list = re.findall('data-src="https://image.rawdevart.com/comic/(\S*)"', chapter_res)
    if page_list == []: break
    
    for page in page_list:
        page_url = page_base + page

        # Download the image.
        res = requests.get(page_url)
        res.raise_for_status()
        #print(f'Downloading image {image_url}')

        # Save the image to ./rawdevart_downloads/(title)/(chapter)/(pg#).jpg.
        imageFile = open(os.path.join('rawdevart_downloads', title, f'Chapter {chapter_number}', os.path.basename(page_url)), 'wb')
        for chunk in res.iter_content(100000):
            imageFile.write(chunk)
        imageFile.close()

    print(f'Chapter {chapter_number} downloaded.')
    chapter_number += 1
    os.makedirs(os.path.join("rawdevart_downloads", title, f'Chapter {chapter_number}'), exist_ok=True)

print('Done.')
