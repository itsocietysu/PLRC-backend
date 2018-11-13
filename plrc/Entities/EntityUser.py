import datetime
import time

import falcon
import requests

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from plrc.Entities.EntityBase import EntityBase

from plrc.utils import isAllInData

from plrc.db import DBConnection

Base = declarative_base()


class EntityUser(EntityBase, Base):
    __tablename__ = 'plrc_user'

    pid = Column(Integer, Sequence('plrc_seq'), primary_key=True)
    email = Column(String)
    access_type = Column(String)
    created = Column(Date)
    updated = Column(Date)

    json_serialize_items_list = ['pid', 'email', 'access_type', 'created', 'updated']

    def __init__(self, email=None, access_type='user'):
        super().__init__()

        self.email = email
        self.access_type = access_type

        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    @classmethod
    def add_from_json(cls, data):

        pid = None

        if isAllInData(['email', 'access_token'], data):
            email = data['email']
            access_token = data['access_token']
            req_url = 'http://each.itsociety.su:5000/oauth2/emailinfo?access_token=%s&email=%s' % (access_token, email)
            resp = requests.get(req_url)
            data = resp.json()
            if resp.status_code == 200:
                new_entity = EntityUser(email, data['access_type'])
                eid = new_entity.add()
                return eid, falcon.HTTP_200, None
            return pid, falcon.__dict__['HTTP_%s' % resp.status_code], data.error

        return pid, falcon.HTTP_400, 'Invalid parameters supplied'

    @classmethod
    def check_user(cls, email):

        with DBConnection() as session:
            users = session.db.query(EntityUser).filter_by(email=email).all()
            if len(users):
                return True
        return False
