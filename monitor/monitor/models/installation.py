from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    String,
    Boolean
)
import uuid

from .meta import Base

import pdb

from datetime import datetime

# TODO: get from settings
PING_THRESHOLD = 120

class Installation(Base):
    __tablename__ = 'installation'
    id = Column(Integer, primary_key=True)
    uid = Column(String(255), nullable=False, unique=True)
    name = Column(Text)
    ip_address = Column(Text)
    active = Column(Boolean)
    notes = Column(Text)

    def __repr__(self):
        return "%s - %s" % (self.name, self.ip_address)

    # constructor to auto set the uid
    def __init__(self, **kwargs):
        self.uid = uuid.uuid4()
        for k,v in kwargs.items():
            setattr(self, k, v)

    @property
    def last_ping(self):
        return self.pings[0] if len(self.pings) else None

    @property
    def status(self):
        "return OK if last health check was within X minutes, else ERROR"
        if not self.last_ping:
            return "N/A"
        else:
            delta = datetime.now() - self.last_ping.datetime
            if delta.total_seconds() > PING_THRESHOLD:
                return "ERROR"
            else:
                return "OK"
