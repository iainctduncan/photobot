from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import Installation, Ping

import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from ..models import Installation, Recipient, Notification, Ping
from datetime import datetime

import logging
log = logging.getLogger(__name__)

#@view_config(route_name='dashboard', renderer='../templates/dashboard.jinja2')
@view_config(route_name='receiver', renderer='string')
def receive_message(request):
    dbs = request.dbsession
    data = request.json_body
    bot_ip = request.remote_addr
    log.info("received request from %s: %s" % (bot_ip, data) )

    installation_id = "1-MI" # data['installation_id']
    # look up the installation from the incoming uid
    installation = dbs.query(Installation).filter_by(uid=installation_id).one()
    if not installation:
        return {'status': 'ERROR', 'error':'Bad Installation UID'}

    #update installation
    installation.ip_address=bot_ip
    dbs.commit()

    # create a new ping
    ping = Ping(
        installation_uid = installation.uid,
        datetime = datetime.now(),

        status = data['status']
    )
    installation.pings.append(ping)
    return {'status': 'OK'}

