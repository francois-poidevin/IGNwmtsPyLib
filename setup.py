from distutils.core import setup
setup(name='IGNwmtsPyLib',
      version='1.1',
      description='Provide a python library for using IGN WMTS web service.',
      author='Francois Poidevin Merdrignac',
      author_email='francois.poidevin@yahoo.fr',
      packages=['wmts'],
      install_requires=['pyproj','pillow','requests'],
      )