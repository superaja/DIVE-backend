import pandas as pd
import numpy as np

import ujson as json

from flask import current_app

import logging
logger = logging.getLogger(__name__)


class RoundedFloat(float):
    def __repr__(self):
        return '%.3f' % self

def jsonify(args):
    return current_app.response_class(json.dumps(args), mimetype='application/json')

def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + "".join(x.title() for x in components[1:])


def replace_unserializable_numpy(obj):
    if isinstance(obj, dict):
        return dict((k, replace_unserializable_numpy(v)) for k, v in obj.items())
    elif isinstance(obj, np.float32) or isinstance(obj, np.float64):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj.item()
    elif isinstance(obj, float) or isinstance(obj, int):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif isinstance(obj, (np.ndarray, list, tuple)):
        return map(replace_unserializable_numpy, obj)
    elif isinstance(obj,(pd.DataFrame, pd.Series)):
        return replace_unserializable_numpy(obj.to_dict())
    elif obj == None:
        return None
    elif isinstance(obj, str) or isinstance(obj, unicode) or isinstance(obj.keys()[0], unicode):
        return obj.replace('nan', 'null').replace('NaN', 'null')
    return obj


def format_json(obj):
    if isinstance(obj, dict):
        if len(obj.keys()) > 0:
            if isinstance(obj.keys()[0], str) or isinstance(obj.keys()[0], unicode):
                return dict((to_camel_case(k), format_json(v)) for k, v in obj.items())
            elif isinstance(obj.keys()[0], tuple):
                return dict((str(k), format_json(v)) for k, v in obj.items())
    if isinstance(obj, np.float32) or isinstance(obj, np.float64):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj.item()
    elif isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif isinstance(obj, (np.ndarray, list)):
        return map(format_json, obj)
    elif isinstance(obj, tuple):
        return tuple(map(format_json, obj))
    elif isinstance(obj,(pd.DataFrame, pd.Series)):
        return format_json(obj.to_dict())
    elif isinstance(obj, str):
        return obj.replace('nan', 'null').replace('NaN', 'null')
    return obj
