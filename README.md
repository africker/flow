Introduction
------------

Flow is a python pipeline that uses the Windows executables of Terrain Analysis Using Digital Elevation Models (<a href="http://hydrology.usu.edu/taudem/taudem5/index.html">TauDEM</a>) to calculate flow accumulation for the multiscale elevation output of <a href="https://github.com/jeffreywolf/surface">Surface Analysis Tools (e.g. surface.py)</a>. <a href="http://hydrology.usu.edu/taudem/taudem5/index.html">TauDEM</a> is a fast parallel implementation of a large suite of hydrology tools. This wrapper facilitates calculation of Flow Accumulation using either the D8 or the D-infinity algorithm (Tarboton) at multiple spatial scales. 

Notes
-----
<a href="http://hydrology.usu.edu/taudem/taudem5/downloads.html">Download the TauDEM tools for ArcGIS 10</a>.  

All you need to use them outside ArcGIS is the path to the executable folder. For version 5, the subfolder is labelled TauDEM5Exe.


References
----------
http://hydrology.usu.edu/taudem/taudem5/index.html

Tarboton DG. 1997. A new method for the determination of flow directions and contributing areas in grid digital elevation models. Water Resources Research 33(2):309-319.

Tesfa TK, Tarboton DG, Watson DW, Schreuders KAT, Baker ME, Wallace RM. 2011. Extracting hydrological proximity measures from DEMs using parallel processing. Environmental Modelling and Software 26(12): 1696-1706. http://dx.doi.org/10.1016/j.envsoft.2011.07.018
