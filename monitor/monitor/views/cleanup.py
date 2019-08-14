from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import Installation, Ping, Notification

import logging
from time import gmtime, strftime
import datetime

log = logging.getLogger(__name__)

@view_config(route_name='cleanup',renderer='../templates/cleanup.jinja2')
def cleanup(request):
    now = datetime.datetime.now()

    today = datetime.date.today()
    first = today.replace(day=1)
    lastMonth = first - datetime.timedelta(days=60)

    # the installations shows the latest ping from all active installations

    cutoff = lastMonth.strftime("%Y-%m-%d %H:%M:%S" )
    print(cutoff)


    installations = request.dbsession.execute("delete from ping where datetime<'" +cutoff +"' " )
    return {"msg": cutoff}







