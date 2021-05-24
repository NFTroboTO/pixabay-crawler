import json
import csv
import pixabay
import os
import requests
import time
import random
from PIL import Image

config = json.load(open('./pixabay_config.json', 'r'))
API_KEY = config['pixabay_api_key']

save_root = config['save_root']

keywords_file = open(config['keywords_file'], 'r')
keywords_tag_dic = json.load(keywords_file)
keywords = keywords_tag_dic.keys()

url_keys = config['url_keys']
pb = pixabay.Image(API_KEY)

fields = ['id', 'tags', 'imageWidth', 'imageHeight', 'pageURL', 'pixabay_url']

for ikeyword in keywords:
    im_dir = os.path.join(save_root, 'Img', ikeyword)
    lic_dir = os.path.join(save_root, 'Lic', ikeyword)
    os.makedirs(im_dir, exist_ok=True)
    os.makedirs(lic_dir, exist_ok=True)

    csvpath = os.path.join(lic_dir, (str(ikeyword) + '.csv'))
    with open(csvpath, 'w') as f:
        writer = csv.DictWriter(f, fieldnames = fields)
        writer.writeheader()

    for ipage in range(1, config['npage'] + 1):
        # Searching
        try:
            ipb_json = pb.search(q=keywords_tag_dic[ikeyword],
                                 image_type='photo',
                                 per_page=200,
                                 page=ipage)
        except Exception as e:
            print('Walking Error')
            continue

        # download images and make license_jsons
        photos = ipb_json['hits']
        for photo in photos:
            url_keys_list = url_keys.replace(' ', '').split(',')
            for item in url_keys_list:
                url = photo.get(item)
                if url != None:
                    break

            if (str(url) != "None"):
                print(url)
                try:
                    response = requests.get(url)
                    ipath = os.path.join(im_dir,
                                         (str(photo.get('id')) + "." +
                                          os.path.basename(url).split(".")[1]))
                    with open(ipath, 'wb+') as f:
                        f.write(response.content)

                    with Image.open(ipath) as img:
                        width = img.width
                        height = img.height

                    photo_dic = {
                        'id': str(photo.get('id')),
                        'tags': photo.get('tags'),
                        'imageWidth': width,
                        'imageHeight': height,
                        'pageURL': photo.get('pageURL'),
                        'pixabay_url': url
                    }

                    with open(csvpath, 'a+') as f:
                        writer = csv.DictWriter(f, fieldnames = fields)
                        writer.writerow(photo_dic)

                    time.sleep(3 * random.random())

                except Exception as e:
                    print(str(e))
                    continue
