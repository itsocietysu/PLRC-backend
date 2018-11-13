import concurrent.futures as ftr
import json
import logging
import mimetypes
import os
import posixpath
import re
import time

import tensorflow as tf
import cv2
import numpy as np
import math
from urllib.parse import parse_qs
from collections import OrderedDict

from plrc_project.Utils.label_map_reader import *
from plrc_project.run import run

import falcon
from falcon_multipart.middleware import MultipartMiddleware

from plrc import utils
from plrc.db import DBConnection
from plrc.serve_swagger import SpecServer
from plrc.utils import obj_to_json, getIntPathParam, getQueryParam, admin_access_type_required

from plrc.Entities.EntityBase import EntityBase
from plrc.Entities.EntityRecognize import EntityRecognize
from plrc.Entities.EntityUser import EntityUser

from plrc.auth import auth


def guess_response_type(path):
    if not mimetypes.inited:
        mimetypes.init()  # try to read system mime.types

    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',  # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
    })

    base, ext = posixpath.splitext(path)
    if ext in extensions_map:
        return extensions_map[ext]
    ext = ext.lower()
    if ext in extensions_map:
        return extensions_map[ext]
    else:
        return extensions_map['']


def date_time_string(timestamp=None):
    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    if timestamp is None:
        timestamp = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
        weekdayname[wd],
        day, monthname[month], year,
        hh, mm, ss)
    return s


