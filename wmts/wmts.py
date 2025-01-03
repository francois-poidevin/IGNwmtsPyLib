import math
from wmts.variables import EPSG_3857_RES_M_PX, EPSG_2154_RES_M_PX
from PIL import Image
import requests
from io import BytesIO
from pyproj import Transformer
import xml.etree.ElementTree as ET
import os

class BoundingBox:
    def __init__(self, nelon: float, nelat: float, swlon: float,  swlat: float):
        self._nelon = nelon
        self._nelat = nelat
        self._swlon = swlon
        self._swlat = swlat

    def getNELon(self):
        return self._nelon

    def getNELat(self):
        return self._nelat

    def getSWLon(self):
        return self._swlon

    def getSWLat(self):
        return self._swlat

class Coordinate:
    def __init__(self, lon, lat):
        self._lon = lon
        self._lat = lat

    def getCoordinate(self):
        return self._lon, self._lat
    
class TileMatrix():
    def __init__(self, level, topLeftCorner: dict[str, float], tileSizePx):
        self._level = level
        self._topLeftCorner = topLeftCorner
        self._tileSizePx = tileSizePx

    def getLevel(self):
        return self._level
    
    def getTopLeftCorner(self):
        return self._topLeftCorner
    
    def getTileSizePx(self):
        return self._tileSizePx

class TileMatrixSet():
    def __init__(self, identifier: str, crs: str, tileMatrices: dict[str, TileMatrix]):
        self._identifier = identifier
        self._crs = crs
        self._tileMatrices = tileMatrices

    def getIdentifier(self):
        return self._identifier

    def getCRS(self):
        return self._crs
    
    def getTileMatrices(self):
        return self._tileMatrices
    
class IgnLayer():
    def __init__(self, title: str, abstract: str, identifier: str, tileMatrixSetIdentifier: str, tileMatrixSet: TileMatrixSet):
        self._title = title
        self._abstract = abstract
        self._identifier = identifier
        self._tileMatrixSetIdentifier = tileMatrixSetIdentifier
        self._tileMatrixSet = tileMatrixSet

    def getTitle(self):
        return self._title
    
    def getAbstract(self):
        return self._abstract
    
    def getIdentifier(self):
        return self._identifier
    
    def getTileMatrixSetIdentifier(self):
        return self._tileMatrixSetIdentifier
    
    def getTileMatrixSet(self):
        return self._tileMatrixSet
    
    def toString(self):
        return "Title: " + self._title + "\nAbstract: " + self._abstract + "\nIdentifier: " + self._identifier + "\nTileMatrixSetIdentifier: " + self._tileMatrixSetIdentifier

