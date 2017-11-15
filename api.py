# -*- coding: utf-8 -*-
'''
    magento.api

    Generic API for magento

    :license: BSD, see LICENSE for more details
'''
import sys
import base64
from threading import RLock

PROTOCOLS = []

import rest
try:
    import requests
    import json
except ImportError:
    pass
else:
    PROTOCOLS.append('rest')

from traccarApi.utils import expand_url, camel_2_snake


class ClientApiMeta(type):
    """
    A Metaclass that automatically injects objects that inherit from API
    as properties.
    """
    def __new__(meta, name, bases, dct):
        abstract = dct.get('__abstract__', False)
        Klass = super(ClientApiMeta, meta).__new__(meta, name, bases, dct)

        if not abstract:
            setattr(
                API, camel_2_snake(name),
                property(lambda self: self.get_instance_of(Klass))
            )

        return Klass


class API(object):
    """
    Generic API to connect to Traccar
    """
    __metaclass__ = ClientApiMeta
    __abstract__ = True

    def __init__(self, url, username, password,
                 version='1.3.2.4', full_url=False,
                 protocol='rest', transport=None,
                 verify_ssl=True):
       
        assert protocol \
            in PROTOCOLS, "protocol must be %s" % ' OR '.join(PROTOCOLS)
        self.url = str(full_url and url or expand_url(url, protocol))
        self.username = username
        self.password = password
        self.protocol = protocol
        self.version = version
        self.transport = transport
        self.session = None
        self.client = None
        self.verify_ssl = verify_ssl
        self.lock = RLock()

    def connect(self):
        """
        Connects to the service
        but does not login. This could be used as a connection test
        """
        if self.protocol == 'rest':
            # Use an authentication token as the password
            chaine='{0}:{1}'.format(self.username, self.password,'utf-8')
            print(chaine)
            token=base64.b64encode(chaine)
            print(token)
            self.client = rest.Client(self.url, token,
                                      verify_ssl=self.verify_ssl)
        else:
            self.client = Client(self.url)

    def __enter__(self):
        """
        Entry point for with statement
        Logs in and creates a session
        """
        if self.client is None:
            self.connect()
        if self.protocol == 'rest':
            self.session = True
        else:
            self.session = self.client.service.login(
                self.username, self.password)
        return self

    def __exit__(self, type, value, traceback):
        """
        Exit point

        Closes session with traccar
        """
        self.session = None

    def call(self, resource_path, arguments):
        if self.protocol == 'rest':
            return self.client.call(resource_path, arguments)
        else:
            return self.client.service.call(
                self.session, resource_path, arguments)

    def multiCall(self, calls):
        """
        Proxy for multicalls
        """
        return self.client.service.multiCall(self.session, calls)

    _missing = []

    def get_instance_of(self, Klass):
        """
        Return an instance of the client API with the same auth credentials
        that the API server was instanciated with. The created instance is
        cached, so subsequent requests get an already existing instance.

        :param Klass: The klass for which the instance has to be created.
        """
        with self.lock:
            value = self.__dict__.get(Klass.__name__, self._missing)
            if value is self._missing:
                value = Klass(
                    self.url,
                    self.username,
                    self.password,
                    self.version,
                    True,
                    self.protocol,
                )
                self.__dict__[Klass.__name__] = value.__enter__()
            return value
