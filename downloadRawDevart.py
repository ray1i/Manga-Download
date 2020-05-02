# !python3
# downloadRawDevart.py - Downloads manga from RawDevart

import requests, os, bs4, re

master_url = input('Enter the URL of the chapter list:  ')  # Url of chapter list

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

# Function that returns the url of a page, given the title of the manga, the chapter, and page.
def get_image_url(title, ch, pg):
    converted_title = ''
    for c in range(len(title)):
        if title[c] == ' ':
            converted_title += '-'
        else:
            converted_title += title[c].lower()
    
    if len(str(pg)) < 3:
        pg_ = '0' * (3 - len(str(pg))) + str(pg)

    return f'https://image.rawdevart.com/comic/{converted_title}/chapters/{ch}/{pg_}.jpg'

chapter_number = 1
success = True
while True:
    if not success:
        break
    
    # Save the image to ./rawdevart_downloads/(title)/(chapter).
    os.makedirs(os.path.join("rawdevart_downloads", title, f'Chapter {chapter_number}'), exist_ok=True)
    print(f'Downloading Chapter {chapter_number}...')

    page_number = 1
    success = False
    while True:
        try:
            # Download the image.
            image_url = get_image_url(title, chapter_number, page_number)
            res = requests.get(image_url)
            res.raise_for_status()
            #print(f'Downloading image {image_url}')
            
            success = True
        except requests.exceptions.HTTPError:
            break

        # Save the image to ./rawdevart_downloads/(title)/(chapter)/(pg#).jpg.
        imageFile = open(os.path.join('rawdevart_downloads', title, f'Chapter {chapter_number}', os.path.basename(image_url)), 'wb')
        for chunk in res.iter_content(100000):
            imageFile.write(chunk)
        imageFile.close()

        page_number += 1

    chapter_number += 1

print('Done.')