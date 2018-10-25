from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    DateTime,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .meta import Base

class Ping(Base):
    """
    A health check ping from an installation
    """
    __tablename__ = 'ping'
    id = Column(Integer, primary_key=True)
    installation_id = Column(Integer, ForeignKey('installation.id'), nullable=False)
    installation_uid = Column(String(255))
    datetime = Column(DateTime, nullable=False)
    json = Column(Text)

    installation = relationship("Installation", backref="pings")

    def __repr__(self):
        return "%s - %s" % (self.name, self.ip_address)

