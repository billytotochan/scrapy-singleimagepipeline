Custom Images Pipeline for Scrapy
==================================================

Get inspiration from https://stackoverflow.com/questions/18081997/scrapy-customize-image-pipeline-with-renaming-defualt-image-name

Install
----------

The quick way:

    pip install scrapy-custom-imagepipeline

Or checkout the source and run

    python setup.py install


Examples
----------

0 Each Item has x images downloaded and x images saved

    id     | image_paths                         | image_thumbs     | image_names | image_urls        
    ------------------------------------------------------------------------------------------------------------------------
    1      | ['full/1.jpg','thumbs/small/1.jpg'] | ['full','small'] | ['1','1']   | ['http://big.jpg','http://small.jpg']   
    2      | ['full/sum1.jpg','full/sum2.jpg']   | ['full','full']  | []          | ['http://big.jpg','http://small.jpg']
    3      | ['full/1.jpg']                      | ['full','small'] | ['1','1']   | ['http://big.jpg'] 
    4      | ['full/1.jpg','full/sum.jpg']       | ['full','full']  | ['1']       | ['http://big.jpg','http://small.jpg']  
    5      | ['full/1.jpg','thumbs/small/1.jpg'] | ['full','small'] | ['1']       | ['http://big.jpg','http://big.jpg']   
    6      | ['full/1.jpg','full/1.jpg']         | ['full','full']  | ['1']       | ['http://big.jpg','http://small.jpg']   

1 Each Item has only one image downloaded and only one image saved

    Different size of images available for download

    id     | image_paths                         | image_thumbs     | image_names | image_urls        
    ------------------------------------------------------------------------------------------------------------------------
    1      | full/1.jpg                          | full             | 1           | http://big.jpg   
    2      | thumbs/small/1.jpg                  | small            | 1           | http://small.jpg 
    3      | thumbs/small/sum.jpg                | small            |             | http://small.jpg 

Settings
----------

Please refer to https://doc.scrapy.org/en/latest/topics/media-pipeline.html for other image settings.

    # CUSTOM MODE
    # 0, 1
    IMAGES_PIPELINE_MODE = 0

    # FILENAME RENAME
    IMAGES_RENAME = False

    # FIELD FOR UPDATE THE FILENAME
    IMAGES_NAMES_FIELD = 'image_names'
    
    # THUMB GENERATION (This will REALLY generate a thumbnail depends on its `IMAGES_THUMBS_PATH_FIELD`)
    IMAGES_THUMBS_RESIZE = False

    # FIELD FOR UPDATE THE STORAGE DIRECOTORY
    IMAGES_THUMBS_PATH_FIELD = 'image_thumbs'


spider.py
----------

