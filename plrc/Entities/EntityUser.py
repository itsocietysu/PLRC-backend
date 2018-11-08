import datetime
import time

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from plrc.Entities.EntityBase import EntityBase

from plrc.db import DBConnection

Base = declarative_base()


class EntityUser(EntityBase, Base):
    __tablename__ = 'each_user'

    eid = Column(Integer, Sequence('each_seq'), primary_key=True)
    type = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String, primary_key=True)
    image = Column(String)
    access_type = Column(String)
    created = Column(Date)
    updated = Column(Date)

    json_serialize_items_list = ['eid', 'type', 'name', 'email', 'image',
                                 'access_type', 'created', 'updated']
    required_fields = ['name', 'email', 'image', 'access_type']

    def __init__(self, type='each', name='user', email=None, image=None, access_type='user'):
        super().__init__()

        self.type = type
        self.name = name
        self.email = email
        self.image = image
        self.access_type = access_type

        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    @classmethod
    def update_user(cls, eid, data):

        with DBConnection() as session:
            entity = session.db.query(EntityUser).filter_by(eid=eid).first()
            if entity:
                for _ in cls.required_fields:
                    if _ in data:
                        setattr(entity, _, data[_])

                ts = time.time()
                entity.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
                session.db.commit()
