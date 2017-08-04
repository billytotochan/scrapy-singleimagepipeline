# -*- coding: utf-8 -*-
import logger
import re
from scrapy.http import Request
from scrapy.settings import Settings
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline

log = logging.getLogger('scrapy.pipelines.image.custom')

class Mode:
    ORIGINAL = 0
    ONE_IMAGE_ONE_THUMB = 1
    MULTIPLE_IMAGES_MULTIPLE_THUMBS = 2

class CustomImagesPipeline(ImagesPipeline):
    CONVERTED_ORIGINIAL = re.compile('^full/[0-9,a-f]+.jpg$')
    DEFAULT_IMAGES_THUMBS_FIELD = 'image_thumbs'
    DEFAULT_IMAGE_THUMB_ID = 'full'
    DEFAULT_IMAGES_NAMES_FIELD = 'image_names'
    DEFAULT_IMAGE_NAME = 'iF-NamE-eqUAL-mE-uSE-deFaULT-chECKsuM-aS-fiLEnaME'

    def __init__(self, store_uri, download_func=None, settings=None):
        super(CustomImagesPipeline, self).__init__(
            store_uri, 
            settings=settings,
            download_func=download_func
        )
        
        if isinstance(settings, dict) or settings is None:
            settings = Settings(settings)

        self.thumbs_resize = settings.get('IMAGES_THUMBS_RESIZE', False)
        self.rename = settings.get('IMAGES_RENAME', False)
        self.mode = settings.get('IMAGES_PIPELINE_MODE', Mode.ORIGINAL)

        if not hasattr(self, 'IMAGES_THUMBS_FIELD'):
            self.IMAGES_THUMBS_FIELD = self.DEFAULT_IMAGES_THUMBS_FIELD

        if not hasattr(self, 'IMAGES_NAMES_FIELD'):
            self.IMAGES_NAMES_FIELD = self.DEFAULT_IMAGES_NAMES_FIELD

        self.images_thumbs_field = settings.get(
            'IMAGES_THUMBS_FIELD',
            self.IMAGES_THUMBS_FIELD
        )

        self.images_names_field = settings.get(
            'IMAGES_NAMES_FIELD',
            self.IMAGES_NAMES_FIELD
        )

        if (self.thumbs_resize) and (self.thumbs is None):
            raise KeyError('IMAGES_THUMBS setting is missing')

        self.custom_thumbs = self.thumbs
        self.thumbs = {}

    def get_media_requests(self, item, info):
        try:
            if self.mode == Mode.ONE_IMAGE_ONE_THUMB:
                image_url = item.get(
                    self.images_urls_field, ''
                )
                image_thumb = item.get(
                    self.image_thumb_field, self.DEFAULT_IMAGE_THUMB_ID
                )
                image_name = item.get(
                    self.image_name_field, self.DEFAULT_IMAGE_NAME
                )

                yield Request(image_url, meta={
                    'image_thumb': image_thumb,
                    'image_name': image_name
                })

            elif self.mode == Mode.MULTIPLE_IMAGES_MULTIPLE_THUMBS:
                image_urls = item.get(self.images_urls_field, [])
                image_thumbs = item.get(self.images_thumbs_field, [])
                image_thumbs = map(lambda x, y: y if x is None else x, 
                    image_thumbs, [DEFAULT_IMAGE_THUMB_ID]*len(image_urls))
                image_names = item.get(self.images_names_field, [])
                image_names = map(lambda x, y: y if x is None else x, 
                    image_names, [DEFAULT_IMAGE_NAME]*len(image_urls))

                return [Request(u, meta={
                    'image_thumb': i, 
                    'image_name': n
                }) for u, i, n in zip(image_urls, image_thumbs, image_names)]
            else:
                return [Request(x) for x in item.get(self.images_urls_field, [])]
        except KeyError:
            log.warning('Item doesn\'t have field : {}'.format(self.images_urls_field))
            pass

    def get_images(self, response, request, info):
        thumb_id = response.meta['image_thumb']
        for path, image, buf in super(CustomImagesPipeline, self).get_images(
                response, request, info
            ):
            if self.thumbs_resize and thumb_id != self.DEFAULT_IMAGE_THUMB_ID::
                image, buf = super(CustomImagesPipeline, self).convert_image(
                    image, self.custom_thumbs[thumb_id]
                )
            yield path, image, buf

    def item_completed(self, results, item, info):
        if isinstance(item, dict) or self.images_result_field in item.fields:
            if self.mode == Mode.ONE_IMAGE_ONE_THUMB:
                image_paths = [x['path'] for ok, x in results if ok]
                log.info('{} Image saved succesfully'.format(len(image_paths)))
                if image_paths:
                    item[self.images_result_field] = image_paths[0]
            elif self.mode == Mode.MULTIPLE_IMAGES_MULTIPLE_THUMBS:
                image_paths = [x['path'] for ok, x in results if ok]
                log.info('{} Images saved succesfully'.format(len(image_paths)))
                item[self.images_result_field] = image_paths
            else:
                item[self.images_result_field] = [x['path'] for ok, x in results if ok]
        return item

    def file_path(self, request, response=None, info=None):
        path = super(CustomImagesPipeline, self).file_path(
            request, response=response, info=info
        )
        thumb_id = response.meta['image_thumb']
        name_id = response.meta['image_name']
        if self.converted_original.match(path):
            if (self.rename) and (name_id != self.DEFAULT_IMAGE_NAME):
                path = self.update_file_name(name_id)
            if thumb_id != self.DEFAULT_IMAGE_THUMB_ID:
                path = self.update_thumbpath(path, thumb_id)
        log.debug('Image will be saved ==> {}'.format(path))
        return path

    def update_thumb_path(self, path, thumb_id):
        return path.replace('full', 'thumbs/'+thumb_id)

    def update_file_name(self, name):
        return 'full/{}.jpg'.format(name)