class Wmts():
    def __init__(self):
        pass

    def getCapabilities(self):
        # Get data from https://data.geopf.fr/annexes/ressources/wmts/ortho.xml
        url='https://data.geopf.fr/annexes/ressources/wmts/ortho.xml'
        response = requests.get(url)
        if response.status_code == 404:
            # Handle 404 error
            raise Exception("url does not exist (HTTP404): " + url)
        elif response.status_code == 200:
            # Use response content
            return ET.parse(BytesIO(response.content))
        else:
            # Handle all others http status codes
            raise Exception("url request error: " + url + " . HTTPCode: " + response.status_code)

    def getAvailableLayers(self):
        layers = {}
        # Get data from https://data.geopf.fr/annexes/ressources/wmts/ortho.xml
        url='https://data.geopf.fr/annexes/ressources/wmts/ortho.xml'
        response = requests.get(url)
        if response.status_code == 404:
            # Handle 404 error
            raise Exception("url does not exist (HTTP 404): " + url)
        elif response.status_code == 200:
            # Use response content
            xmlIGN =  ET.parse(BytesIO(response.content))
        else:
            # Handle all others http status codes
            raise Exception("url request error: " + url + " . HTTPCode: " + response.status_code)

        xmlContent = xmlIGN.find('{http://www.opengis.net/wmts/1.0}Contents')
        
        xmlLayers = xmlContent.findall('{http://www.opengis.net/wmts/1.0}Layer')
        for child in xmlLayers:
            layerTitle = child.find('{http://www.opengis.net/ows/1.1}Title').text
            layerAbstract = child.find('{http://www.opengis.net/ows/1.1}Abstract').text
            layerIdentifier = child.find('{http://www.opengis.net/ows/1.1}Identifier').text
            layerTileMatrixSetIdentifier = ""
            xmlLayerTileMatrixSet = child.find('{http://www.opengis.net/wmts/1.0}TileMatrixSetLink')
            layerTileMatrixSetIdentifier = xmlLayerTileMatrixSet.find('{http://www.opengis.net/wmts/1.0}TileMatrixSet').text
        
            # Load tileMatrix for the layer
            xmlTileMatrixSet = xmlContent.findall('{http://www.opengis.net/wmts/1.0}TileMatrixSet')
            for xmlTileMatrixSetChild in xmlTileMatrixSet:
                if xmlTileMatrixSetChild.find('{http://www.opengis.net/ows/1.1}Identifier').text == layerTileMatrixSetIdentifier:
                    tileMatrices = {}
                    tmsCRS = ""
                    tmsCRS = xmlTileMatrixSetChild.find('{http://www.opengis.net/ows/1.1}SupportedCRS').text
                    xmlTileMatrices = xmlTileMatrixSetChild.findall('{http://www.opengis.net/wmts/1.0}TileMatrix')
                    for tileMatrix in xmlTileMatrices:
                        topLeftCornerDict = {}
                        level = tileMatrix.find('{http://www.opengis.net/ows/1.1}Identifier').text
                        topLeftCorner = tileMatrix.find('{http://www.opengis.net/wmts/1.0}TopLeftCorner').text.split()
                        topLeftCornerDict['x0'] = float(topLeftCorner[0])
                        topLeftCornerDict['y0'] = float(topLeftCorner[1])
                        tileSize = int(tileMatrix.find('{http://www.opengis.net/wmts/1.0}TileWidth').text)
                        tileMatrices[level] = TileMatrix(level, topLeftCornerDict, tileSize)
                    tileMatrixSet = TileMatrixSet(layerTileMatrixSetIdentifier, tmsCRS, tileMatrices)

                    ignLayer = IgnLayer(layerTitle, layerAbstract, layerIdentifier, layerTileMatrixSetIdentifier, tileMatrixSet)
                    layers[layerIdentifier] = ignLayer
                    break
        return layers
    
    def lat_lon_WGS84_to_projection(self, lat: float, lon: float, proj: str):
        return Transformer.from_crs("EPSG:4326", proj).transform(lat, lon)
    
    def projection_to_lat_lon_WGS84(self, x: int, y: int, proj: str):
        return Transformer.from_crs(proj, "EPSG:4326").transform(x, y)
    
    def getTileSizeMeter(self, tileMatrixSet: TileMatrixSet, level: str):
        tileMatrix = tileMatrixSet.getTileMatrices()[level]
        if tileMatrixSet.getCRS() == "EPSG:3857":
            tileSizeMeter = tileMatrix.getTileSizePx()*EPSG_3857_RES_M_PX[int(level)]
        elif tileMatrixSet.getCRS() == "EPSG:2154":
            tileSizeMeter = tileMatrix.getTileSizePx()*EPSG_2154_RES_M_PX[int(level)]
        else:
            raise Exception("projection not supported")
        
        return tileSizeMeter
    
    def getTileSizeMeter(self, tileMatrix: TileMatrix, crs: str, level: str):
        if crs == "EPSG:3857":
            tileSizeMeter = tileMatrix.getTileSizePx()*EPSG_3857_RES_M_PX[int(level)]
        elif crs == "EPSG:2154":
            tileSizeMeter = tileMatrix.getTileSizePx()*EPSG_2154_RES_M_PX[int(level)]
        else:
            raise Exception("projection not supported")
        
        return tileSizeMeter
    
    def lat_lon_to_IGN_projection(self, lat: float, lon: float, tileMatrixSet: TileMatrixSet, level: str):
        tileMatrix = tileMatrixSet.getTileMatrices()[level]
        topLeftCorner = tileMatrix.getTopLeftCorner()

        x, y = self.lat_lon_WGS84_to_projection(lat, lon, tileMatrixSet.getCRS())
        xCalibrate = x - topLeftCorner['x0']
        yCalibrate = topLeftCorner['y0'] - y

        if tileMatrixSet.getCRS() == "EPSG:3857":
            tileSizeMeter = tileMatrix.getTileSizePx()*EPSG_3857_RES_M_PX[int(level)]
        elif tileMatrixSet.getCRS() == "EPSG:2154":
            tileSizeMeter = tileMatrix.getTileSizePx()*EPSG_2154_RES_M_PX[int(level)]
        else:
            raise Exception("projection not supported")
        
        tileColumRaw=xCalibrate/tileSizeMeter
        tileRowRaw=yCalibrate/tileSizeMeter
        
        val_x = math.floor(tileColumRaw)
        val_y = math.floor(tileRowRaw)
        
        return val_x, val_y
    
    def lat_lon_bbox_to_IGN_projection_bbox(self, bbox: BoundingBox, tileMatrixSet: TileMatrixSet, lvl: str):
        # init values
        ne_x, ne_y, sw_x, sw_y = -1,-1,-1,-1

        ## compute x,y NE Web Mercator calibrated
        ne_x, ne_y = self.lat_lon_to_IGN_projection(bbox.getNELat(), bbox.getNELon(), tileMatrixSet, lvl)
        
        ## compute x,y SW Web Mercator calibrated
        sw_x, sw_y = self.lat_lon_to_IGN_projection(bbox.getSWLat(), bbox.getSWLon(), tileMatrixSet, lvl)

        return ne_x, ne_y, sw_x, sw_y
    
    def ign_projection_to_lat_lon(self, x: int, y: int, tileMatrixSet: TileMatrixSet, level: str):

        tileMatrix = tileMatrixSet.getTileMatrices()[level]
        topLeftCorner = tileMatrix.getTopLeftCorner()

        if tileMatrixSet.getCRS() == "EPSG:3857":
            tileSizeMeter = tileMatrix.getTileSizePx()*EPSG_3857_RES_M_PX[int(level)]
        elif tileMatrixSet.getCRS() == "EPSG:2154":
            tileSizeMeter = tileMatrix.getTileSizePx()*EPSG_2154_RES_M_PX[int(level)]
        else:
            raise Exception("projection not supported")
        
        x_uncalibrated = (x * tileSizeMeter) + topLeftCorner['x0']
        y_uncalibrated =  -(y * tileSizeMeter) + topLeftCorner['y0']
        
        return self.projection_to_lat_lon_WGS84(x_uncalibrated, y_uncalibrated, tileMatrixSet.getCRS())

    def getImageIGNWMTSBbox(self, ne_x: int, ne_y: int, sw_x: int, sw_y: int, level: str, tileSetMatrixSet: str, layer: str):
        imagesDict = {}
        # Loop on ne/sw web mercator tiles
        x = ne_x
        while x <= sw_x:
            imagesDict[x] = {}
            y = ne_y
            while y >= sw_y:
                image = self.getImageIGNWMTS(x, y, level, tileSetMatrixSet, layer)
                imagesDict[x][y] = image
                y -= 1
            x += 1
            
        return imagesDict

    # https://pillow.readthedocs.io/en/stable/reference/ImageFile.html#PIL.ImageFile.ImageFile
    def getImageIGNWMTS(self, x: int, y: int, level: str, tileSetMatrixSet: str, layer: str):
        # Request pattern https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER={Couche}&STYLE={Style}&FORMAT={format}&TILEMATRIXSET={TileMatrixSet}&TILEMATRIX={TileMatrix}&TILEROW={TileRow}&TILECOL={TileCol}
        url='https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER='+layer+'&STYLE=normal&FORMAT=image/jpeg&TILEMATRIXSET='+tileSetMatrixSet+'&TILEMATRIX='+level+'&TILEROW='+ str(y)+'&TILECOL='+ str(x)
        response = requests.get(url)
        if response.status_code == 404:
            # Handle 404 error
            raise Exception("url does not exist (HTTP 404): " + url)
        elif response.status_code == 200:
            # Use response content
            print("Image received.")
            return Image.open(BytesIO(response.content))
        else:
            # Handle all others http status codes
            raise Exception("url request error: " + url + " . HTTPCode: " + response.status_code)
        
    def saveImageIGNWMTSBbox(self, ne_x: int, ne_y: int, sw_x: int, sw_y: int, level: str, tileSetMatrixSet: str, layer: str, filePath: str):
        filePathArray = []
        # Loop on ne/sw web mercator tiles
        x = ne_x
        while x <= sw_x:
            y = ne_y
            while y >= sw_y:
                savedFilePath = self.saveImageIGNWMTS(x, y, level, tileSetMatrixSet, layer, filePath)
                filePathArray.append(savedFilePath)
                y -= 1
            x += 1
            
        return filePathArray
        
    def saveImageIGNWMTS(self, x: int, y: int, level: str, tileSetMatrixSet: str, layer: str, saveFolder: str):
        # Add trailing slash if it is not already there
        saveFolder = os.path.join(saveFolder, '', '')
        # Check saveFolder parameter - check folder exist
        if not os.path.exists(saveFolder):
            raise Exception(f"Path does not exist: {saveFolder}")
        
        # Request pattern https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER={Couche}&STYLE={Style}&FORMAT={format}&TILEMATRIXSET={TileMatrixSet}&TILEMATRIX={TileMatrix}&TILEROW={TileRow}&TILECOL={TileCol}
        url='https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER='+layer+'&STYLE=normal&FORMAT=image/jpeg&TILEMATRIXSET='+tileSetMatrixSet+'&TILEMATRIX='+level+'&TILEROW='+ str(y)+'&TILECOL='+ str(x)
        response = requests.get(url)
        if response.status_code == 404:
            # Handle 404 error
            raise Exception("url does not exist (HTTP 404): " + url)
        elif response.status_code == 200:
            filePath = saveFolder + f"IGN_WMTS_{str(x)}_{str(y)}.jpeg"
            # Use response content
            print(f"Image received and saved at: {filePath}")
            Image.open(BytesIO(response.content)).save(filePath)
            return filePath
        else:
            # Handle all others http status codes
            raise Exception("url request error: " + url + " . HTTPCode: " + response.status_code)
    
    