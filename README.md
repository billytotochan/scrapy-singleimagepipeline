Single Image Pipeline for Scrapy
==================================================

Why multiple images store together in one item?

IMAGES_STORE

    <IMAGES_STORE>/full/<image_id>.jpg ==> <IMAGES_STORE>/<SPIDER_NAME>/full/<image_id>.jpg

IMAGES URLS FIELD

    item['image_urls'] = ['a'] ==> item['image_url'] = 'a'

IMAGES RESULT FIELD

    item['image_paths'] = ['a.jpg'] ==> item['image_path'] = 'a.jpg'


Install
----------

    pip install scrapy-singleimagepipeline


Examples Output
----------

    id     | image_path                    | image_thumb      | image_name  | image_url
    ------------------------------------------------------------------------------------------------------------------------
    1      | foo/full/1.jpg                | full             | 1           | http://full.jpg
    2      | foo/thumbs/small/1.jpg        | small            | 1           | http://small.jpg
    3      | foo/thumbs/small/checksum.jpg | small            |             | http://small.jpg
    4      | foo/full/checksum.jpg         |                  |             | http://small.jpg
    5      | foo/full/checksum.jpg         |                  | 1           | http://no_rename.jpg

Settings
----------

Please refer to https://doc.scrapy.org/en/latest/topics/media-pipeline.html#using-the-images-pipeline for other image settings.

    # IMAGE RENAME
    IMAGES_RENAME = False

    # FIELD FOR UPDATE THE FILENAME
    # PLEASE REMIND THAT I DO NOT HANDLE FOR DUPLICATE FILENAME
    IMAGES_NAMES_FIELD = 'image_name'

    # IMAGE THUMB RESIZE
    # IF TRUE, ALSO SET THE IMAGES_THUMBS PARAMETER
    # IMAGE RESIZES BASE ON IMAGES_THUMB_FIELD
    IMAGES_THUMBS_RESIZE = False
    IMAGES_THUMBS = {
        'small': (60, 60),
        'big': (600, 600),
    }

    # FIELD FOR UPDATE THE STORAGE DIRECOTORY
    IMAGES_THUMBS_FIELD = 'image_thumb'

    ITEM_PIPELINES = {
        ...
        'scrapy.pipelines.images.ImagesPipeline': None,
        'singleimagepipeline.images.SingleImagePipeline': 1,
        ...
    }