# !python3
# downloadPixiv_new.py - Downloads manga from pixiv

import requests, os, bs4, re

master_url = input('Enter the URL of the chapter list:  ')  # Url of chapter list
chapter_base = 'https://www.pixiv.net/en/artworks/'
#page_base = 'https://tc-pximg01.techorus-cdn.com/img-original/img/'
page_base = 'https://i.pximg.net/img-original/img/'

# Load the master list.
print(f'Loading page {master_url} ...') 
master_res = requests.get(master_url)
master_res.raise_for_status()
master_res = master_res.text

# Find the title of the manga
title = re.search('<title>「(\w*)」/', master_res)
title = title.group(1)

# Store comics in ./pixiv_downloads/(title)
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join("pixiv_downloads", title), exist_ok=True)

# Search master list for all the chapters, put their ids into a list.
findChaptersRegex = re.compile(r'image-item"><a href="/artworks/(\d{8})')
master_ids = findChaptersRegex.findall(master_res)
master_page_number = 2
while True:

    new_master_url = master_url + '?p=' + str(master_page_number)

    # Load the master list.
    new_master_res = requests.get(new_master_url)
    new_master_res.raise_for_status()
    new_master_res = new_master_res.text
    if '<div class="no-content">' in new_master_res:
        break
    print(f'Loading page {new_master_url} ...')

    # Search master list for all the chapters, put their ids into a list.
    temp_ids = findChaptersRegex.findall(new_master_res)
    for id in temp_ids:
        master_ids.append(id)
    
    # Go to the next page of pages
    master_page_number += 1

chapter_number = len(master_ids)
for chapter_id in master_ids:

    # Generate the url of the chapter.
    chapter_url = chapter_base + chapter_id

    # Download the page.
    print(f'Downloading from page {chapter_url}...') 
    res = requests.get(chapter_url)
    res.raise_for_status()
    chapter_res = res.text

    # Find the name of the chapter.
    chapter_name = re.search(f'"illustId":"{chapter_id}","illustTitle":"([^"]*)"', chapter_res)
    chapter_name = str(chapter_number) + '. ' + chapter_name.group(1)
    chapter_number -= 1
    #print(chapter_name + ':')

    # Find the URL of the first image.
    findPageRegex = re.compile(r'"original":"https://\S*/img-original/img/(\d{4}/(\d\d/){5}\d{8}_p)0(.\w*)"')
    page_id = findPageRegex.search(chapter_res)
    page_ext = page_id.group(3)
    page_id = page_id.group(1)
    
    # Download each image in the chapter.
    # Do this by taking the URL of the first chapter
    # (i.e. https://i.pximg.net/img-original/img/####/##/##/##/##/##/########_p0.xxx)
    # and replace the "p0" with "p1", then "p2", etc. until a 404 Error,
    # then move on to the next chapter.
    page_number = 0
    while True:
        page_url = page_base + page_id + str(page_number) + page_ext

        try:
            # Download the image.
            res = requests.get(page_url)
            res.raise_for_status()
            print(f'Downloading image {page_url}')
        except requests.exceptions.HTTPError:
            break

        # Save the image to ./pixiv_downloads/(chapter name)/(title).
        imageFile = open(os.path.join('pixiv_downloads', title, chapter_name, os.path.basename(page_url)), 'wb')
        for chunk in res.iter_content(100000):
            imageFile.write(chunk)
        imageFile.close()

        page_number += 1

print('Done.')
