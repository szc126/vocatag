#!/usr/bin/env python3

import collections
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
	'NicoNicoDouga': 'http://www.nicovideo.jp/watch/{}',
	'SoundCloud': 'http://soundcloud.com/{}',
	'Youtube': 'https://www.youtube.com/watch?v={}',
}

service_url_functions = {
	'SoundCloud': lambda x:re.search('([a-z0-9_-]+/[a-z0-9_-]+)', x).group(1) # leave the latter part (not the numeric id)
}

db_urls = {
	'VocaDB': 'http://vocadb.net/api/songs/byPv?pvService={}&pvId={}&fields=Artists&lang={}',
	'UtaiteDB': 'http://utaitedb.net/api/songs/byPv?pvService={}&pvId={}&fields=Artists&lang={}'
}

user_agent = 'vocadb_tag.py (https://vocadb.net/Profile/u126)'

file_extensions = ('.mp3', '.m4a', '.ogg')

colorama.init(autoreset=True)

def fetch_data(service, id):
	"""Fetch PV data from the VocaDB/UtaiteDB API"""

	for db in db_urls:
		response = requests.get(
			db_urls[db].format(service, id, cfg['LANGUAGE']),
			headers = {
				'user-agent': user_agent,
			},
		)

		if not response.content == b'null':
			return db, response
			break

	print(colorama.Back.RED + f'The video \'{id}@{service}\' is not registered on VocaDB or UtaiteDB!')
	return None, None

def check_connectivity():
	"""Check to see if the NND API can be reached"""

	try:
		fetch_data('NicoNicoDouga', 'sm26661454')
	except:
		print(colorama.Back.RED + 'Server could not be reached!')
		quit()

def generate_metadata(service, id):
	"""Parse and rearrange the data from the VocaDB API"""

	db, api_data = fetch_data(service, id)

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

	metadata['title'] = api_data['name']

	metadata['song_type'] = api_data['songType']

	if 'publishDate' in api_data:
		metadata['publish_date'] = api_data['publishDate']

		metadata['year'] = metadata['publish_date'][0:4] # it just werks

	if service in service_url_functions:
		id = service_url_functions[service](id)

	metadata['url'] = service_urls[service].format(id)

	for artist in api_data['artists']:
		# print(artist)
		# print()

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

def determine_service_and_id(path):
	"""Test path against regexes to determine the service and PV ID"""

	for service in service_regexes:
		matches = re.search(service_regexes[service], path)

		if matches:
			return service, matches.group(1)
			break
		else:
			print(f'{path} is not {service}')

	return None, None # path did not match any service urls

def tag_file(path):
	"""Given the file path, write lines for mp3tag"""

	service, id = determine_service_and_id(path)

	if service is None:
		return None # path did not match any service urls

	print(id)

	metadata = generate_metadata(service, id)

	if metadata is None:
		return None # vocadb has no data

	def metadata_returner(x):
		metadata_value = metadata[x.group(1)]
		if type(metadata_value) is list:
			metadata_value = cfg['METADATA_DELIMITER'].join(metadata_value)
		elif type(metadata_value) is int:
			metadata_value = str(metadata_value)
		return metadata_value

	with open(cfg['OUTPUT_FILE'], mode='a', encoding='utf-8') as file:
		metadata_values = [path]

		for field in cfg['METADATA_FORMAT']:
			metadata_value = re.sub('\$([a-z_]+)', metadata_returner, cfg['METADATA_FORMAT'][field]) # pattern, repl, string
			metadata_values.append(metadata_value)

		file.write(cfg['OUTPUT_DELIMITER'].join(metadata_values) + '\n')

def write_mp3tag_format_string():
	with open(cfg['FORMATSTRING_OUTPUT_FILE'], mode='w', encoding='utf-8') as file:
		format_string = ['%_filename_ext%']

		for field in cfg['METADATA_FORMAT']:
			format_string.append('%{}%'.format(field.lower()))

		file.write(cfg['OUTPUT_DELIMITER'].join(format_string) + '\n')

def main(args):
	check_connectivity()

	write_mp3tag_format_string()

	# tentative
	with open(cfg['OUTPUT_FILE'], mode='w', encoding='utf-8') as file:
		file.write('\ufeff') # bom, for mp3tag

	for dir, subdirs, files in os.walk(args.FOOBAR):
		for file in files:
			if file.endswith(file_extensions):
				tag_file(file)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='LOREM IPSUM DOLOR SIT AMET')
	parser.add_argument('FOOBAR', help='LOREM IPSUM DOLOR SIT AMET', metavar='LOREM IPSUM DOLOR SIT AMET')
	args = parser.parse_args()

	main(args)
