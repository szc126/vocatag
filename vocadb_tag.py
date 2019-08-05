#!/usr/bin/env python3

import argparse
import colorama
import json
import os
import re
import requests
import runpy

cfg = runpy.run_path('config.vocadb_tag.py')

service_regexes = {
	'NicoNicoDouga': '([sn]m\d+)',
	'SoundCloud': '([0-9]+ [a-z0-9-]+/[a-z0-9-]+)', # not sure what program would output files like this
	'Youtube': '([A-Za-z0-9_-]{11})',
}

service_urls = {
	'NicoNicoDouga': 'https://www.nicovideo.jp/watch/{}',
	'SoundCloud': 'https://soundcloud.com/{}',
	'Youtube': 'https://www.youtube.com/watch?v={}',
}

service_url_functions = {
	'SoundCloud': lambda x:re.search('([a-z0-9_-]+/[a-z0-9_-]+)', x).group(1), # leave the latter part (not the numeric id)
}

api_urls_song_by_pv = {
	'VocaDB': 'https://vocadb.net/api/songs/byPv?pvService={}&pvId={}&fields=Artists&lang={}',
	'UtaiteDB': 'https://utaitedb.net/api/songs/byPv?pvService={}&pvId={}&fields=Artists&lang={}',
}

api_urls_add_pv = {
	'VocaDB': 'https://vocadb.net/Song/Create?PVUrl={}',
	'UtaiteDB': 'https://utaitedb.net/Song/Create?PVUrl={}',
}

user_agent = 'vocadb_tag.py (https://vocadb.net/Profile/u126)'

file_extensions = ('.mp3', '.m4a', '.ogg')

colorama.init(autoreset=True)

def fetch_data(service, pv_id):
	"""Fetch PV data from the VocaDB/UtaiteDB API"""

	for db in api_urls_song_by_pv:
		response = requests.get(
			api_urls_song_by_pv[db].format(service, pv_id, cfg['language']),
			headers = {
				'user-agent': user_agent,
			},
		)

		if not response.content == b'null':
			print(colorama.Fore.GREEN + 'Entry found!')
			return db, response
			break

	print(colorama.Fore.RED + 'Entry not found!')
	print('Add it?')
	for db in api_urls_add_pv:
		print(api_urls_add_pv[db].format(
			service_urls[service].format(pv_id)
		))

	return None, None

def check_connectivity():
	"""Check to see if the VocaDB API can be reached"""

	try:
		fetch_data('NicoNicoDouga', 'sm26661454')
	except:
		print(colorama.Fore.RED + 'Server could not be reached!')
		quit()

def generate_metadata(service, pv_id, path):
	"""Parse and rearrange the data from the VocaDB API"""

	db, api_data = fetch_data(service, pv_id)

	if api_data is None:
		return None

	api_data = json.loads(api_data.content)

	metadata = {
		'title': None,
		'song_type': None,
		'publish_date': None, 'year': None,
		'producers': [],
		'vocalists': [],
		'url': [],

		# meta-metadata
		'x_db': None,
		'x_db_id': None,
		'x_synthesizers': {
			'vocaloid': None,
			'utau': None,
			'cevio': None,
			'other_synthesizer': None,
			'actual_human_people': None,
		},
	}

	metadata['x_db'] = db

	metadata['x_db_id'] = api_data['id']

	metadata['x_path'] = path

	metadata['title'] = api_data['name']

	metadata['song_type'] = api_data['songType']

	if 'publishDate' in api_data:
		metadata['publish_date'] = api_data['publishDate']

		metadata['year'] = metadata['publish_date'][0:4] # it just werks

	if service in service_url_functions:
		pv_id = service_url_functions[service](pv_id)

	metadata['url'] = service_urls[service].format(pv_id)

	for artist in api_data['artists']:
		#print(artist)
		#print()

		if not 'artist' in artist: # custom artist
			pass
		elif artist['artist']['artistType'] == 'Vocaloid':
			metadata['x_synthesizers']['vocaloid'] = True
			metadata['vocalists'].append(artist['name'])
		elif artist['artist']['artistType'] == 'UTAU':
			metadata['x_synthesizers']['utau'] = True
			metadata['vocalists'].append(artist['name'])
		elif artist['artist']['artistType'] == 'CeVIO':
			metadata['x_synthesizers']['cevio'] = True
			metadata['vocalists'].append(artist['name'])
		elif artist['artist']['artistType'] == 'OtherVoiceSynthesizer':
			metadata['x_synthesizers']['other_synthesizer'] = True
			metadata['vocalists'].append(artist['name'])
		elif ('Vocalist' in artist['roles']) or ('Vocalist' in artist['categories'] and 'Default' in artist['roles']): # what's the difference between 'roles' and 'effectiveRoles'
			metadata['x_synthesizers']['actual_human_people'] = True
			metadata['vocalists'].append(artist['name'])

		elif 'Composer' in artist['roles']:
			metadata['producers'].append(artist['name'])

		elif 'Default' in artist['roles'] and 'Producer' in artist['categories']:
			metadata['producers'].append(artist['name'])

	return metadata

