#!/usr/bin/env python3

import argparse
import colorama
import logging
from lxml import etree
import os
import re
import requests
import runpy

cfg = runpy.run_path('config.nnd_verify.py')

colorama.init(autoreset=True)

logging.basicConfig(
	format = '%(message)s',
	handlers =  [
		logging.FileHandler(cfg['log_filename']),
	],
)

def fetch_data(id):
	"""Fetch video data from the NND API"""

	return requests.get(f'https://ext.nicovideo.jp/api/getthumbinfo/{id}')

def check_connectivity():
	"""Check to see if the NND API can be reached"""

	try:
		fetch_data('sm9')
	except:
		print(colorama.Back.RED + 'Server could not be reached!')
		quit()

def collect_paths(paths):
	"""Create list of files from a list of files and folders, traversing through given folders"""

	collected_paths = []

	for path in paths:
		if os.path.isfile(path):
			collected_paths.append(path)
		elif os.path.isdir(path):
			for dir, subdirs, files in os.walk(path):
				for file in files:
					path = os.path.join(dir, file)
					collected_paths.append(path)

	return collected_paths

def sizes(id):
	"""Given the video ID, return the file sizes retrieved from the NND API"""

	data = fetch_data(id)

	tree = etree.fromstring(data.content)

	size_hq = tree.findall('.//size_high') # find <size_high>
	size_lq = tree.findall('.//size_low') # find <size_low>

	size_hq = int(size_hq[0].text)
	size_lq = int(size_lq[0].text)

	return size_hq, size_lq

def verify_filesize(path):
	"""Verify filesize"""

	matches = re.search('([sn]m\d+).+(mp4|flv|swf)', path)

	if matches:
		id = matches.group(1)

		print('')
		print(colorama.Back.YELLOW + f'The ID "{id}" was detected for the file\n"{path}".')

		size_hq, size_lq = sizes(id)

		size_real = os.stat(path).st_size

		if size_real == size_hq:
			print(colorama.Back.GREEN + f'  OK ({size_real} = {size_hq}, HQ)')
		elif size_real == size_lq:
			print(colorama.Back.MAGENTA + f'  X ({size_real} = {size_lq} != {size_hq}, LQ)')
			logging.warning(f'https://www.nicovideo.jp/watch/{id}') # Write URL to log
		else:
			print(colorama.Back.RED + f'  X ({size_real} != {size_hq} != {size_lq}, neither)')
			logging.warning(f'https://www.nicovideo.jp/watch/{id}')

def main():
	check_connectivity()

	paths = collect_paths(args.paths)

	for path in paths:
		verify_filesize(path)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='For PATH(s), check the file size of Niconico Douga downloads.')
	parser.add_argument(
		'paths',
		metavar='[PATH]...',
		help='Files or folders.',
		nargs='+',
	)
	args = parser.parse_args()

	main()
