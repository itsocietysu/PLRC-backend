import json
import base64

from collections import OrderedDict

from plrc.db import DBConnection

from plrc.MediaResolver.MediaResolverFactory import MediaResolverFactory

class EntityBase:
    host = '.'
    PERMIT_NONE = 0
    PERMIT_ACCESSED = 1
    PERMIT_ADMIN = 2
    PERMIT_OWNER = 2

    json_serialize_items_list = ['']

    MediaCls = None
    MediaPropCls = None

    locales = ['RU', 'EN']

    def to_dict(self, items=[]):
        def fullfill_entity(key, value):
            if key == 'url':
                value = '%s%s' % (EntityBase.host, value[1:])
            return value

        def dictionate_entity(entity):
            try:
                json.dump(entity)
                return entity
            except:
                if 'to_dict' in dir(entity):
                    return entity.to_dict()
                else:
                    return str(entity)

        res = OrderedDict([(key, fullfill_entity(key, dictionate_entity(self.__dict__[key])))
                           for key in (self.json_serialize_items_list if not len(items) else items)])
        return res

    def __init__(self):
        pass

    def add(self):
        with DBConnection() as session:
            session.db.add(self)
            session.db.commit()
            return self.eid

        return None

    @classmethod
    def delete(cls, eid):
        with DBConnection() as session:
            res = session.db.query(cls).filter_by(eid=eid).all()

            if len(res):
                [session.db.delete(_) for _ in res]
                session.db.commit()
            else:
                raise FileNotFoundError('%s was not found' % cls.__name__)

    @classmethod
    def get(cls):
        with DBConnection() as session:
            return session.db.query(cls)

    @classmethod
    def get_ownerid_entity_id(cls, eid, callRaise=False):
        ownerid = None

        res = cls.get().filter_by(eid=eid).all()

        if len(res):
            try:
                ownerid = res[0].ownerid
            except:
                try:
                    ownerid = res[0].userid
                except:
                    if callRaise:
                        raise Exception("%s doesn't contain field 'ownerid'")

        return ownerid

    @classmethod
    def convert_media_value_to_media_item(cls, media_type, _owner_id, _):
        _name = ''
        _desc = ''

        if media_type == 'equipment':
            _name = _['name']
            _desc = _['desc']
            _ = _['media']

        if type(_) is str:
            resolver = MediaResolverFactory.produce(media_type, base64.b64decode(_))
            resolver.Resolve()
            return EntityBase.MediaCls(_owner_id, media_type, resolver.url, name=_name, desc=_desc).add()
        return _

    @classmethod
    def process_media(cls, session, media_type, _owner_id, eid, _id, _, update=False):
        if EntityBase.MediaCls:
            _ = cls.convert_media_value_to_media_item(media_type, _owner_id, _)

            if type(_) is int:
                if not update:
                    EntityBase.MediaPropCls(eid, _id, _).add(session=session, no_commit=True)
                else:
                    EntityBase.MediaPropCls(eid, _id, _).update(session=session, no_commit=True)
            else:
                raise FileNotFoundError("Media has not been created")

