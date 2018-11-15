import datetime
import os
import time

import uuid
import json
import zipfile
import cv2
import numpy as np

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from plrc.Entities.EntityBase import EntityBase
from plrc.db import DBConnection

Base = declarative_base()


class EntityRecognize(EntityBase, Base):
    __tablename__ = 'plrc_recognize'

    pid = Column(Integer, Sequence('plrc_seq'), primary_key=True)
    ownerid = Column(Integer)
    url = Column(String)
    created = Column(Date)

    json_serialize_items_list = ['pid', 'ownerid', 'url', 'created']

    def __init__(self, ownerid, url):
        super().__init__()

        self.ownerid = ownerid
        self.url = url

        ts = time.time()
        self.created = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    @classmethod
    def delete(cls, pid):
        def safe_delete(item):
            if os.path.isfile(item.url):
                os.remove(item.url)
            session.db.delete(item)

        with DBConnection() as session:
            res = session.db.query(cls).filter_by(pid=pid).all()

            if len(res) == 1:
                [safe_delete(_) for _ in res]
                session.db.commit()
            else:
                raise FileNotFoundError('%s was not found' % cls.__name__)

    @classmethod
    def save(cls, owner_id, img, desc):

        pid = None

        if type(img) is np.ndarray:
            _name = uuid.uuid4().hex
            _url = './results/%s.zip' % _name

            with zipfile.ZipFile(_url, 'w') as zipf:
                for i, _ in enumerate(desc):
                    with zipf.open('%d.json' % i, 'w') as jsf:
                        jsf.write(json.dumps(_.to_dict(), indent=2).encode('utf-8'))
                with zipf.open('%s.png' % _name, 'w') as imf:
                    imf.write(cv2.imencode(".png", img)[1])

            pid = EntityRecognize(owner_id, _url).add()

        return pid
