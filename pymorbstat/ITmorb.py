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

#%% Set the environment

import os, sys, io
import warnings

from collections import OrderedDict, Mapping, Sequence#analysis:ignore
from six import string_types
from copy import deepcopy

from datetime import datetime, timedelta
import calendar

__TEST_STANDALONE = False 
__TEST_PYEUDATNAT = not(__TEST_STANDALONE)

try:
    import numpy as np
    import pandas as pd
except:
    raise IOError("Impossible to handle dataframe not available: abort...")

try:
    import matplotlib 
    import matplotlib.pyplot as mplt
    import matplotlib.dates as mdates
except:
    raise IOError("Impossible to draw plots: abort...")
 
try:                          
    import simplejson as json
except ImportError:
    try:                          
        import json
    except ImportError:
        class json:
            def dump(arg):  
                return '%s' % arg
            def load(arg):  
                with open(arg,'r') as f:
                    return f.read()
      
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
    pass
    # obsolete...
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
                self.meta = deepcopy(metadata)
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
    pass
except AssertionError:
    from pyeudatnat.misc import Type, Datetime

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

#%% Get essential metadata

try:
    METAFILEITMORB = __file__.split('.')[0]
except:
    METAFILEITMORB = 'ITmorb'
finally:
    METAFILEITMORB = '%s.json' % METAFILEITMORB 

try:
    assert os.path.exists(METAFILEITMORB)
    with open(METAFILEITMORB,"r") as f:
        METAITMORB = json.load(f)
except:
    __type2name     = lambda t: t.__name__  # lambda t: {v:k for (k,v) in BASETYPE.items()}[t]    
    METAITMORB      =  { "country":     {'code': 'IT', 'name': 'Italia'},
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
                            ]),
                    "nan": 9999
                    }
    with open(METAFILEITMORB,"w") as f:
        json.dump(METAITMORB, f)


#%% Set dataset from metadata

# dIT = load_source(ITMETAMORB)
MorbDatIT = datnatFactory(country = "IT")
dIT = MorbDatIT(METAITMORB)

# some fields of interest 
T_20 = dIT.meta.get('index')['T_20']['name']
NAN = dIT.meta.get('nan')
GE = dIT.meta.get('index')['GE']['name']
fmt = dIT.meta.get('file','.').split('.')[1]
enc = dIT.meta.get('enc',None) 
sep =  dIT.meta.get('sep',None) 
dtype = {v['name']: Type.upytname2npt(v['type']) for v in dIT.meta.get('index',{}).values()}

Yref = 2000  # a leap year for sure


#%% Load, format and clean dataset

try:
    # dateparse = lambda x: datetime.strptime('%s%s' % (x,Yref), '%m%d%Y')
    dIT.load_data(fmt = fmt, encoding = enc, sep = sep, dtype = dtype,
                  # parse_dates=[GE], date_parser=dateparse,
                  )
except:
    dIT.load_data()
    dIT.data  = dIT.data.astype(dtype)
finally:
    print ('Data extracted on %s' % Datetime.datetime(Datetime.TODAY(), fmt='%d/%m/%Y'))
    data = dIT.data     

print('Fields of the data: %s' % list(data.columns))  
print('#Records: %s - #Fields: %s' % data.shape)
data.head(5)

try:
    data.drop(data.loc[data[T_20]==NAN].index, inplace=True)
    print('#Cleaned records: %s - #Fields: %s' % data.shape)
except:
    pass
      
#%% Retrieve basic temporal and geographical information
years = [int("20%s" % tot.split('_')[1]) for tot in data.columns if tot.startswith("TOTALE_")]
ystart, yend =  min(years), max(years)
print('Data collections considered: [%s, %s]' % (ystart, yend))

# retrieve list of comu9ne
ICOMUNE = dIT.meta.get('index')['COMUNE']['name']
comuni = data[ICOMUNE].unique()
print('#Comuni: %s' % len(comuni))

#%% Retrieve temporal series

data[GE].head(5)
dstart, dend = data[GE].min(), data[GE].max()

def fmt_mth(ge):
    return '%s/%s' % (ge[2:], ge[:2])
print('Period of data collection considered: [%s, %s]' % (fmt_mth(dstart), fmt_mth(dend)))

