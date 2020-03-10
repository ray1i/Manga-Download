# !python3
# downloadPixiv.py - Downloads manga from pixiv

import requests, os, bs4, re
     
master_url = input('Enter the URL of the chapter list:  ')  # Url of chapter list
chapter_base = 'https://www.pixiv.net/en/artworks/'
page_base = 'https://tc-pximg01.techorus-cdn.com/img-original/img/'

# Load the master list.
print(f'Loading page {master_url} ...') 
master_res = requests.get(master_url)
master_res.raise_for_status()
master_res = master_res.text

# Find the title of the manga
findTitleRegex = re.compile(r'<title>「(\w*)」/')
title = findTitleRegex.search(master_res)
title = title.group(1)
os.makedirs(os.path.join("pixiv_downloads", title), exist_ok=True)   # Store comics in ./pixiv_downloads/(title)

# Search master list for all the chapters, put their ids into a list.
findChaptersRegex = re.compile(r'image-item"><a href="/artworks/(\d{8})')
master_ids = findChaptersRegex.findall(master_res)

for chapter_id in master_ids:

    # Generate the url of the chapter.
    chapter_url = chapter_base + chapter_id

    # Download the page.
    print(f'Downloading from page {chapter_url}...') 
    res = requests.get(chapter_url)
    res.raise_for_status()
    chapter_res = res.text

    # Find the URL of the first image.
    findPageRegex = re.compile(r'"original":"https://\S*/img-original/img/(\d{4}/(\d\d/){5}\d{8}_p)0(.\w*)"')
    page_id = findPageRegex.search(chapter_res)
    page_ext = page_id.group(3)
    page_id = page_id.group(1)
    
    # Download each image in the chapter.
    # Do this by taking the URL of the first chapter
    # (i.e. https://tc-pximg01.techorus-cdn.com/img-original/img/####/##/##/##/##/##/########_p0.xxx)
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

        # Save the image to ./pixiv_downloads/(title).
        imageFile = open(os.path.join('pixiv_downloads', title, os.path.basename(page_url)), 'wb')
        for chunk in res.iter_content(100000):
            imageFile.write(chunk)
        imageFile.close()

        page_number += 1

print('Done.')
