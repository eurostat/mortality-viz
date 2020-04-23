#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _ITmorb

.. Links

.. _A: http://A
.. |A| replace:: `A <A_>`_

Metadata of IT data on morbidity.
    
**Dependencies**

*require*:      :mod:`os`, :mod:`sys`

*optional*:     :mod:`A`

*call*:         :mod:`A`         

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Fri Apr 17 00:07:57 2020

#%% 

import os, sys, io
import warnings

from collections import OrderedDict, Mapping, Sequence#analysis:ignore
from six import string_types
from copy import deepcopy

from datetime import datetime

__TEST_STANDALONE = False # True
__TEST_PYEUDATNAT = not(__TEST_STANDALONE)

try:
    import numpy as np
    import pandas as pd
except:
    raise IOError("Impossible to handle dataframe not available: abort...")
       
try:
    import pyeudatnat
except ImportError:
    try: 
        assert __TEST_PYEUDATNAT is False
    except AssertionError:
        warnings.warn("Package pyeudatnat not imported - testing not available")
    __is_pyeudatnat_installed = False 
else:
    __is_pyeudatnat_installed = True and not __TEST_STANDALONE
    
try:
    assert __is_pyeudatnat_installed is False
    import requests
    import zipfile
    def load_source(metadata):
        source, file = metadata.get('source',''), metadata.get('file','')
        enc, sep = metadata.get('enc','utf-8'), metadata.get('sep',',')
        warnings.warn('Input source file: %s - data file: %s' % (source,file))
        if any([source.startswith(p) for p in ['http', 'https', 'ftp']]):
            try:
                response = requests.get(source)
                response.raise_for_status()
            except (requests.URLRequired,requests.HTTPError,requests.RequestException):
                raise IOError("NO source file found online... abort!")
            else:
                # warnings.warn("Source file found online... proceed")
                data = io.BytesIO(response.content)
        elif os.path.exists(source):
            # warnings.warn("Source file found on the disk... proceed")
            data = source
        else:
            raise IOError("NO input source file found on the disk... abort!")             
        if file is None:
            nfile = data
        if any([source.endswith(z) for z in ('zip','gzip','gz')]):
            try:
                assert zipfile.is_zipfile(data)
            except:
                raise IOError("Wrongly formatted input source file... abort!")
            with zipfile.ZipFile(data) as zf:
                namelist = zf.namelist()
                try:
                    assert file in namelist
                except:
                    try:
                        _namelist = [os.path.basename(n) for n in namelist]
                        assert file in _namelist
                    except:
                        raise IOError("Data not found in source file... abort!")
                    else:
                        nfile = namelist[_namelist.index(file)]
                else:
                    nfile = file
                try:
                    # data = zf.read(file)
                    with zf.open(nfile) as zd:
                        data = pd.read_csv(zd, encoding=enc, sep=sep)        
                except:
                    raise IOError("Data %s cannot be read in source file... abort!" % nfile)
                else:
                    pass#warnings.warn("Data %s read in source file" % file)
        class MorbDatIT(object):
            def __init__(self,data):
                self.data = data
        return MorbDatIT(data)
except AssertionError:
    from pyeudatnat.base import datnatFactory
    def load_source(metadata):
        MorbDatIT = datnatFactory(country = "IT")
        morbdatIT = MorbDatIT(metadata)
        morbdatIT.load_data()
        return morbdatIT
except ImportError:
    warnings.warn("\n! Impossible to download online data - ensure data are available on-disk and unzipped")
    def load_source(metadata):
        pass

try:
    assert __is_pyeudatnat_installed is False
    import geopy
except AssertionError:
    def geocode(data):
        pass
except ImportError:
    warnings.warn("\n! No geolocalisation available")
else:
    # from pyeudatnat.geo import GeoService
    def geocode(data):
        return data.geoserv.geocode(data.data)

#%% 

__type2name     = lambda t: t.__name__  # lambda t: {v:k for (k,v) in BASETYPE.items()}[t]    

