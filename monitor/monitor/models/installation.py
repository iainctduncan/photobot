from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    String,
)
import uuid

from .meta import Base

class Installation(Base):
    __tablename__ = 'installation'
    id = Column(Integer, primary_key=True)
    #py_serial = Column(Text)
    #uid = Column(String(255), nullable=False, unique=True)
    name = Column(Text)
    notes = Column(Text)
    ip_address = Column(Text)

    def __repr__(self):
        return "%s - %s" % (self.name, self.ip_address)

    # constructor to auto set the uid
    def __init__(self, **kwargs):
        self.uid = uuid.uuid4()
        for k,v in kwargs.items():
            setattr(self, k, v)