def httpDefault(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    path = req.path
    src_path = path
    path = path.replace(baseURL, '.')

    if os.path.isdir(path):
        for index in "index.html", "index.htm", "test-search.html":
            index = os.path.join(path + '/', index)
            if os.path.exists(index):
                path = index
                break
        else:
            return None

    if path.endswith('swagger.json'):
        path = path.replace('swagger.json', 'swagger_temp.json')

    ctype = guess_response_type(path)

    try:
        with open(path, 'rb') as f:
            resp.status = falcon.HTTP_200

            fs = os.fstat(f.fileno())
            length = fs[6]

            buffer = f.read()
            if path.endswith('index.html'):
                str = buffer.decode()
                str = str.replace('127.0.0.1:4201', server_host)
                buffer = str.encode()
                length = len(buffer)

    except IOError:
        resp.status = falcon.HTTP_404
        return

    resp.set_header("Content-type", ctype)
    resp.set_header("Content-Length", length)
    resp.set_header("Last-Modified", date_time_string(fs.st_mtime))
    resp.set_header("Access-Control-Allow-Origin", "*")
    resp.set_header("Path", path)
    resp.body = buffer


def load_graph(graph_location):
    with tf.gfile.GFile(graph_location, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name='')
    return graph


def getVersion(**request_handler_args):
    resp = request_handler_args['resp']
    resp.status = falcon.HTTP_200
    with open("VERSION") as f:
        resp.body = obj_to_json({"version": f.read()[0:-1]})


def restart(**request_handler_args):
    resp = request_handler_args['resp']

    global graph, labels
    graph = load_graph('./graph/frozen_inference_graph.pb')
    labels = label_map_to_dict(load_label_map_file('./graph/label_map.pbtxt'))

    resp.body = obj_to_json({"result": "success"})
    resp.status = falcon.HTTP_200


# User feature set functions
# ---------------------------


@admin_access_type_required
def addUser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        params['access_token'] = req.context['access_token']
        id, status_code, error = EntityUser.add_from_json(params)

        if id:
            objects = EntityUser.get().filter_by(pid=id).all()

            res = []
            for _ in objects:
                obj_dict = _.to_dict(['pid', 'email', 'access_type'])
                res.append(obj_dict)

            resp.body = obj_to_json(res)
            resp.status = falcon.HTTP_200
            return
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    resp.body = obj_to_json({'error': error})
    resp.status = status_code


@admin_access_type_required
def deleteUser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("userId", **request_handler_args)

    if id is not None:
        res = []
        try:
            EntityUser.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        objects = EntityUser.get().filter_by(pid=id).all()
        if not len(objects):
            resp.body = obj_to_json(res)
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


# End of user feature set functions
# ----------------------------------


# Positioning feature set functions
# ----------------------------------


def recognize(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    image = getQueryParam('image', **request_handler_args)
    content_type = image.headers._headers[1][1]
    if image is not None and re.match("image", content_type):

        _bytes = image.file.read()
        _img = cv2.imdecode(np.fromstring(_bytes, np.uint8), cv2.IMREAD_COLOR)

        desc = run(_img, graph)

        pid = EntityRecognize.save(1, _img, desc)

        resp.body = obj_to_json({"result": "success"})
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_400


def layout(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    resp.body = obj_to_json({"result": "success"})
    resp.status = falcon.HTTP_200


# End of positioning feature set functions
# -----------------------------------------

operation_handlers = {
    # User
    'addUser':              [addUser],
    'deleteUser':           [deleteUser],

    # Positioning
    'recognize':            [recognize],
    'layout':               [layout],

    'getVersion':           [getVersion],
    'restart':              [restart],
    'httpDefault':          [httpDefault]
}

class CORS(object):
    def process_response(self, req, resp, resource):
        origin = req.get_header('Origin')
        if origin:
            resp.set_header('Access-Control-Allow-Origin', origin)
            resp.set_header('Access-Control-Max-Age', '100')
            resp.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, PUT, DELETE')
            resp.set_header('Access-Control-Allow-Credentials', 'true')

            acrh = req.get_header('Access-Control-Request-Headers')
            if acrh:
                resp.set_header('Access-Control-Allow-Headers', acrh)

            # if req.method == 'OPTIONS':
            #    resp.set_header('Access-Control-Max-Age', '100')
            #    resp.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, PUT, DELETE')
            #    acrh = req.get_header('Access-Control-Request-Headers')
            #    if acrh:
            #        resp.set_header('Access-Control-Allow-Headers', acrh)


class Auth(object):
    def process_request(self, req, resp):
        #TODO: SWITCH ON
        #req.context['email'] = 'serbudnik@gmail.com'
        #return
        # skip authentication for version, UI and Swagger
        if re.match('(/plrc/version|'
                     '/plrc/settings/urls|'
                     '/plrc/images|'
                     '/plrc/ui|'
                     '/plrc/swagger\.json|'
                     '/plrc/swagger-temp\.json|'
                     '/plrc/swagger-ui).*', req.relative_uri):
            return

        if req.method == 'OPTIONS':
            return # pre-flight requests don't require authentication

        token = None
        try:
            if req.auth:
                token = req.auth.split(" ")[1].strip()
            else:
                raise falcon.HTTPUnauthorized(description='Token was not provided in schema [bearer <Token>]',
                                              challenges=['Bearer realm=http://GOOOOGLE'])
        except:
            raise falcon.HTTPUnauthorized(description='Token was not provided in schema [bearer <Token>]',
                                          challenges=['Bearer realm=http://GOOOOGLE'])

        error = 'Authorization required.'
        if token:
            error, acc_type, user_email, user_id, user_name = auth.Validate(
                cfg['oidc']['each_oauth2']['check_token_url'],
                token
            )


            if not error:
                req.context['user_email'] = user_email
                req.context['user_id'] = user_id
                req.context['user_name'] = user_name
                req.context['access_type'] = acc_type

                if EntityUser.check_user(user_email):
                    return # passed access token is valid
                else:
                    raise falcon.HTTPLocked(description='User is not granted access.', challenges=['Bearer realm=http://GOOOOGLE'])

        raise falcon.HTTPUnauthorized(description=error,
                                      challenges=['Bearer realm=http://GOOOOGLE'])


logging.getLogger().setLevel(logging.DEBUG)
args = utils.RegisterLaunchArguments()

cfgPath = args.cfgpath
profile = args.profile

# configure
with open(cfgPath) as f:
    cfg = utils.GetAuthProfile(json.load(f), profile, args)
    DBConnection.configure(**cfg['each_db'])
    if 'oidc' in cfg:
        cfg_oidc = cfg['oidc']

general_executor = ftr.ThreadPoolExecutor(max_workers=20)

# change line to enable OAuth autorization:
#wsgi_app = api = falcon.API(middleware=[CORS(), Auth(), MultipartMiddleware()])
wsgi_app = api = falcon.API(middleware=[CORS(), MultipartMiddleware()])

server = SpecServer(operation_handlers=operation_handlers)

if 'server_host' in cfg:
    with open('swagger.json') as f:
        swagger_json = json.loads(f.read(), object_pairs_hook=OrderedDict)

    server_host = cfg['server_host']
    swagger_json['host'] = server_host

    baseURL = '/plrc'
    if 'basePath' in swagger_json:
        baseURL = swagger_json['basePath']

    EntityBase.host = server_host + baseURL

    json_string = json.dumps(swagger_json)

    with open('swagger_temp.json', 'wt') as f:
        f.write(json_string)

with open('swagger_temp.json') as f:
    server.load_spec_swagger(f.read())

graph = load_graph('./graph/frozen_inference_graph.pb')
labels = label_map_to_dict(load_label_map_file('./graph/label_map.pbtxt'))

api.add_sink(server, r'/')
