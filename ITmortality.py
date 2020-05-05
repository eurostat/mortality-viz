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

#%% Setttings

import os, io
from os import path as osp
import warnings

from collections import OrderedDict#analysis:ignore
from copy import deepcopy

import time
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
    import matplotlib.pyplot as mplt
    import matplotlib.dates as mdates
    from matplotlib.ticker import FuncFormatter, MaxNLocator
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
        class MortDatIT(object):
            def __init__(self,data):
                self.meta = deepcopy(metadata)
                self.data = data
        return MorbDatIT(data)
except AssertionError:
    from pyeudatnat.base import datnatFactory
    from pyeudatnat.misc import Structure
    from pyeudatnat.misc import Type, Datetime
    def load_source(metadata):
        MorbDatIT = datnatFactory(country = "IT")
        morbdatIT = MorbDatIT(metadata)
        morbdatIT.load_data()
        return morbdatIT
except ImportError:
    warnings.warn("\n! Impossible to download online data - ensure data are available on-disk and unzipped")
    def load_source(metadata):
        pass

#%% Get metadata

METAFILEITMORT  = 'ITmetadata.json'
METAFILEITGEO   = 'ITmetageo.json'

__THISFILE      = __file__
__THISDIR       = osp.dirname(__THISFILE)

__type2name     = lambda t: t.__name__  # lambda t: {v:k for (k,v) in BASETYPE.items()}[t]    

try:
    METAFILEITMORT = osp.join(__THISDIR, METAFILEITMORT)
    assert os.path.exists(METAFILEITMORT)
    with open(METAFILEITMORT,"r") as f:
        METAITMORT = json.load(f)
