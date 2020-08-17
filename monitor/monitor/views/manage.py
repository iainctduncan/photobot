from pyramid.response import Response
from pyramid.view import view_config
import transaction
from sqlalchemy.exc import DBAPIError

from ..models import Installation, Ping, Notification

from pyramid.httpexceptions import HTTPFound

import pdb
import logging
log = logging.getLogger(__name__)


# the installations shows the latest ping from all active installations
@view_config(route_name='manage', renderer='../templates/manage.jinja2')
def manage_view(request):

    log.info("manage_view()")

    installations = request.dbsession.query(Installation).all()

    if 'op' in request.params:
        log.info("we have an op")
        op = request.params.get('op')
        uid = request.params.get('uid')

        installation = request.dbsession.query(Installation).filter_by(uid=uid).one()    

        log.info("working on bot: %s" % installation)

        if op == 'delete':
            log.info("deleting bot %s" % uid)
            # apparently we don't have our cascades set up right, so delete pings first
            with transaction.manager as tx:
                request.dbsession.query(Ping).filter_by(installation_id=installation.id).delete()
                tx.commit()
                request.dbsession.query(Installation).filter_by(uid=uid).delete()
                tx.commit()
            log.info("DELETED")

        elif op == 'show':
            installation.display = True
            log.info("showing bot %s" % uid)
        elif op == 'hide':
            log.info("hiding bot %s" % uid)
            installation.display = False
        else:
            log.info("bad op or uid, doing nothing")     
        return HTTPFound("/manage") 
    else:
        return dict(installations=installations)