def get_ffprobe_path():
	if cfg['ffprobe'] == True:
		# https://stackoverflow.com/q/9877462
		from distutils.spawn import find_executable
		return find_executable('ffprobe')
	else:
		return cfg['ffprobe']

def determine_service_and_pv_id(path):
	"""Determine the service and PV ID"""

	print(colorama.Fore.BLUE + path + ':')

	print('Examining path:')
	for service in service_regexes:
		matches = re.search(service_regexes[service], path)

		if matches:
			pv_id = matches.group(1)
			print(f'o {service} | {pv_id}')
			return service, pv_id
			break
		else:
			print(f'x {service}')

	if cfg['ffprobe'] != False:
		import subprocess
		print('Examining tags:')
		ffprobe_output = subprocess.check_output(
			[
				get_ffprobe_path(),
				'-show_format',
				'-v', 'quiet',
				#'-print_format', 'json',
				'-print_format', 'default',
				'-show_streams', # .ogg, https://trac.ffmpeg.org/ticket/4224
				path,
			],
		)
		ffprobe_output = str(ffprobe_output, 'UTF-8')
		#ffprobe_output = json.loads(ffprobe_output)
		# XXX: hot garbage
		#print(ffprobe_output)
		for service in service_regexes:
			matches = re.search('http.+(?:nicovideo|youtube).+' + service_regexes[service] + '.*', ffprobe_output)

			if matches:
				pv_id = matches.group(1)
				print(f'o {service} | {pv_id} | {matches.group(0)}')
				return service, pv_id
				break
			else:
				print(f'x {service}')

	print(colorama.Fore.RED + 'Could not find a PV ID.')
	return None, None # path did not match any service urls

def write_tags(path):
	"""Given the file path, write tags"""

	service, pv_id = determine_service_and_pv_id(path)

	if service is None:
		return None # path did not match any service urls

	metadata = generate_metadata(service, pv_id, path)

	if metadata is None:
		return None # vocadb has no data

	def metadata_returner(x):
		metadata_value = metadata[x.group(1)]
		if type(metadata_value) is list:
			metadata_value = cfg['metadata_multi_value_delimiter'].join(metadata_value)
		elif type(metadata_value) is int:
			metadata_value = str(metadata_value)
		return metadata_value

	with open(cfg['tags_output_file'], mode='a', encoding='utf-8') as file:
		metadata_values = []

		for field in cfg['metadata_tags']:
			metadata_value = re.sub('\$([a-z_]+)', metadata_returner, cfg['metadata_tags'][field]) # pattern, repl, string
			metadata_values.append(metadata_value)

		file.write(cfg['tags_output_file_tag_delimiter'].join(metadata_values) + '\n')

def write_mp3tag_format_string():
	with open(cfg['formatstring_output_file'], mode='w', encoding='utf-8') as file:
		format_string = []

		for field in cfg['metadata_tags']:
			format_string.append('%{}%'.format(field.lower()))

		file.write(cfg['tags_output_file_tag_delimiter'].join(format_string) + '\n')

def collect_paths(paths):
	"""Create list of files from a list of files and folders, traversing through given folders"""

	collected_paths = []

	for path in paths:
		if os.path.isfile(path):
			collected_paths.append(path)
		elif os.path.isdir(path):
			for dir, subdirs, files in os.walk(path):
				for file in files:
					if file.endswith(file_extensions):
						path = os.path.join(dir, file)
						collected_paths.append(path)

	return collected_paths

def main(args):
	#check_connectivity()

	write_mp3tag_format_string()

	# tentative
	with open(cfg['tags_output_file'], mode='w', encoding='utf-8') as file:
		file.write('\ufeff') # bom, for mp3tag

	for path in collect_paths(args.paths):
		write_tags(path)
		print()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='For PATH(s), retrieve song metadata from VocaDB or UtaiteDB.')
	parser.add_argument(
		'paths',
		metavar='[PATH]...',
		help='Files or folders. Folders will be scanned for certain file ' +
			'types: ' + ' '.join(file_extensions),
		nargs='+'
	)
	args = parser.parse_args()

	main(args)
