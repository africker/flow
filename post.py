#! /usr/bin/env python

"""
Post process flow accumulation raster to fill areas where pits are located
with the maximum value for flow accumulation.
"""

import os, glob, re, sys
try:
	import numpy as np
	from numpy.linalg import inv
	import gdal
	from gdalconst import *
	from osgeo import osr
except ImportError:
	print("One or more libraries required for post processing output of flow.py was not found.")
	print("Check that all dependencies are installed.")
	sys.exit(1)

def getArgs():
	parser = argparse.ArgumentParser(
		description="Surface analysis of a DEM"
	)
	parser.add_argument(
		"-d",
		"--dem",
		required=True,
		type=str,
		help= "Directory with DEMs"
	)
	parser.add_argument(
		"-f",
		"--flowaccum",
		required=True,
		type = str,
		help = "Directory with flow accumulation models"
	)
	parser.add_argument(
		"-o",
		"--output",
		required =True,
		type = str,
		help = "Directory for processed flow accumulation files"
	)
	parser.add_argument(
		"-v",
		"--verbose",
		action = "store_true",
		help = "Print status updates while executing"
	)
	return parser.parse_args()

class Raster(object):
	def __init__(self, args=None):
		self.args = args

	def read(self, infile):
		# never want to change the original input raster so use read only constant
		self.infile = infile
		self.raster = gdal.Open(self.infile, GA_ReadOnly)
		self.band = self.raster.GetRasterBand(1)
		self.NDV = self.band.GetNoDataValue()
		self.x = self.band.XSize
		self.y = self.band.YSize
		DataType = self.band.DataType
		self.DataType = gdal.GetDataTypeName(DataType)
		self.GeoT = self.raster.GetGeoTransform()
		# Problem
		self.prj = osr.SpatialReference()
		self.prj.ImportFromWkt(self.raster.GetProjectionRef())


	def getArray(self):
		self.array = self.band.ReadAsArray()
		self.array[self.array==self.NDV]=np.nan
		return self.array

	def getTiles(self, dim=100):
		# dim is side length of tile.
		# default dim is 100 x 100 pixel tiles
		# Get indexing arrays
		# considering rows as gy and columns as gx
		shape = self.array.shape
		self.gy, self.gx = np.indices(shape)
		tiles = []
		i,j = 0,0
		while i <= shape[0]:
			while j <= shape[1]:
				gx = self.gx[i:i+dim,j:j+dim]
				gy = self.gy[i:i+dim,j:j+dim]
				tile = [gy,gx]
				tiles.append(tile)
				j += dim
			j = 0
			i += dim
		return tiles

	def write(self, array, name):
		self.name = name
		driver= gdal.GetDriverByName("GTiff")
		if self.DataType == "Float32":
			#print gdal.GDT_Float32
			self.DataType = gdal.GDT_Float32
		self.outdata = array
		self.outdata[np.isnan(self.outdata)] = self.NDV
		# Create output file
		band = 1
		DataSet = driver.Create(self.name, self.x, self.y, 
			band, self.DataType)
		DataSet.SetGeoTransform(self.GeoT)
		DataSet.SetProjection(self.prj.ExportToWkt())
		# Write data array
		DataSet.GetRasterBand(1).WriteArray(self.outdata)
		DataSet.GetRasterBand(1).SetNoDataValue(self.NDV)
		DataSet = None

	def close(self):
		self.raster = None
		self.band = None

def arrayProcess(dem, fa):
	output = fa.copy()
	output[np.isnan(dem)!=np.isnan(fa)]=max(fa)
	return output


def driver(args, files, verbose=False):
	for scale, f in files.iteritems():
		if verbose:
			print("Processing {} scale...".format(scale))
		# dem
		dem = Raster()
		dem_path = os.path.join(args.dem,f["dem"])
		dem.read(dem_path)
		dem_data = dem.getArray()
		# flow accumulation
		fa = Raster()
		fa.read(f["fa"])
		fa_data = fa.getArray()
		# process
		output = arrayProcess(dem_data, fa_data)
		output_path = os.join.path(args.output, f["fa"])
		dem.write(output, output_path)
		dem.close()
		fa.close()
	return True


def main():
	t_i = time.time()
	args = getArgs()

	base = os.getcwd()
	os.chdir(args.dem)
	dems = glob.glob("*.tif")
	files = {}
	for dem in dems:
		scale = re.findall(r'\d+', dem)[0]
		files[scale]={'dem':dem}
	os.chdir(base)
	os.chdir(args.flowaccum)
	flowaccums = glob.glob("*.tif")
	for fa in flowaccums:
		scale = re.findall(r'\d+', fa)[0]
		files[scale]['fa']=fa
	os.chdir(base)
	driver(args, files, args.verbosep)

	t_f = time.time()
	print("Total elapsed time is {} s".format((t_f-t_i)/60.))


if __name__ == "__main__":
	main()