METAMORBIT      =  { "country":     {'code': 'IT', 'name': 'Italia'},
                     "lang":        {'code': 'it', 'name': 'italian'}, 
                     "file":        'comune_giorno.csv',
                     "source":      'https://www.istat.it/it/files/2020/03/comune-giorno.zip',
                     "enc":         "latin1",
                     "sep":         ',', 
                     "date":        None, #'%d-%m-%Y %H:%M',
                     "index":     OrderedDict( [ 
                        ("REG",       {"name": "REG",                     "desc": "Codice Istat della Regione di residenza.",
                                      "type": __type2name(int),         "values": None}),
                        ("PROV",     {"name": "PROV",          "desc": "Codice Istat della Provincia di residenza.",   
                                      "type": __type2name(int),         "values": None}),
                        ("REGIONE",     {"name": "NOME_REGIONE",          "desc": "Regione di residenza.",   
                                      "type": __type2name(str),         "values": None}),
                        ("PROVINCIA",     {"name": "NOME_PROVINCIA",          "desc": "Provincia di residenza.",   
                                      "type": __type2name(str),         "values": None}),
                        ("COMUNE",     {"name": "NOME_COMUNE",          "desc": "Comune di residenza.",   
                                      "type": __type2name(str),         "values": None}),
                        ("PROVCOM",     {"name": "COD_PROVCOM",          "desc": "Comune di residenza (classificazione Istat al 01/01/2020)",   
                                      "type": __type2name(str),         "values": None}),
                        ("ETA",     {"name": "CL_ETA",          "desc": "Classe di età in anni compiuti al momento del decesso",   
                                      "type": __type2name(int),         "values": {0: "0", 1: "1-4", 2: "5-9", 3:"10-14", 4:"15-19", 5:"20-24", 6:"25-29", 7:"30-34", 8:"35-39", 9:"40-44", 10:"45-49", 11:"50-54", 12:"55-59", 13:"60-64", 14:"65-69", 15:"70-74", 16:"75-79", 17:"80-84", 18:"85-89", 19:"90-94", 20:"95-99",21:"100+"}}),
                        ("GE",       {"name": "GE",                     "desc": "Giorno di decesso (formato variabile: MeseMeseGiornoGiorno).",
                                      "type": __type2name(str),         "values": None}),
                        ("M_15",       {"name": "MASCHI_15",                     "desc": "numero di decessi maschili nel 2015.",
                                      "type": __type2name(int),         "values": None}),
                        ("M_16",       {"name": "MASCHI_16",                     "desc": "numero di decessi maschili nel 2016.",
                                      "type": __type2name(int),         "values": None}),
                        ("M_17",       {"name": "MASCHI_17",                     "desc": "numero di decessi maschili nel 2017.",
                                      "type": __type2name(int),         "values": None}),
                        ("M_18",       {"name": "MASCHI_18",                     "desc": "numero di decessi maschili nel 2018.",
                                      "type": __type2name(int),         "values": None}),
                        ("M_19",       {"name": "MASCHI_19",                     "desc": "numero di decessi maschili nel 2019.",
                                      "type": __type2name(int),         "values": None}),
                        ("M_20",       {"name": "MASCHI_20",                     "desc": "numero di decessi maschili nel 2020.",
                                      "type": __type2name(int),         "values": None}),
                        ("F_15",       {"name": "FEMMINE_15",                     "desc": "numero di decessi femminili nel 2015.",
                                      "type": __type2name(int),         "values": None}),
                        ("F_16",       {"name": "FEMMINE_16",                     "desc": "numero di decessi femminili nel 2016.",
                                      "type": __type2name(int),         "values": None}),
                        ("F_17",       {"name": "FEMMINE_17",                     "desc": "numero di decessi femminili nel 2017.",
                                      "type": __type2name(int),         "values": None}),
                        ("F_18",       {"name": "FEMMINE_18",                     "desc": "numero di decessi femminili nel 2018.",
                                      "type": __type2name(int),         "values": None}),
                        ("F_19",       {"name": "FEMMINE_19",                     "desc": "numero di decessi femminili nel 2019.",
                                      "type": __type2name(int),         "values": None}),
                        ("F_20",       {"name": "FEMMINE_20",                     "desc": "numero di decessi femminili nel 2020.",
                                      "type": __type2name(int),         "values": None}),
                        ("T_15",       {"name": "TOTALE_15",                     "desc": "numero di decessi totali nel 2015.",
                                      "type": __type2name(int),         "values": None}),
                        ("T_16",       {"name": "TOTALE_16",                     "desc": "numero di decessi totali nel 2016.",
                                      "type": __type2name(int),         "values": None}),
                        ("T_17",       {"name": "TOTALE_17",                     "desc": "numero di decessi totali nel 2017.",
                                      "type": __type2name(int),         "values": None}),
                        ("T_18",       {"name": "TOTALE_18",                     "desc": "numero di decessi totali nel 2018.",
                                      "type": __type2name(int),         "values": None}),
                        ("T_19",       {"name": "TOTALE_19",                     "desc": "numero di decessi totali nel 2019.",
                                      "type": __type2name(int),         "values": None}),
                        ("T_20",       {"name": "TOTALE_20",                     "desc": "numero di decessi totali nel 2020.",
                                      "type": __type2name(int),         "values": None})
                        ])
}


#%% 
                        
morbIT = load_source(METAMORBIT)                        

