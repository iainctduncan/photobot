import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars
from datetime import datetime, timedelta

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from ..models import Installation, Recipient, Notification, Ping

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        i1 = Installation(
            name = "Mayne Island",
            ip_address = "1.0.0.1",
            uid = "1-MI",
            active=True,
            pings = [
                Ping(installation_uid="1-MI", datetime=datetime.now() - timedelta(minutes=1)),
                Ping(installation_uid="1-MI", datetime=datetime.now() - timedelta(minutes=2)),
                Ping(installation_uid="1-MI", datetime=datetime.now() - timedelta(minutes=3)),
                Ping(installation_uid="1-MI", datetime=datetime.now() - timedelta(minutes=4)),
                Ping(installation_uid="1-MI", datetime=datetime.now() - timedelta(minutes=5)),
            ]
        )
        i2 = Installation(
            name = "Saltspring Island",
            ip_address = "1.0.0.2",
            uid = "2-SI",
            active=True,
            pings = [
                Ping(installation_uid="2-SI", datetime=datetime.now() - timedelta(minutes=1)),
                Ping(installation_uid="2-SI", datetime=datetime.now() - timedelta(minutes=2)),
                Ping(installation_uid="2-SI", datetime=datetime.now() - timedelta(minutes=3)),
                Ping(installation_uid="2-SI", datetime=datetime.now() - timedelta(minutes=4)),
                Ping(installation_uid="2-SI", datetime=datetime.now() - timedelta(minutes=5)),
            ]
        )
        i3 = Installation(
            name = "Pender Island",
            ip_address = "1.0.0.3",
            uid = "3-PI",
            active=True,
            pings = [
                Ping(installation_uid="2-SI", datetime=datetime.now() - timedelta(minutes=2)),
                Ping(installation_uid="2-SI", datetime=datetime.now() - timedelta(minutes=3)),
                Ping(installation_uid="2-SI", datetime=datetime.now() - timedelta(minutes=4)),
                Ping(installation_uid="2-SI", datetime=datetime.now() - timedelta(minutes=5)),
            ]
        )
        i4 = Installation(
            name = "San Juan Island",
            ip_address = None,
            uid = "4-SJI",
            active=False
        )

        iain = Recipient(
            name_last = "Duncan",
            name_first = "Iain",
            email = "iainctduncan@gmail.com",
            active = True
        )
        nev = Recipient(
            name_last = "Gibson",
            name_first = "Nev",
            email = "nev@indivision.ca",
            active = True
        )
        dbsession.add_all([i1,i2,i3,i4, iain, nev])
