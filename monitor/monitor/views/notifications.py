from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import Installation, Ping, Notification

import logging
log = logging.getLogger(__name__)

@view_config(route_name='notifications', renderer='../templates/notifications.jinja2')
def notifications_view(request):

    # the notifications shows the latest ping from all active installations
    notifications = request.dbsession.query(Notification).all()

    return dict(notifications=notifications)





