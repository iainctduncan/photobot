from pyramid.response import Response
from pyramid.view import view_config
import transaction
from sqlalchemy.exc import DBAPIError

from ..models import Installation, Ping, Notification

from datetime import datetime, timedelta
import time
#from time import time as timemaker
import logging
log = logging.getLogger(__name__)

from .protector import *


@view_config(route_name='installations', renderer='../templates/installations.jinja2')
@view_config(route_name='home', renderer='../templates/installations.jinja2')
def installations_view(request):

    # the installations shows the latest ping from all active installations
    installations = request.dbsession.query(Installation).filter_by(display=True).all()
    subsystems = ['pi', 'usb', 'ptz','ais', 'disk', 'thermal']
    #subsystems = ['pi']

    protect_from_direct_access(request)


    # list of two field tuples of (installation, ping_dict)
    installs = []
    for installation in installations:
        ping_dict = dict()

        last_ping_datetime = None

        last_ping = installation.get_last_ping_by_subsystem(request.dbsession)
        if last_ping:
            installation.last_ping_time = last_ping.datetime

            last_ping_datetime = last_ping.datetime #datetime.strptime(last_ping.datetime,'%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            now_ts = time.mktime(now.timetuple())
            last_ts = time.mktime(last_ping_datetime.timetuple())

            diff = now_ts - last_ts

            if diff < 3600:
                installation.last_ping_class = "RecentPing"
            elif diff < 10800:
                installation.last_ping_class = "MediumPing"
            else:
                installation.last_ping_class = "OldPing"
        else:
            installation.last_ping_time = "N/A"
            installation.last_ping_class = "MissingPing"
            #with transaction.manager as tx:
            #    request.dbsession.execute("delete from installation where id = " + str(installation.id))
            #    tx.commit()
            #request.dbsession.commit()

        active_subsystems = []

        if last_ping_datetime:
            one_day_before_last_ping = last_ping_datetime - timedelta(days=1)
            one_day_before_last_ping_for_mysql = one_day_before_last_ping.strftime('%Y-%m-%d %H:%M:%S')
            active_systems_query = "SELECT subsystem FROM ping WHERE  ping.installation_uid='" + installation.uid + "' and ping.datetime > '" + one_day_before_last_ping_for_mysql + "' group by subsystem "

            #print(active_systems_query)
            result_proxy = request.dbsession.execute(active_systems_query)
            #print(active_subsystems)


            for rowproxy in result_proxy:
                active_subsystems.append(rowproxy[0])

            #if not active_subsystems:
            #    active_subsystems = subsystems

        print(active_subsystems)

        for subsystem in active_subsystems:

            subsystem_ping = installation.get_last_ping_by_subsystem(request.dbsession, subsystem)

            if subsystem_ping :
                subsystem_status = subsystem_ping.status
                if subsystem_status=='OK':
                    subsystem_last_ping_ts = time.mktime(subsystem_ping.datetime.timetuple())
                    age_in_seconds =  now_ts - subsystem_last_ping_ts
                    if age_in_seconds > 5000:
                        subsystem_status = "Stale"
            else:
                subsystem_status = "?"

            ping_dict[subsystem] = subsystem_status
        installs.append( dict(installation=installation, ping_dict=ping_dict))

    return dict(installs=installs)
