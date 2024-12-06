# IGNwmtsPyLib

## Aim

Provide a python library for using IGN WMTS web service.

## Documentation

### IGN WMTS
https://geoservices.ign.fr/documentation/services/services-geoplateforme/diffusion#70062

### IGN WMTS Deprecated
Explain the principal in better way than the current IGN WMTS actual documentation

https://geoservices.ign.fr/documentation/services/services-deprecies/images-tuilees-wmts-ogc

## Run locally

```shell
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ python3 wmts_example.py
```

## Usage externally

```shell
$ pip install git+https://github.com/francois-poidevin/IGNwmtsPyLib@main
```

```python
from wmtsPyLib.wmts.wmts import Wmts

_wmts = Wmts()

print(_wmts.getCapabilities())

print(_wmts.getAvailableLayers())

```

Take a look in __./wmts_example.py__ for examples