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
    pi_cpu_id = data['pi_cpu_id']

    installation_id = data['installation_id']

    # if we have an installation_uid use it to get the apropriate installation
    # if we don't have an installation id (pi not properly configured) look up based on pi cpu serial
    if installation_id:
        installation = dbs.query(Installation).filter_by(uid=installation_id).first()
    else:
        installation = dbs.query(Installation).filter_by(pi_cpu_id=data['pi_cpu_id']).first()

    if not installation:
        installation = Installation(
            uid=installation_id,
            pi_cpu_id=data['pi_cpu_id'],
            ip_address = bot_ip,
            name = data['name']
        )
        dbs.add(installation)

    #update installation
    installation.ip_address=bot_ip
    installation.pi_cpu_id=pi_cpu_id

    # create a new ping
    ping = Ping(
        installation_uid = installation.uid,
        datetime = datetime.now(),
        status = data['status'],
        msg=data['msg']
    )
    installation.pings.append(ping)
    return {'status': 'OK'}