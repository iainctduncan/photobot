from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import Installation, Ping, Notification

import logging
log = logging.getLogger(__name__)
from .protector import *

@view_config(route_name='pings_by_install', renderer='../templates/pings.jinja2')
def pings_by_install(request):
    protect_from_direct_access(request)

    install_id = request.matchdict.get('install')
    log.info(install_id)
    # the installations shows the latest ping from all active installations
    pings = request.dbsession.query(Ping).filter(Ping.installation_uid==install_id).order_by(Ping.datetime.desc()).limit(150).all()

    return dict(pings=pings)

@view_config(route_name='pings_by_subsystem', renderer='../templates/pings.jinja2')
def pings_by_subsystem(request):
    protect_from_direct_access(request)

    install_id = request.matchdict.get('install')
    subsystem = request.matchdict.get('subsystem')
    log.info(install_id)
    # the installations shows the latest ping from all active installations
    pings = request.dbsession.query(Ping).filter(Ping.installation_uid==install_id).filter(Ping.subsystem==subsystem).order_by(Ping.datetime.desc()).limit(150).all()

    return dict(pings=pings)


@view_config(route_name='pings', renderer='../templates/pings.jinja2')
def pings(request):
    protect_from_direct_access(request)

    # the installations shows the latest ping from all active installations
    pings = request.dbsession.query(Ping).order_by(Ping.datetime.desc()).limit(150).all()

    return dict(pings=pings)