except:
    METAITMORT      =  { "country":     {'code': 'IT', 'name': 'Italia'},
                         "lang":        {'code': 'it', 'name': 'italian'}, 
                         "file":        'comune_giorno.csv',
                         "fmt":         'csv',
                         "source":      'https://www.istat.it/it/files/2020/03/comune-giorno.zip',
                         "enc":         "latin1",
                         "sep":         ',', 
                         "datefmt":     '%m%d', # see GE variable
                         "index":     OrderedDict( [ 
                            ("reg_code",       {"name": "REG",                     "desc": "Codice Istat della Regione di residenza.",
                                          "type": __type2name(int),         "values": None}),
                            ("prov_code",     {"name": "PROV",          "desc": "Codice Istat della Provincia di residenza.",   
                                          "type": __type2name(int),         "values": None}),
                            ("region",     {"name": "NOME_REGIONE",          "desc": "Regione di residenza.",   
                                          "type": __type2name(str),         "values": None}),
                            ("province",     {"name": "NOME_PROVINCIA",          "desc": "Provincia di residenza.",   
                                          "type": __type2name(str),         "values": None}),
                            ("city",     {"name": "NOME_COMUNE",          "desc": "Comune di residenza.",   
                                          "type": __type2name(str),         "values": None}),
                            ("city_code",     {"name": "COD_PROVCOM",          "desc": "Comune di residenza (classificazione Istat al 01/01/2020)",   
                                          "type": __type2name(str),         "values": None}),
                            ("age",     {"name": "CL_ETA",          "desc": "Classe di età in anni compiuti al momento del decesso",   
                                          "type": __type2name(int),         "values": {0: "0", 1: "1-4", 2: "5-9", 3:"10-14", 4:"15-19", 5:"20-24", 6:"25-29", 7:"30-34", 8:"35-39", 9:"40-44", 10:"45-49", 11:"50-54", 12:"55-59", 13:"60-64", 14:"65-69", 15:"70-74", 16:"75-79", 17:"80-84", 18:"85-89", 19:"90-94", 20:"95-99",21:"100+"}}),
                            ("date",       {"name": "GE",                     "desc": "Giorno di decesso (formato variabile: MeseMeseGiornoGiorno).",
                                          "type": __type2name(str),         "values": None}),
                            ("m_15",       {"name": "MASCHI_15",                     "desc": "numero di decessi maschili nel 2015.",
                                          "type": __type2name(int),         "values": None}),
                            ("m_16",       {"name": "MASCHI_16",                     "desc": "numero di decessi maschili nel 2016.",
                                          "type": __type2name(int),         "values": None}),
                            ("m_17",       {"name": "MASCHI_17",                     "desc": "numero di decessi maschili nel 2017.",
                                          "type": __type2name(int),         "values": None}),
                            ("m_18",       {"name": "MASCHI_18",                     "desc": "numero di decessi maschili nel 2018.",
                                          "type": __type2name(int),         "values": None}),
                            ("m_19",       {"name": "MASCHI_19",                     "desc": "numero di decessi maschili nel 2019.",
                                          "type": __type2name(int),         "values": None}),
                            ("m_20",       {"name": "MASCHI_20",                     "desc": "numero di decessi maschili nel 2020.",
                                          "type": __type2name(int),         "values": None}),
                            ("f_15",       {"name": "FEMMINE_15",                     "desc": "numero di decessi femminili nel 2015.",
                                          "type": __type2name(int),         "values": None}),
                            ("f_16",       {"name": "FEMMINE_16",                     "desc": "numero di decessi femminili nel 2016.",
                                          "type": __type2name(int),         "values": None}),
                            ("f_17",       {"name": "FEMMINE_17",                     "desc": "numero di decessi femminili nel 2017.",
                                          "type": __type2name(int),         "values": None}),
                            ("f_18",       {"name": "FEMMINE_18",                     "desc": "numero di decessi femminili nel 2018.",
                                          "type": __type2name(int),         "values": None}),
                            ("f_19",       {"name": "FEMMINE_19",                     "desc": "numero di decessi femminili nel 2019.",
                                          "type": __type2name(int),         "values": None}),
                            ("f_20",       {"name": "FEMMINE_20",                     "desc": "numero di decessi femminili nel 2020.",
                                          "type": __type2name(int),         "values": None}),
                            ("t_15",       {"name": "TOTALE_15",                     "desc": "numero di decessi totali nel 2015.",
                                          "type": __type2name(int),         "values": None}),
                            ("t_16",       {"name": "TOTALE_16",                     "desc": "numero di decessi totali nel 2016.",
                                          "type": __type2name(int),         "values": None}),
                            ("t_17",       {"name": "TOTALE_17",                     "desc": "numero di decessi totali nel 2017.",
                                          "type": __type2name(int),         "values": None}),
                            ("t_18",       {"name": "TOTALE_18",                     "desc": "numero di decessi totali nel 2018.",
                                          "type": __type2name(int),         "values": None}),
                            ("t_19",       {"name": "TOTALE_19",                     "desc": "numero di decessi totali nel 2019.",
                                          "type": __type2name(int),         "values": None}),
                            ("t_20",       {"name": "TOTALE_20",                     "desc": "numero di decessi totali nel 2020.",
                                          "type": __type2name(int),         "values": None})
                            ]),
                         "nan":     9999,
                         "desc":    "Descrizione e tracciato record dati comunali giornalieri.docx"                
                         }
    with open(METAFILEITMORT,"w") as f:
        json.dump(METAITMORT, f)


try:
    METAFILEITGEO = osp.join(__THISDIR, METAFILEITGEO)
    assert os.path.exists(METAFILEITGEO)
    with open(METAFILEITGEO,"r") as f:
        METAITGEO = json.load(f)
except:
    METAITGEO      =  { "country":     {'code': 'IT', 'name': 'Italia'},
                         "lang":        {'code': 'it', 'name': 'italian'}, 
                         "file":        ['Com01012020_WGS84.shp', 'Com01012020_WGS84.shx', 'Com01012020_WGS84.dbf', 'Com01012020_WGS84.prj'],
                         "path":        'Com01012020',
                         "source":      'http://www.istat.it/storage/cartografia/confini_amministrativi/non_generalizzati/Limiti01012020.zip',
                         "fmt":         'shapefile',
                         "proj":        'WGS84',
                         "index":     OrderedDict( [
                             ("cod_rip",    {"name": "COD_RIP",         "desc": "Codice numerico della ripartizione geografica (5 modalità).",
                                             "type": __type2name(int),  "values": None}),
                             ("cod_reg",    {"name": "COD_REG",         "desc": "Codice numerico che identifica univocamente le 20 regioni italiane sul territorio nazionale.",   
                                             "type": __type2name(int),  "values": None}),
                             ("cod_prov",   {"name": "COD_PROV",        "desc": "Codice numerico che identifica univocamente la provincia nell’ambito del territorio nazionale.",   
                                             "type": __type2name(int),  "values": None}),
                             ("COD_CM",     {"name": "COD_CM",          "desc": "Codice Istat della città metropolitana (tre caratteri in formato numerico) ottenuto sommando il valore 200 al corrispondente codice della provincia.",   
                                             "type": __type2name(int),  "values": None}),
                             ("COD_PCM",    {"name": "COD_PCM",         "desc": "Codice della Provincia o della Città metropolitana.",   
                                             "type": __type2name(int),  "values": None}),
                             ("PRO_COM",    {"name": "PRO_COM",         "desc": "Codice del comune (numerico).",   
                                             "type": __type2name(int),  "values": None}),
                             ("PRO_COM_T",  {"name": "PRO_COM_T",       "desc": "Codice del Comune (alfanumerico)",   
                                             "type": __type2name(str),  "values": None}),
                             ("COMUNE",     {"name": "COMUNE",          "desc": "Denominazione del Comune.",
                                             "type": __type2name(str),  "values": None}),
                             ("COMUNE_A",   {"name": "COMUNE_A",        "desc": "Denominazione del Comune in lingua diversa dall'italiano.",
                                             "type": __type2name(str),  "values": None})
                            ]),
                         "desc": "https://www.istat.it/it/files//2018/10/Descrizione-dei-dati-geografici-2020-03-19.pdf"
                         }
    with open(METAFILEITGEO,"w") as f:
        json.dump(METAITGEO, f)

