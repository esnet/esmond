#!/usr/bin/env python

"""
Small example/test script to post some data to locally running rest 
interface (django runserver) and cassandra instance.
"""

import json
import os
import requests
import sys
import time

from esmond.api.client.timeseries import PostRawData, PostBaseRate, GetRawData, GetBaseRate
from esmond.util import atencode

def read_insert(ts, p_type, path):
    params = {
        'begin': ts-90000, 'end': ts+1000
    }

    get = None

    args = {
        'api_url': 'http://localhost:8000/', 
        'path': path, 
        'freq': 30000,
        'params': params,
    }

    if p_type == 'RawData':
        get = GetRawData(**args)
    elif p_type == 'BaseRate':
        get = GetBaseRate(**args)

    payload = get.get_data()

    print payload
    for d in payload.data:
        print '  *', d

def main():

    ts = int(time.time()) * 1000

    payload = [
        { 'ts': ts-90000, 'val': 1000 },
        { 'ts': ts-60000, 'val': 2000 },
        { 'ts': ts-30000, 'val': 3000 },
        { 'ts': ts, 'val': 4000 },
    ]

    path = ['rtr_test_post', 'FastPollHC', 'ifHCInOctets', 'interface_test/0/0.0']

    p = PostRawData(api_url='http://localhost:8000/', path=path, freq=30000)
    # set_payload will completely replace the internal payload of the object.
    p.set_payload(payload)
    # add_to_payload will just add new items to internal payload.
    p.add_to_payload({'ts': ts+1000, 'val': 5000})
    # send the request and clear the internal payload list.
    p.send_data()
    # Second call will generate a warning since the first will
    # clear the internal payload.
    p.send_data()

    read_insert(ts, 'RawData', path)

    # return

    p = PostBaseRate(api_url='http://localhost:8000/', path=path, freq=30000)
    p.set_payload(payload)
    p.send_data()

    read_insert(ts, 'BaseRate', path)



if __name__ == '__main__':
    main()