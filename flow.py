#! /usr/bin/env python

"""
C:\Program Files\TauDEM\TauDEM5Exe
"""
import argparse, subprocess as sp, os, sys, time, glob, shlex, re

def getArgs():
	parser = argparse.ArgumentParser(
		description = """PyFlow is a pipeline using TauDEM to calculate Flow Accumulation for multiscale elevation output of Surface Analysis Tools"""
	)
	parser.add_argument(
		"-i",
		"--input",
		type = str,
		required = True,
		help = "Input folder containing 1 or more DEM in GeoTiff (.tif) format"
	)
	parser.add_argument(
		"-o",
		"--output",
		type = str,
		required = True,
		help = "Empty output directory where results of TauDEM will be saved"
	)
	parser.add_argument(
		"-e",
		"--executables",
		type = str,
		required = True,
		help = "Path to TauDEM Executables Folder"
	)
	parser.add_argument(
		"-m",
		"--method",
		type = int,
		required = True,
		choices=[0,1],
		help = "Either D-8 (0) or D-Infinity (1) Algorithm. Default is D-Infinity."

	)
	parser.add_argument(
		"-v",
		"--verbose",
		action = "store_true",
		help = "Print status updates while executing"
	)
	return parser.parse_args()

def commandline(cmd, verbose=False):
	if verbose:
		print(cmd)
	#cmd_args = shlex.split(cmd)
	stdout, stderr = sp.Popen(
		cmd,
		stdin = sp.PIPE,
		stdout = sp.PIPE,
		stderr = sp.PIPE
	).communicate()
	if verbose:
		print stdout, stderr
	return True

def rmPits(cmd_dict):
	cmd = "{exec}\\PitRemove.exe -z {input}\\{file} -fel {output}\\rmpit\\{file}".format(
		**cmd_dict
	)
	commandline(cmd)
	return True	

def flowdir(cmd_dict):
	if cmd_dict['method']==0:
		cmd = "{exec}\\D8FlowDir.exe -fel {output}\\rmpit\\{file} -sd8 \
{output}\\slope\\slope{scale}.tif -p {output}\\fd\\fd{scale}.tif".format(**cmd_dict)
	else:
		cmd = "{exec}\\DinfFlowDir.exe -fel {output}\\rmpit\\{file} -slp\
 {output}\\slope\\slope{scale}.tif -ang {output}\\fd\\fd{scale}.tif".format(**cmd_dict)
 	commandline(cmd)
 	return True

def area(cmd_dict):
	if cmd_dict['method']==0:
		cmd = "{exec}\\AreaD8.exe -p {output}\\fd\\fd{scale}.tif -ad8 \
{output}\\fa\\fa{scale}.tif".format(**cmd_dict)
	else:
		cmd = "{exec}\\AreaDinf.exe -ang {output}\\fd\\fd{scale}.tif\
 -sca {output}\\fa\\fa{scale}.tif".format(**cmd_dict)
 	commandline(cmd)
 	return True

def mkdir(dir):
	try:
		os.mkdir(dir)
		return True
	except:
		return False

def driver(args):
	base = os.getcwd()
	os.chdir(args.input)
	files = glob.glob("*.tif")
	os.chdir(base)
	# Make directories for output files
	os.chdir(args.output)
	# intermediate files
	mkdir("rmpit")
	mkdir("fd")
	mkdir("slope")
	mkdir("fa")
	
	os.chdir(base)
	# run for each file at each scale
	for f in files:
		if args.verbose:
			print("Processing file {}...".format(f))
		scale = re.findall(r'\d+', f)[0]
		cmd_dict = {
			'exec':args.executables,
			'input':args.input,
			'output':args.output,
			'file':f,
			'scale':scale,
			'method':args.method
		}
		rmPits(cmd_dict)
		flowdir(cmd_dict)
		area(cmd_dict)
	return True

def main():
	t_i = time.time()
	args = getArgs()
	driver(args)
 	t_f = time.time()
 	if args.verbose:
 		print("Total elapsed time was {} s".format((t_f-t_i)/60.))

if __name__ == "__main__":
	main()