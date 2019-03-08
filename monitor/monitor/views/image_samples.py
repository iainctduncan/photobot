from pyramid.response import Response
from pyramid.view import view_config
import os

from sqlalchemy.exc import DBAPIError

from ..models import Installation, Ping

import logging
log = logging.getLogger(__name__)

class ImageSample(object):
    def __init__(self,filename):
        self.filename=filename

@view_config(route_name='image_samples_by_install', renderer='../templates/photosample.jinja2')
def image_samples_by_install(request):
    install_id = request.matchdict.get('install_id')
    path = request.registry.settings['image_samples_dir']
    images = os.listdir(path)

    samples = []

    image_limit = 50
    image_count = 0
    for image in images:

        sample = ImageSample(image)

        if install_id in image:
            samples.append(sample)
            image_count = image_count + 1
            if image_count > image_limit:
                break
           # log.info(" - installations: %s" % installations)

    return dict(samples=samples)

@view_config(route_name='image_samples', renderer='../templates/photosample.jinja2')
def image_sample(request):

    path = request.registry.settings['image_samples_dir']
    images = os.listdir(path)

    samples = []

    image_limit = 50
    image_count = 0
    for image in images:

        sample = ImageSample(image)


        if '.jpg' in image:
            samples.append(sample)
            image_count = image_count + 1
            if image_count > image_limit:
                break
           # log.info(" - installations: %s" % installations)

    return dict(samples=samples)
    #return Response(output)

