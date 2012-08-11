#!/usr/bin/env python

from ctypes import c_bool, c_float, c_int, c_long, c_void_p, sizeof

from types import (
    BooleanType, DictType, FloatType, IntType, ListType, LongType, NoneType,
    StringTypes
)

ENCODING = 'utf-8'

_typeToSize = {
    BooleanType: sizeof(c_bool),
    FloatType: sizeof(c_float),
    IntType: sizeof(c_int),
    LongType: sizeof(c_long),
    NoneType: sizeof(c_void_p),
}


def summarize(data):
    if isinstance(data, dict):
        summary = {
            'dictValues': [],
            'length': len(data),
            'listValues': [],
            'totalKeysBytes': 0,
            'totalValuesBytes': 0,
            'type': 'dict',
        }
        for key in sorted(data.keys()):
            summary['totalKeysBytes'] += len(key.encode(ENCODING))
            valueType = type(data[key])
            if valueType == DictType:
                sub = summarize(data[key])
                summary['totalValuesBytes'] += sub['totalValuesBytes']
                summary['dictValues'].append(sub)
            elif valueType == ListType:
                sub = summarize(data[key])
                summary['totalValuesBytes'] += sub['totalBytes']
                summary['listValues'].append(sub)

    elif isinstance(data, list):
        summary = {
            'dictValues': [],
            'length': len(data),
            'listValues': [],
            'totalBytes': 0,
            'type': 'list',
        }
        for item in data:
            itemType = type(item)
            if itemType == DictType:
                sub = summarize(item)
                summary['totalBytes'] += (sub['totalValuesBytes'] +
                                          sub['totalKeysBytes'])
                summary['dictValues'].append(sub)
            elif itemType == ListType:
                sub = summarize(item)
                summary['totalBytes'] += sub['totalBytes']
                summary['listValues'].append(sub)
            elif isinstance(item, StringTypes):
                summary['totalBytes'] += len(item.encode(ENCODING))
            else:
                summary['totalBytes'] += _typeToSize[itemType]

    else:
        raise ValueError('Unknown value %r passed to summarize.' % data)
    return summary


if __name__ == '__main__':
    from json import dumps, loads
    import sys

    try:
        j = loads(sys.stdin.read())
    except ValueError, e:
        print >>sys.stderr, 'Could not load JSON object from stdin.'
        sys.exit(1)

    print dumps([summarize(j), j])