def get_date(ge, year):
    d = {'y':year, 'm':int(ge[:2]), 'd':int(ge[2:])}
    return Datetime.datetime(d, fmt='datetime')

def len_series(ystart, yend, dstart, dend):
    # get the lenght of the datasets. This will depend on the occurrence of a 29/02
    # (leap year) in the period consider
    # number of leap years in the range from startyear to curyear
    nleap = calendar.leapdays(ystart, yend+1)
    if nleap > 0:   yref = yend # any year
    else:           yref = Yref 
    td = Datetime.span(since=get_date(dstart,yref), until=get_date(dend,yref)) # until - since
    # lenght of the series in days
    return td.days

ndays = len_series(ystart, yend, dstart, dend)
print('Max lenght of the time series, i.e. number of days (max) covered by the' 
      ' data collection: %s' % ndays)

#%%

# the following assumes all dates are informed
def pos_leap(dstart):
    leapday = Datetime.datetime({'y':Yref, 'm':2, 'd':29}, fmt='datetime')
    td = Datetime.span(since=get_date(dstart,Yref), until=leapday)
    # position of the 29/02 in the series
    return td.days

ileapday = pos_leap(dstart)
print('Time series will be padded in position %s' % ileapday)
# note: indexing starts at 0

def insert_leapday(s, pos):  # not used...
    # slice the upper and lower halves of the dataframe 
    s1, s2 = s[0:pos], s[pos:]    
    # insert the leap values in the upper half dataframe 
    if pos>0:   s1.loc[pos] = s1[pos-1] 
    else:       s1.loc[pos] = s2[0] 
    # concat the two series 
    snew = pd.concat([s1, s2]) 
    # reassign the index labels 
    snew.index = [*range(snew.shape[0])] 
    # return the updated dataframe 
    return snew  

def pad_leapday(s, pos): 
    try:
        s[pos] = s[pos-1]
    except:
        s[pos] = np.nan # NAN

dailydeaths = pd.DataFrame()
for y in years:
    col = dIT.meta.get('index')['T_%s' % str(y)[2:]]['name']
    dailydeaths[y] = data.groupby(GE)[col].agg('sum')
    if not calendar.isleap(y):
        # pad_leapday(dailydeaths[y], ileapday)
        yloc = dailydeaths.columns.get_loc(y)
        dailydeaths.iloc[ileapday,yloc] = dailydeaths.iloc[ileapday-1,yloc]
    
cumdailydeaths = dailydeaths.cumsum(axis = 0, skipna =True) # default


#idx = pd.MultiIndex.from_arrays([
#        pd.to_datetime(data[GE].strftime('%m%d%Y' % Yref)),
#        pd.Index(range(ystart,yend+1))
#    ])

##### datetime.strptime('%s%s' % (x,Yref), '%m%d%Y')

ddstart, ddend = get_date(dstart, y), get_date(dend, y)

idx_rng = pd.date_range(start=ddstart, end=ddend, freq=timedelta(1))
# mdates.drange(ddstart, ddend, timedelta(1))
dailydeaths.set_index(idx_rng, inplace=True)
cumdailydeaths.set_index(idx_rng, inplace=True)

#%%

# years = list(dailydeaths.columns)

locator, formatter = mdates.DayLocator(bymonthday=[1,15]), mdates.DateFormatter('%d/%m')

fig, ax = mplt.subplots()
ax.plot(dailydeaths)
ax.set_ylabel('Daily death counts')
#ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter);
ax.set_title('Date')
ax.legend(years);

fig, ax = mplt.subplots()
ax.plot(cumdailydeaths)
ax.set_ylabel('Daily cumulative death counts')
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter);
ax.set_title('Date')
ax.legend(years);

weeklydeaths = dailydeaths.resample('W').mean()
fig, ax = mplt.subplots()
#ax.bar(dailydeaths.index.values, dailydeaths.loc[ddstart:ddend, 2020],
#       color='purple', label='daily')
ax.plot(dailydeaths.loc[ddstart:ddend, 2020], 
        marker='.', linestyle='-', linewidth=0.5, label='daily')
ax.plot(weeklydeaths.loc[ddstart:ddend, 2020],
        marker='o', markersize=8, linestyle='-', label='weekly mean')
ax.set_ylabel('Death counts')
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter);
ax.legend();


#%% 

def run():
    pass    
def __main__():
    run()
