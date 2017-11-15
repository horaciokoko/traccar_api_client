# -*- coding: UTF-8 -*-

import re


def expand_url(url, protocol):
    """
    Expands the given URL to a full URL by adding
    the traccar rest parts

    :param url: URL to be expanded
    :param service: 'rest' 
    """
    
        ws_part = 'api'
    return url.endswith('/') and url + ws_part or url + '/' + ws_part


def camel_2_snake(name):
    "Converts CamelCase to camel_case"
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
