from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import Installation, Ping, Notification

import logging
log = logging.getLogger(__name__)

@view_config(route_name='installations', renderer='../templates/installations.jinja2')
def installations_view(request):

    # the installations shows the latest ping from all active installations
    installations = request.dbsession.query(Installation).all()



    return dict(installations=installations)





