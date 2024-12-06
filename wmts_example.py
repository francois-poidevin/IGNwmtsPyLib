from wmts.wmts import Wmts, BoundingBox

if __name__ == "__main__":

    print("Hello IGN!")

    # Instanciate WMTS IGN class
    _wmts = Wmts()

    # Get WMTS IGN capabilties and display
    xmlIGN = _wmts.getCapabilities().getroot()
    print(xmlIGN)

    # Get all available layer in a dictionary
    layers = _wmts.getAvailableLayers()

    # Display all layers informations
    for id in layers:
        print("===")
        layer = layers[id]
        print(layer.toString())

    # Do a request for available level (i.e. 19) of 'ORTHOIMAGERY.ORTHOPHOTOS' for IGN headQuarter geo. pos., then fetch and store image
    try:
        layerName = 'ORTHOIMAGERY.ORTHOPHOTOS'
        bdOrtho = layers[layerName]
        tileMatrixSet = bdOrtho.getTileMatrixSet()
        # Level
        lvl = str(19)
        x, y = _wmts.lat_lon_to_IGN_projection(48.845593, 2.424481,tileMatrixSet, lvl)
        image = _wmts.call_IGN_WMTS(x, y, lvl, tileMatrixSet.getIdentifier(), layerName)
        image.save(f"/tmp/IGN_WTMS_output_{x}_{y}.png")
        print(f"image saved.")
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")

    # Do a request for available level (i.e. 19) of 'ORTHOIMAGERY.ORTHOPHOTOS' with a Toulouse bounding box, then fetch and store images
    try:
        layerName = 'ORTHOIMAGERY.ORTHOPHOTOS'
        bdOrtho = layers[layerName]
        tileMatrixSet = bdOrtho.getTileMatrixSet()
        # Toulouse Capitol square bbox
        lonLatTLSBbox = BoundingBox(1.442606,43.603645,1.445824,43.605215)
        # Level
        lvl = str(19)
        ne_x, ne_y, sw_x, sw_y = _wmts.lat_lon_bbox_to_IGN_projection_bbox(lonLatTLSBbox,tileMatrixSet,lvl)
        imagesDict = _wmts.call_IGN_WMTS_bbox(ne_x, ne_y, sw_x, sw_y, lvl, tileMatrixSet.getIdentifier(), layerName)
        for x in imagesDict:
            for y in imagesDict[x]:
                imagesDict[x][y].save(f"/tmp/IGN_WTMS_outputDict_{x}_{y}.png")
                print(f"image saved.")
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")

    