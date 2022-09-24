"""Object relational mapper for connecting to the application database and
managing underlying database constructs.

Module Contents
---------------
"""

from __future__ import annotations

from typing import Callable

from sqlalchemy import Column, DateTime, Integer, MetaData, String, create_engine, func
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker, validates

from app.settings import ApplicationSettings

Base = declarative_base()


class Notification(Base):
    """History of user notifications

    Fields:
      - id         (Integer): Primary key for this table
      - username    (String): Unique account name
      - datetime  (DateTime): Datetime of the last user notification
      - threshold  (Integer): Disk usage threshold that triggered the notification
      - file_system (String): Name of the file system triggering the notification
    """

    __tablename__ = 'notification'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=False, onupdate=func.now())
    threshold = Column(Integer, nullable=False)
    file_system = Column(String, nullable=False)

    @validates('threshold')
    def validate_percent(self, key: str, value: int) -> int:
        """Verify the given value is between 0 and 100 (inclusive)

        Args:
            key: Name of the database column being tested
            value: The value to test

        Raises:
            ValueError: If the given value does not match required criteria
        """

        if 0 <= value <= 100:
            return value

        raise ValueError(f'Value for {key} column must be between 0 and 100 (got {value}).')


class DBConnection:
    """A configurable connection to the application database

    This class acts as the primary interface for connecting to the application
    database. Use the ``configure`` method to change the location of the
    underlying application database. Changes made via this class will
    propagate to the entire parent application.
    """

    connection: Connection = None
    engine: Engine = None
    url: str = None
    metadata: MetaData = Base.metadata
    session: Callable[[], Session] = None

    @classmethod
    def configure(cls, url: str = ApplicationSettings.db_url) -> None:
        """Update the connection information for the underlying database

        Changes made here will affect the entire running application

        Args:
            url: URL information for the application database
        """

        cls.url = url
        cls.engine = create_engine(cls.url)
        cls.metadata.create_all(cls.engine)
        cls.connection = cls.engine.connect()
        cls.session = sessionmaker(cls.engine)
