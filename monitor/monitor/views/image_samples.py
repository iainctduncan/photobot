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

#@view_config(route_name='dashboard', renderer='../templates/dashboard.jinja2')
@view_config(route_name='image_samples', renderer='../templates/photosample.jinja2')
def image_sample(request):

    path = request.registry.settings['image_samples_dir']
    images = os.listdir(path)

    samples = []

    for image in images:
        sample = ImageSample(image)
        samples.append(sample)
           # log.info(" - installations: %s" % installations)

    return dict(samples=samples)
    #return Response(output)

