# -*- coding: utf-8 -*-
import logger
import re
from scrapy.http import Request
from scrapy.settings import Settings
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline

log = logging.getLogger('scrapy.pipelines.image.custom')

class SingleImagePipeline(ImagesPipeline):
    CONVERTED_ORIGINIAL = re.compile('^full/[0-9,a-f]+.jpg$')

    DEFAULT_IMAGE_URL_FIELD = 'image_url'
    DEFAULT_IMAGE_RESULT_FIELD = 'image_path'
    DEFAULT_IMAGE_THUMB_FIELD = 'image_thumb'
    DEFAULT_IMAGE_NAME_FIELD = 'image_name'

    DEFAULT_IMAGE_THUMB = 'full'
    DEFAULT_IMAGE_NAME = 'iF-NamE-eqUAL-mE-uSE-deFaULT-chECKsuM-aS-fiLEnaME'

    def __init__(self, store_uri, download_func=None, settings=None):
        super(SingleImagePipeline, self).__init__(
            store_uri,
            settings=settings,
            download_func=download_func
        )

        if isinstance(settings, dict) or settings is None:
            settings = Settings(settings)

        self.images_thumb_resize = settings.get('IMAGES_THUMB_RESIZE', False)
        self.images_rename = settings.get('IMAGES_RENAME', False)

        if not hasattr(self, 'IMAGES_THUMBS_FIELD'):
            self.IMAGES_THUMB_FIELD = self.DEFAULT_IMAGE_THUMB_FIELD

        if not hasattr(self, 'IMAGES_NAMES_FIELD'):
            self.IMAGES_NAME_FIELD = self.DEFAULT_IMAGE_NAME_FIELD

        if not hasattr(self, 'IMAGES_URLS_FIELD'):
            self.IMAGES_URL_FIELD = self.DEFAULT_IMAGE_URL_FIELD

        if not hasattr(self, 'IMAGES_RESULTS_FIELD'):
            self.IMAGES_RESULT_FIELD = self.DEFAULT_IMAGE_RESULT_FIELD

        self.image_thumb_field = settings.get(
            'IMAGES_THUMBS_FIELD',
            self.IMAGES_THUMB_FIELD
        )

        self.image_name_field = settings.get(
            'IMAGES_NAMES_FIELD',
            self.IMAGES_NAME_FIELD
        )

        self.image_url_field = settings.get(
            'IMAGES_URLS_FIELD',
            self.IMAGES_URL_FIELD
        )

        self.image_result_field = settings.get(
            'IMAGES_RESULT_FIELD',
            self.IMAGES_RESULT_FIELD
        )

        if (self.images_thumb_resize) and (self.thumbs is None):
            raise KeyError('IMAGE_THUMBS setting is missing')

        self.custom_thumbs = self.thumbs
        self.thumbs = {}

    def get_media_requests(self, item, info):
        try:
            image_url = item.get(
                self.image_url_field,
                ''
            )
            image_thumb = item.get(
                self.image_thumb_field,
                self.DEFAULT_IMAGE_THUMB
            )
            image_name = item.get(
                self.image_name_field,
                self.DEFAULT_IMAGE_NAME
            )

            yield Request(image_url, meta={
                'image_thumb': image_thumb,
                'image_name': image_name
            })
        except KeyError:
            log.warning('Item doesn\'t have field : {}'.format(
                self.image_url_field))
            pass

    def get_images(self, response, request, info):
        thumb_id = response.meta['image_thumb']
        for path, image, buf in super(SingleImagePipeline, self).get_images(
            response, request, info
        ):
            if self.images_thumb_resize and thumb_id != self.DEFAULT_IMAGE_THUMB_ID:
                :
                image, buf = super(SingleImagePipeline, self).convert_image(
                    image, self.custom_thumbs[thumb_id]
                )
            yield path, image, buf

    def item_completed(self, results, item, info):
        if isinstance(item, dict) or self.image_result_field in item.fields:
            image_paths = [x['path'] for ok, x in results if ok]
            log.info('{} Image saved succesfully'.format(len(image_paths)))
            if image_paths:
                item[self.image_result_field] = image_paths[0]
        return item

    def file_path(self, request, response=None, info=None):
        path = super(SingleImagePipeline, self).file_path(
            request, response=response, info=info
        )
        thumb_id = request.meta['image_thumb']
        name_id = request.meta['image_name']
        if self.converted_original.match(path):
            if (self.images_rename) and (name_id != self.DEFAULT_IMAGE_NAME):
                path = self.update_file_name(name_id)

            path = prepend_path(path, spider_name)
            if thumb_id != self.DEFAULT_IMAGE_THUMB_ID:
                path = self.update_thumbpath(path, thumb_id)
        log.debug('Image will be saved ==> {}'.format(path))
        return path

    def prepend_path(self, path, spider_name):
        return path.replace('full', spider_name + '/full')

    def update_thumb_path(self, path, thumb_id):
        return path.replace('/full', '/thumbs/' + thumb_id)

    def update_file_name(self, name):
        return 'full/{}.jpg'.format(name)
