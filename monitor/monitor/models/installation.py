from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    String,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy import desc

import uuid

from .meta import Base

import pdb

from datetime import datetime, timedelta
from .ping import Ping

# TODO: get from settings
PING_THRESHOLD = 3600

class Installation(Base):
    __tablename__ = 'installation'
    id = Column(Integer, primary_key=True)
    uid = Column(String(255), nullable=False, unique=True)
    name = Column(Text)
    pi_cpu_id=Column(Text)
    dataplicity_hash=Column(Text)
    config_json=Column(Text)
    ip_address = Column(Text)
    active = Column(Boolean)
    notes = Column(Text)
    display = Column(Boolean)   # do I show up on the dashboard?

    pings = relationship("Ping", order_by=desc("ping.datetime"),lazy='dynamic', backref="installation")
    #pings = relationship("Ping", order_by=desc("ping.datetime"), backref="installation")

    def __repr__(self):
        return "%s - %s" % (self.name, self.ip_address)

    # constructor to auto set the uid
    def __init__(self, **kwargs):
        self.uid = uuid.uuid4()
        for k,v in kwargs.items():
            setattr(self, k, v)

    # 2020-01-29 filter only ask for pings in the last week
    def get_last_ping_by_subsystem(self, session, subsystem=None):
        query = session.query(Ping).filter(Ping.installation_id == self.id)
        query = query.filter_by(subsystem=subsystem) if subsystem else query
        # adding the below
        query = query.filter(Ping.datetime >= datetime.today() - timedelta(days=7))
        query = query.order_by(desc(Ping.datetime)).limit(1)
        return query.first()

