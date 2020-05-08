losstat
=====

Basic descriptive statistics on mortality data
--- 

The material hereby aims at reproducing the results of Ricciato's preliminary study on 2020 mortality data from ISTAT (see [below](#References)).

<table align="center">
    <!-- <tr> <td align="left"><i>documentation</i></td> <td align="left">available at: ...</td> </tr> -->
    <tr> <td align="left"><i>status</i></td> <td align="left">since 2020 &ndash; <b>closed</b></td></tr> 
    <tr> <td align="left"><i>contributors</i></td> 
    <td align="left" valign="middle">
<a href="https://github.com/fabioricciato"><img src="https://github.com/fabioricciato.png" width="40"></a>
<a href="https://github.com/gjacopo"><img src="https://github.com/gjacopo.png" width="40"></a>
</td> </tr> 
    <tr> <td align="left"><i>license</i></td> <td align="left"><a href="https://joinup.ec.europa.eu/sites/default/files/eupl1.1.-licence-en_0.pdfEUPL">EUPL</a> </td> </tr> 
</table>

**Description**

The _"Data resources"_ section [below](#Data) references the data used for the study (freely available for download). The present project will enable you to reproduce most of the figures presented in the document:

* [notebook](https://nbviewer.jupyter.org/github/gjacopo/morbstat/blob/master/01_preliminary_IT_study.ipynb)

**(Re)run - Usage**

You can rerun the notebook :
* in [`Google colab`](https://colab.research.google.com/)** environment (you will need a _Google_ login): launch [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gjacopo/morbstat/blob/master/01_preliminary_IT_study.ipynb).
* in [`binder`](https://mybinder.org) environment: [![Binder](https://mybinder.org/badge_logo.svg)](http://mybinder.org/v2/gh/eurostat/losstat/master?filepath=notebooks/01_preliminary_IT_study.ipynb) 

You will need standard `Python` library for data handling, _e.g._, `pandas`, `numpy`, `matplotlib`, and date manipulation, _e.g._, `datetime`, `calendar` (see also [below](#Software)). The code herein also uses the [`pyeudatnat`](https://github.com/eurostat/pyEUDatNat) package.

The `environment.yml` file in this directory provides with all requirements. See also the _"Settings"_ cell of the [`ITmorb.py`](ITmorb.py) source code file.
 
**<a name="Note"></a>Note**
 
The data used in the provided notebook will fetch data from the source directly (_ISTAT_ online database, see [below](#Data)). Therefore, when (re)running the notebook, the results and figures you generate always refer to the latest available (possibly updated) data. The results and figures presented in Ricciato's document refer to the data downloaded at the time of the study, hence on April, 16th.
 
**<a name="Software"></a>Software requirements**

* Package for metadata and data fetching:  [`pyeudatnat`](https://github.com/eurostat/pyEUDatNat)).
* Packages for time-series and dataframe handling: [`numpy`](https://numpy.org), [`pandas`](http://pandas.pydata.org).
* Plotting package: [`matplotlib`](https://matplotlib.org).

**<a name="Data"></a>Data resources**
 
* [_ISTAT_](https://www.istat.it/) online database: [http://dati.istat.it](http://dati.istat.it).
* Mortality data collected by _ISTAT_: ["dati di mortalitˆ"](https://www.istat.it/it/archivio/240401), including micro datasets with daily death counts: ["dataset analitico con i decessi giornalieri"_](https://www.istat.it/it/files//2020/03/comune-giorno.zip) and aggregated datasets with weekly death counts ["dataset sintetico con i decessi per settimana"](https://www.istat.it/it/files//2020/03/comuni-settimana.zip).
* [Confini delle unitˆ amministrative a fini statistici al 1o gennaio 2020](https://www.istat.it/it/archivio/222527).
* [Codici statistici delle unitˆ amministrative territoriali: comuni, cittˆ metropolitane, province e regioni](https://www.istat.it/it/archivio/6789).
* Identification of cities/municipalities: ["Elenco dei communi"](https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv).

**<a name="References"></a>References**

* Ricciato F. (2020): [A preliminary view at 2020 mortality data from ISTAT](https://ec.europa.eu/eurostat/cros/content/preliminary-view-2020-mortality-data-istat), last updated on April 16th.
* Study of COVID-19 over mortality by _ISTAT_(2020): [Impatto dellÕepidemia COVID-19 sulla mortalitˆ totale della popolazione residente primo trimestre 2020](https://www.istat.it/it/files//2020/05/Rapporto_Istat_ISS.pdf)
* Timeline of deaths in IT: ["L'andamento dei decessi del 2020"](https://www.istat.it/it/files//2020/03/Decessi_2020_Nota.pdf).
* Visualisations of deaths in IT cities and provinces  published by _ISTAT_ (using the same data): ["Andamento dei decessi"](https://public.tableau.com/views/Mortalit_15858412215300/Mortalit).

**<a name="Other"></a>Related publications and studies / In the news**

* [Coronavirus: La luce in fondo al tunnel](https://www.neodemos.info/articoli/coronavirus-la-luce-in-fondo-al-tunnel/), _neodemos_, published on March 30th.
* [Global coronavirus death toll could be 60% higher than reported](https://www.ft.com/content/6bd88b7d-3386-4543-b2e9-0d5c6fac846c), _Financial Times_, published on April 26th.
* [Tracking covid-19 excess deaths across countries](https://www.economist.com/graphic-detail/2020/04/16/tracking-covid-19-excess-deaths-across-countries), _The Economist_, published on April 16th.
https://mtmx.github.io/blog/deces_pandemie/
* [An unprecedented context of health crisis](https://dc-covid.site.ined.fr/en/), _INED_. Comparison of the COVID-19 pandemics in 6 countries, data available [here](https://dc-covid.site.ined.fr/en/data/).
* Timeline of deaths in FR regions: [Deces pendant la pandemie](https://mtmx.github.io/blog/deces_pandemie/). 

<!-- of interest: https://colab.research.google.com/drive/1WikPfT-Zrelor-4Wh0EocB49akR7yIvY#scrollTo=CoMUgyp22zMm -->
