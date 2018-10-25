from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    DateTime,
    Boolean
)

from .meta import Base

class Recipient(Base):
    """
    A recipient of notifications
    Entry of someone here, as active means they will get email notifications
    """
    __tablename__ = 'recipient'
    id = Column(Integer, primary_key=True)
    name_first = Column(Text, nullable=False)
    name_last = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    active = Column(Boolean, default=True)

    def __repr__(self):
        return "%s %s - %s" % (self.name_last, self.name_first, self.email)

