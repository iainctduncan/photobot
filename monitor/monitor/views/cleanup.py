from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc

from ..models import Installation, Ping, Notification

import logging
from time import gmtime, strftime
import datetime

log = logging.getLogger(__name__)

@view_config(route_name='cleanup',renderer='../templates/cleanup.jinja2')
def cleanup(request):
    now = datetime.datetime.now()

    installations = request.dbsession.query(Installation).all()
    subsystems = ['pi', 'usb', 'ptz','ais', 'disk', 'thermal']

    # delete all pings going back more than 500 for each subsystem
    pings_to_keep = 500
    # query each subsystem for total, ordering by datetime desc,
    # and get the datetime of the 200th most recent ping
    ping_thresholds = []
    for installation in installations:
        for subsystem in subsystems:
            recent_pings = request.dbsession.query(Ping
                ).filter(Installation.id == installation.id
                ).filter_by(subsystem=subsystem
                ).order_by( desc(Ping.datetime)
                ).limit(pings_to_keep).all()
            #log.info("found %i recent pings for %s %s" % (len(recent_pings), installation, subsystem))
            if len(recent_pings) >= pings_to_keep:
                id_threshold = recent_pings[-1].id
                # delete the rest
                #log.info("Most recent %s %s is %i" % (installation, subsystem, recent_pings[0].id ))
                #log.info("Deleting %s %s under %i" % (installation, subsystem, id_threshold ))
                request.dbsession.query(Ping
                    ).filter_by(installation_id=installation.id
                    ).filter_by(subsystem=subsystem
                    ).filter(Ping.id < id_threshold ).delete()
                #log.info(" -- DONE")

    return Response("[HEALTHY]")









