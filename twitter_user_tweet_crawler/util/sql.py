from sqlalchemy import Column, Integer, String, create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..util.config import config

engine = create_engine(f"sqlite:///{config['save']}/index.db", echo=False)
Base = declarative_base()


def set_journal_mode(connection, branch):
    connection.execute("PRAGMA journal_mode=WAL;")


event.listen(engine, 'connect', set_journal_mode)


class Table(Base):
    __tablename__: str = "info"
    id = Column(Integer, primary_key=True)
    location = Column(String, nullable=True)
    time = Column(Integer)


def is_id_exists(id_value: int):
    result = session.query(Table.id).filter_by(id=id_value).scalar() is not None
    return result


def insert_new_record(id_value: int, time_value: int, location_value: None | str):
    new_record = Table(id=id_value, time=time_value, location=location_value)
    session.add(new_record)
    session.commit()


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
