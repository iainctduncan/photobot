from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import Installation, Ping, Notification

import logging
log = logging.getLogger(__name__)

@view_config(route_name='installations', renderer='../templates/installations.jinja2')
@view_config(route_name='home', renderer='../templates/installations.jinja2')
def installations_view(request):

    # the installations shows the latest ping from all active installations
    installations = request.dbsession.query(Installation).all()

    subsystems = ['pi', 'usb', 'ptz','ais', 'disk', 'thermal']
    # list of two field tuples of (installation, ping_dict)
    installs = []
    for installation in installations:
        ping_dict = dict()

        last_ping = installation.get_last_ping_by_subsystem(request.dbsession)
        if last_ping:
            installation.last_ping_time = last_ping.datetime
        else:
            installation.last_ping_time = "N/A"

        for subsystem in subsystems:

            subsystem_ping = installation.get_last_ping_by_subsystem(request.dbsession, subsystem)

            if subsystem_ping :
                subsystem_status = subsystem_ping.status
            else:
                subsystem_status = "N/A"

            ping_dict[subsystem] = subsystem_status
        installs.append( dict(installation=installation, ping_dict=ping_dict))

    return dict(installs=installs)