YEAR = 2020
YREF = 2000  # a leap year for sure


#%% Set dataset

# dIT = load_source(METAITMORT)
MortDatIT = datnatFactory(country = "IT")

dIT = MortDatIT(METAITMORT)
# some fields of interest 
FMT = dIT.meta.get('fmt') or dIT.meta.get('file','.').split('.')[1]
ENC = dIT.meta.get('enc',None) 
SEP =  dIT.meta.get('sep',None) 
DTYPE = {v['name']: Type.upytname2npt(v['type']) for v in dIT.meta.get('index',{}).values()}


#%% Load/format data

try:
    # dateparse = lambda x: datetime.strptime('%s%s' % (x,Yref), '%m%d%Y')
    dIT.load_data(fmt = FMT, encoding = ENC, sep = SEP, dtype = DTYPE,
                  # parse_dates=[day], date_parser=dateparse,
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

#%% Clean data

NAN = dIT.meta.get('nan')
T_20 = dIT.meta.get('index')['t_20']['name']

try:
    data.drop(data.loc[data[T_20]==NAN].index, inplace=True)
    print('#Cleaned records: %s - #Fields: %s' % data.shape)
except:
    pass

      
#%% Space info
# Retrieve basic temporal and geographical information

DAY = dIT.meta.get('index')['date']['name']

years = [int("20%s" % tot.split('_')[1]) for tot in data.columns if tot.startswith(T_20.split('_')[0])]
ystart, yend =  min(years), max(years)
print('Temporal coverage - Data collections considered: [%s, %s]' % (ystart, yend))

try:
    assert yend == YEAR
except:
    print('Last year available and year of study differ...')

# retrieve list of comu9ne
CITY = dIT.meta.get('index')['city']['name']
comuni = data[CITY].unique()
print('#Cities/municipalities: %s' % len(comuni))

#%% Time info
# Retrieve temporal series

DATEFMT = dIT.meta.get('datefmt')
data[DAY].head(5)

dstart, dend = data[DAY].min(), data[DAY].max()

def get_daymonth(ge):
    try:
        ge = datetime.strptime(ge, DATEFMT)
    except ValueError:  # deal with 29/02   
        ge = datetime.fromtimestamp(time.mktime(time.strptime(ge, DATEFMT)))
    except TypeError:
        pass
    return ge.day, ge.month

print('Period of data collection considered: [%s/%s, %s/%s]' % \
      (*get_daymonth(dstart), *get_daymonth(dend)))

def get_datetime(ge, year):
    d = dict(zip(['d', 'm', 'y'], [*get_daymonth(ge), year]))
    return Datetime.datetime(d, fmt='datetime')


#obsolete
def len_series(ystart, yend, dstart, dend): # not used: all the same lenght
    # get the lenght of the datasets. This will depend on the occurrence of a 29/02
    # (leap year) in the period consider
    # number of leap years in the range from startyear to curyear
    nleap = calendar.leapdays(ystart, yend+1)
    if nleap > 0:   yref = yend # any year
    else:           yref = YREF 
    td = Datetime.span(since=get_datetime(dstart,yref), until=get_datetime(dend,yref)) # until - since
    # lenght of the series in days
    return td.days
# ndays = len_series(ystart, yend, dstart, dend)

dstartref, dendref = get_datetime(dstart, YREF), get_datetime(dend, YREF)

wend = dendref.isocalendar()[1] # dendref.strftime("%U")
print('Period of data collection considered: until week #%s' % wend)

span = Datetime.span(since=dstartref, until=dendref)
ndays = span.days
print('Max lenght of the time series, i.e. number of days (max) covered by the' 
      ' data collection: %s' % ndays)

#%% Figure 1

dgeoIT = MortDatIT(METAITGEO)


try:
    # dgeoIT.load_content()
    dgeoIT.load_data(on_disk=True, infer_fmt=False)
except:
    print('Geographical data not available')
else:
    print ('Geo information retrieved on %s' % Datetime.datetime(Datetime.TODAY(), fmt='%d/%m/%Y'))

print('Attributes of the geodata (including geometries): %s' % list(dgeoIT.data.columns))  
dgeoIT.data.head(5)
dgeoIT.data['geometry'].head(5)

CITY_CODE = dIT.meta.get('index')['city_code']['name'] 
PRO_COM_T = dgeoIT.meta.get('index')['PRO_COM_T']['name'] 
code_comuni = Structure.uniq_list(data[CITY_CODE].to_list())

geodata = dgeoIT.data[dgeoIT.data.set_index(PRO_COM_T).index.isin(code_comuni)]
geodata.head(5)

f, ax = mplt.subplots(1, figsize=(12, 12))
geodata.plot(ax=ax)
ax.set_axis_off()
ax.set_title('Location of cities/municipalities (comuni) considered in the study',  
             fontsize='small')
mplt.show()


#%% Figure 2
# Daily and weekly deaths in current year

# the following assumes all dates are informed

#obsolete
def pos_leap(dstart):
    leapday = Datetime.datetime({'y':YREF, 'm':2, 'd':29}, fmt='datetime')
    # position of the 29/02 in the series
    td = Datetime.span(since=get_datetime(dstart,YREF), until=leapday)
    return td.days

leapday = Datetime.datetime({'y':YREF, 'm':2, 'd':29}, fmt='datetime')
spanleap = Datetime.span(since=dstartref, until=leapday)
ileapday = spanleap.days
print('Time series will be padded in position %s' % ileapday)
# note: indexing starts at 0

#obsolete
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

#obsolete
def pad_leapday(s, pos): 
    try:
        s[pos] = s[pos-1]
    except:
        s[pos] = np.nan # NAN

dailydeaths = pd.DataFrame()
for y in years:
    TCOL = dIT.meta.get('index')['t_%s' % str(y)[2:]]['name'] 
    dailydeaths[y] = data.groupby(DAY)[TCOL].agg('sum')
    if not calendar.isleap(y):
        yloc = dailydeaths.columns.get_loc(y)
        dailydeaths.iloc[ileapday,yloc] = dailydeaths.iloc[ileapday-1,yloc]
        

# we set a dummy index
idx_rng = pd.date_range(start=dstartref, end=dendref, freq=timedelta(1))
# mdates.drange(ddstart, ddend, timedelta(1))
dailydeaths.set_index(idx_rng, inplace=True)

def plot_one(dat, index = None, one = None, bar=False, dpi=120,
             marker='v', color='r', linestyle='-', 
             label='',  xlabel='', ylabel='', title = '', 
             xticks = None, xticklabels = None,
             xrottick = False, grid = False,           
             locator = None, formatter = None): 
    if dpi is None:     fig, ax = mplt.subplots()
    else:               fig, ax = mplt.subplots(dpi=dpi)
    if index is None:
        index = dat.index
    if bar is True:
        ax.bar(dat.index.values, 
               dat.loc[index] if one is None else dat.loc[index, one], 
               color=color, label=label)
    else:
        ax.plot(dat.loc[index] if one is None else dat.loc[index, one], 
                c=color, marker=marker, markersize=3, ls=linestyle, lw=0.6,
                label=label)
    ax.set_xlabel(xlabel), ax.set_ylabel(ylabel)
    if grid is not False:       ax.grid(linewidth=grid)
    if xticks is not None:      ax.set_xticks(xticks)
    if xticklabels is not None: ax.set_xticklabels(xticklabels)            
    if xrottick is not False:   ax.tick_params(axis ='x', labelrotation=xrottick)
    if formatter is not None:   ax.xaxis.set_major_formatter(formatter)
    if locator is not None:     ax.xaxis.set_major_locator(locator)
    ax.set_title(title,  fontsize='medium')
    ax.legend()
    return ax
    
years_exc = years.copy()
years_exc.remove(YEAR)
weeklydeaths = dailydeaths.resample('W').mean()
avdailydeathsexc = dailydeaths[years_exc].mean(axis = 1, skipna =True) # default

locator = mdates.DayLocator(bymonthday=[1,15]) # mdates.WeekdayLocator(interval=2)
formatter = mdates.DateFormatter('%d/%m')

ax = plot_one(dailydeaths, one = YEAR, index=slice(dstartref,dendref), label='daily',                
              locator = locator, formatter = formatter)
ax.plot(weeklydeaths.loc[dstartref:dendref, YEAR],
        marker='o', markersize=6, linestyle='-', label='weekly mean')
ax.plot(avdailydeathsexc.loc[dstartref:dendref],
        marker='+', linestyle=':',
        label='mean over [%s,%s]' % (min(years_exc),max(years_exc)))
ax.legend()

def plot_oneversus(dat, index = None, one = None, versus = None,  dpi=120,
                   xlabel='', ylabel='', title = '', legend = None,                 
                   grid = False, locator = None, formatter = None):    
    if dpi is None:     fig, ax = mplt.subplots()
    else:               fig, ax = mplt.subplots(dpi=dpi)
    if index is None:
        index = dat.index
    if one is not None:
        ax.plot(dat.loc[index,one], ls='-', lw=0.6, c='r', 
                marker='v', markersize=6, fillstyle='none')
        next(ax._get_lines.prop_cycler)
    if versus is None:
        versus = dat.columns
        try:    versus.remote(one)
        except: pass
    ax.plot(dat.loc[index,versus], ls='None', marker='o', fillstyle='none')
    ax.set_xlabel(xlabel), ax.set_ylabel(ylabel)
    if grid is not False:       ax.grid(linewidth=grid)
    if locator is not None:     ax.xaxis.set_major_locator(locator)
    if formatter is not None:   ax.xaxis.set_major_formatter(formatter)
    ax.set_title(title, fontsize='medium')
    if legend is None:
        legend = [one]
        legend.extend(versus)
    ax.legend(legend)
    return ax

cumdailydeaths = dailydeaths.cumsum(axis = 0, skipna =True) # default

plot_oneversus(dailydeaths, one = YEAR, versus = years_exc[::-1],
            xlabel='day since Jan 1st', ylabel='death counts', 
            title = 'Dailty deaths (all, total)',                
            locator = locator, formatter = formatter)

plot_oneversus(cumdailydeaths, one = YEAR, versus = years_exc[::-1],
            xlabel='day since Jan 1st', ylabel='cumulative death counts', 
            title = 'Daily cumulative deaths (all, total)',                
            locator = locator, formatter = formatter)


#%% Figure 3 
# Age distribution of total deaths
AGE = dIT.meta.get('index')['age']['name']

if True:
    dstart = get_datetime('0315',YREF)   
    week = dstart.isocalendar()[1]
else:
    week = 12 
    dstart = datetime.strptime('%s-W%s-1' % (YEAR,week), '%G-W%V-%u')
    #      = datetime.strptime('%s-W%s-1' % (YEAR,week), "%Y-W%W-%w") % complete week
    # only in Python >3.8: date.fromisocalendar(YEAR, week, 1)
    dstart = get_datetime(dstart,YREF) # in YREF reference year
dend = dstart + timedelta(6) # ddays[-1] 

ddays = ['%02d%02d' % (d.month,d.day) for d in [dstart + timedelta(i) for i in range(6)]]

ageofdeaths = dict.fromkeys(['t','f','m'])
for k in ageofdeaths.keys():
    deaths = pd.DataFrame()
    for y in years:
        COL = dIT.meta.get('index')['%s_%s' % (k,str(y)[2:])]['name']
        d = data.groupby([AGE,DAY])[COL].agg('sum') #.reindex(idx_rng)
        if leapday >= dstart and leapday <= dend:
            # ispan = Datetime.span(since=dstart, until=leapday)
            # d.iloc[ileapday] = d.iloc[ileapday-1]
            pass
        deaths[y] = d[d.index.get_level_values(DAY).isin(ddays)].groupby(AGE).agg('sum')
    ageofdeaths.update({k: deaths})
    
FORMATTER = dIT.meta.get('index')['age']['values']
    
ax = plot_one(ageofdeaths['t'], one = YEAR, label = YEAR,
              marker = 'v', color = 'r', linestyle = '-', 
              xrottick = -45, grid = 0.2,
              xlabel = 'age group', 
              ylabel = 'death total counts',
              title = 'Age distribution of total deaths in the period [%s/%s, %s/%s] (week #%s)' % 
                      (*get_daymonth(dstart), *get_daymonth(dend), week) , 
              xticks = list(range(len(FORMATTER.keys()))),
              xticklabels = list(FORMATTER.values())
              )
next(ax._get_lines.prop_cycler)
if True:
    ax.plot(ageofdeaths['t'][years_exc[::-1]],
            marker='o', markersize=3, linestyle='None')
    ax.legend(years[::-1]) # cheating...
else:
    ageofdeaths['t'][years_exc[::-1]]   \
        .plot(ax=ax, marker='o', linestyle = 'None', markersize=4) 
    ax.tick_params(axis ='x', labelrotation=-45)
    ax.legend()


#%% Figure 4
# Relative increments

for k in ageofdeaths.keys():
    deaths = ageofdeaths[k]
    deaths['base'] = deaths[years_exc].mean(axis = 1, skipna =True) # default
    # deaths['rinc'] = deaths.apply(lambda row: (row[YEAR] - row['base']) / row['base'], axis=1)
    deaths['rinc'] = deaths[YEAR].sub(deaths.base).div(deaths.base)

astart, aend = 11, 20
rages, sages = range(astart, aend), slice(astart, aend)

FORMATTER = dIT.meta.get('index')['age']['values']
def func_formater(val, pos):
    try:        return FORMATTER[str(int(val))]
    except:     return ''

ax = plot_one(ageofdeaths['t'], index = sages, one = 'rinc',
              marker = '*', color = 'k', linestyle = 'None', 
              xrottick = -45, grid = 0.2,
              xlabel = 'age class', 
              ylabel = 'increment over baseline',
              title = 'Relative increment of %s over baseline in the period [%s/%s, %s/%s] per age group' %
                (YEAR, *get_daymonth(dstart), *get_daymonth(dend)), 
              label = 'm+f',
              formatter = FuncFormatter(func_formater),
              locator = MaxNLocator(integer=True)
              )
ax.plot(ageofdeaths['f'].loc[sages,'rinc'],
        marker='o', color='g', markersize=3, linestyle='None', label='female')
ax.plot(ageofdeaths['m'].loc[sages,'rinc'],
        marker='D', color='b', markersize=3, linestyle='None', label='male')
ax.legend()


#%% Figure 5 
# Cumulative increments

incdeaths = ageofdeaths['t'].apply(lambda row: row[YEAR] - row['base'], axis=1)
cumdeaths = incdeaths.cumsum(axis = 0, skipna =True)

plot_one(cumdeaths/max(cumdeaths), index = sages, 
         marker = 'o', color = 'b', xrottick = -45, 
         xlabel = 'age class', 
         ylabel = 'fraction of excess deaths',         
         title = 'Empirical cumulative distribution of excess deaths in the period [%s/%s, %s/%s] per age group' % 
             (*get_daymonth(dstart), *get_daymonth(dend)), 
         label = 'm+f',
         formatter = FuncFormatter(func_formater),
         locator = MaxNLocator(integer=True)
         )


#%% Figure 6
# Daily and weekly deaths in current year for Male 65+

dailydeaths_m65 = pd.DataFrame()
for y in years:
    MCOL = dIT.meta.get('index')['m_%s' % str(y)[2:]]['name'] 
    dailydeaths_m65[y] = data[data[AGE].isin(rages)].groupby(DAY)[MCOL].agg('sum')
    if not calendar.isleap(y):
        yloc = dailydeaths_m65.columns.get_loc(y)
        dailydeaths_m65.iloc[ileapday,yloc] = dailydeaths_m65.iloc[ileapday-1,yloc]
        
dailydeaths_m65.set_index(idx_rng, inplace=True)

cumdailydeaths_m65 = dailydeaths_m65.cumsum(axis = 0, skipna =True) # default

locator = mdates.DayLocator(bymonthday=[1,15]) # mdates.WeekdayLocator(interval=2)
formatter = mdates.DateFormatter('%d/%m')

plot_oneversus(dailydeaths_m65, one = YEAR, versus = years_exc[::-1],
            xlabel='day since Jan 1st', 
            ylabel='death counts', 
            title = 'Dailty deaths (male 65+, total)',                
            locator = locator, formatter = formatter)

plot_oneversus(cumdailydeaths_m65, one = YEAR, versus = years_exc[::-1],
            xlabel='day since Jan 1st', 
            ylabel='cumulative death counts', 
            title = 'Dailty cumulative deaths (male 65+, total)',                
            locator = locator, formatter = formatter)


#%% Figure 7
# Total deaths in the period 1-21 March per individual municipalities

CITY_CODE = dIT.meta.get('index')['city_code']['name']
PROV_CODE = dIT.meta.get('index')['prov_code']['name']
PROVINCE = dIT.meta.get('index')['province']['name']

cities = data.loc[:,[CITY, CITY_CODE, PROVINCE, PROV_CODE]].drop_duplicates()
comuni = ['Albino', 'Bergamo', 'Brescia', 'Codogno', 'Crema', 
          'Milano', 'Nembro', 'Parma', 'Piacenza', 'San Giovanni Bianco']
comunitable = cities.loc[cities[CITY].isin(comuni)]
comunitable.set_index(comunitable[CITY_CODE], inplace=True)
# comunitable.drop(columns=CITY_CODE, inplace=True)

data['refdate'] = data[DAY].apply(lambda row: get_datetime(row, YREF))
# data.set_index('refdate', inplace=True)

dstart = get_datetime('0301',YREF)
dend = get_datetime('0321',YREF)

# data[(data['refdate']>=dstart) & (data['refdate']<=dend)]
# data[data['refdate'].between(dstart, dend, inclusive=True)]

citydeaths = pd.DataFrame()
for y in years:
    TCOL = dIT.meta.get('index')['t_%s' % str(y)[2:]]['name'] 
    citydeaths[y] = data[data['refdate'].between(dstart, dend, inclusive=True)]   \
        .groupby(CITY_CODE)[TCOL].agg('sum')
    # if not calendar.isleap(y) and dstart<=leapday and dend>=leapday:
    #     yloc = dailydeaths_m65.columns.get_loc(y)
    #     dailydeaths_m65.iloc[ileapday,yloc] = dailydeaths_m65.iloc[ileapday-1,yloc]
citydeaths['base'] = citydeaths.loc[:,years_exc].max(axis=1)
# citydeaths.drop(columns = years_exc)

ax = citydeaths.plot(loglog=True,  x='base', y=YEAR, # kind='scatter',
                     ls='None', color='b', marker='s', fillstyle='none',
                     label='data')
# ax = citydeaths.set_index('basemax')[YEAR].plot(loglog=True, linestyle='None', color='b', marker='s', fillstyle='none')
xlim, ylim = ax.get_xlim(), ax.get_ylim()
x = np.arange(0, 10**4, 1)
for i, c in zip([1,2,3,4,10], ['g', 'purple', 'red', 'k', 'pink']):    
    ax.loglog(x, i * x, label = 'y=%sx' % ('' if i==1 else str(i)), ls='-.', lw=0.8, c=c)
ax.set_xlim(xlim), ax.set_ylim(ylim)
ax.grid(linewidth=0.3, which="both", ls='dotted')
for index in comunitable.index:
    xpos, ypos = citydeaths.loc[index,'base'], citydeaths.loc[index,YEAR]
    r = np.random.random() +1
    ax.annotate(comunitable.loc[index,CITY], 
                (xpos, ypos), 
                xytext=(xpos+r*10**np.log10(xpos), ypos-r*10**(np.log10(ypos)-1)),  
                arrowprops=dict(arrowstyle='->'), #facecolor='black', shrink=0.5, width = 0.1),
                size=9, ha='center')
ax.set_xlabel('baseline')
ax.set_ylabel('deaths in %s (selected comuni)' % YEAR)
ax.set_title('Total deaths in the period %s - %s per individual municipalities' % 
             (Datetime.datetime(dstart, fmt='%d %b'), Datetime.datetime(dend, fmt='%d %b')),  fontsize='medium'),
ax.legend()

#%% Figure 7' - on map

# cityrdeaths = pd.DataFrame(index=citydeaths.index)
# cityrdeaths[PRO_COM_T] = citydeaths.index
# # cityrdeaths['baseave'] = citydeaths.loc[:,years_exc].mean(axis = 1, skipna =True) 
# cityrdeaths['base'] = citydeaths.base
# cityrdeaths['rinc'] = citydeaths[YEAR].sub(cityrdeaths.base).div(cityrdeaths.base)
# cityrdeaths.drop(columns='base', inplace=True)

citydeaths['rinc'] = citydeaths[YEAR].sub(citydeaths.base).div(citydeaths.base)
citydeaths[PRO_COM_T] = citydeaths.index
geodata = geodata.merge(citydeaths, on=PRO_COM_T)
geodata.head(5)

f, ax = mplt.subplots(1, figsize=(12, 12))
geodata.plot(column='rinc', legend=True, ax=ax)
ax.set_axis_off()
ax.set_title('Relative increment over selected cities/municipalities (comuni)',  
             fontsize='small')
mplt.show()


#%% Figure 8
# Codogno

codogno = 'Codogno'
provincia = cities.loc[cities[CITY]==codogno].loc[:,[PROVINCE,PROV_CODE]].values.tolist()[0]

dailydeaths = pd.DataFrame()
for y in years:
    TCOL = dIT.meta.get('index')['t_%s' % str(y)[2:]]['name'] 
    dailydeaths[y] = data[data[PROV_CODE]==provincia[1]].groupby(DAY)[TCOL].agg('sum')
    if not calendar.isleap(y):
        yloc = dailydeaths.columns.get_loc(y)
        dailydeaths.iloc[ileapday,yloc] = dailydeaths.iloc[ileapday-1,yloc]
        
# we set a dummy index
idx_rng = pd.date_range(start=dstartref, end=dendref, freq=timedelta(1))
# mdates.drange(ddstart, ddend, timedelta(1))
dailydeaths.set_index(idx_rng, inplace=True)

cumdailydeaths = dailydeaths.cumsum(axis = 0, skipna =True) # default

locator = mdates.DayLocator(bymonthday=[1,15]) # mdates.WeekdayLocator(interval=2)
formatter = mdates.DateFormatter('%d/%m')

plot_oneversus(dailydeaths, one = YEAR, versus = years_exc[::-1],
            xlabel='day since Jan 1st', ylabel='death counts', 
            title = 'Dailty deaths (total) - Provincia %s' % provincia[0],                
            locator = locator, formatter = formatter)

plot_oneversus(cumdailydeaths, one = YEAR, versus = years_exc[::-1],
            xlabel='day since Jan 1st', ylabel='cumulative death counts', 
            title = 'Daily cumulative deaths (total) - Provincia %s' % provincia[0],                
            locator = locator, formatter = formatter)

dailydeaths_m65 = pd.DataFrame()
for y in years:
    MCOL = dIT.meta.get('index')['m_%s' % str(y)[2:]]['name'] 
    dailydeaths_m65[y] = data[(data[PROV_CODE]==provincia[1]) & (data[AGE].isin(rages))].groupby(DAY)[MCOL].agg('sum')
    if not calendar.isleap(y):
        yloc = dailydeaths_m65.columns.get_loc(y)
        dailydeaths_m65.iloc[ileapday,yloc] = dailydeaths_m65.iloc[ileapday-1,yloc]
        
dailydeaths_m65.set_index(idx_rng, inplace=True)

cumdailydeaths_m65 = dailydeaths_m65.cumsum(axis = 0, skipna =True) # default

locator = mdates.DayLocator(bymonthday=[1,15]) # mdates.WeekdayLocator(interval=2)
formatter = mdates.DateFormatter('%d/%m')

plot_oneversus(dailydeaths_m65, one = YEAR, versus = years_exc[::-1],
            xlabel='day since Jan 1st', 
            ylabel='death counts', 
            title = 'Dailty deaths (male 65+, total) - Provincia %s' % provincia[0],                
            locator = locator, formatter = formatter)

plot_oneversus(cumdailydeaths_m65, one = YEAR, versus = years_exc[::-1],
            xlabel='day since Jan 1st', 
            ylabel='cumulative death counts', 
            title = 'Dailty cumulative deaths (male 65+, total) - Provincia %s' % provincia[0],                
            locator = locator, formatter = formatter)
