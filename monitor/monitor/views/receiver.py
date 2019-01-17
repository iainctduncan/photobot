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


import logging
log = logging.getLogger(__name__)

#@view_config(route_name='dashboard', renderer='../templates/dashboard.jinja2')
@view_config(route_name='receiver', renderer='string')
def receive_message(request):
    dbs = request.dbsession
    data = request.json_body
    bot_ip = request.remote_addr
    log.warning(data['name'])
    log.warning(bot_ip)

    new = Installation(
        name = data['name'],
        ip_address = bot_ip,
    )

    dbsession.add_all([new])
    return data
    #test = request.GET['test']
    #return Response('<body>Visit <a href="/howdy">'+test+'</a></body>')
