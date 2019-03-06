from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import Installation, Ping

import logging
log = logging.getLogger(__name__)

#@view_config(route_name='dashboard', renderer='../templates/dashboard.jinja2')
@view_config(route_name='dashboard', renderer='string')
def dashboard_view(request):

    # the dashboard shows the latest ping from all active installations
    installations = request.dbsession.query(Installation).all()

    log.info(" - installations: %s" % installations)
    return Response("OK.. installations: %s" % installations)





