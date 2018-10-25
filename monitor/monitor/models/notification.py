from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    DateTime,
    String,
    ForeignKey
)
from sqlalchemy.orm import relationship

from .meta import Base

class Notification(Base):
    """
    A request for a notification from an installation
    """
    __tablename__ = 'notification'
    id = Column(Integer, primary_key=True)
    installation_id = Column(Integer, ForeignKey('installation.id'), nullable=False)
    installation_uid = Column(String(255))
    datetime = Column(DateTime, nullable=False)
    # notification key, ie: 'mount_error', 'disk_full', etc
    key = Column(Text)
    # json body of the notification payload
    json = Column(Text)

    installation = relationship("Installation", backref="notifications")

    def __repr__(self):
        return "Notification: %s %s %s" % (self.installation_uid, self.key, self.datetime)

