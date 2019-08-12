#!/usr/bin/env python3

import argparse
import colorama
import json
import os
import re
import urllib3
import runpy

cfg = runpy.run_path('config.vocadb_tag.py')

dbs = {
	'vocadb': 'VocaDB',
	'utaitedb': 'UtaiteDB',
}

service_regexes = {
	'NicoNicoDouga': '(?:nicovideo\.jp/watch/)?([sn]m\d+)',
	'SoundCloud': '(?:soundcloud\.com/)([a-z0-9_-]+/[a-z0-9_-]+)',
	'Youtube': '(?:youtube\.com/watch\?v=|youtu\.be/)?([A-Za-z0-9_-]{11})',
}

service_urls = {
	'NicoNicoDouga': 'https://www.nicovideo.jp/watch/{}',
	'SoundCloud': 'https://soundcloud.com/{}',
	'Youtube': 'https://www.youtube.com/watch?v={}',
}

def service_id_function_soundcloud(pv_id):
	""""""

	import youtube_dl

	try:
		ytdl = youtube_dl.YoutubeDL()
		ytdl_info = ytdl.extract_info(
			service_urls['SoundCloud'].format(pv_id),
			download = False,
		)
	except:
		return ""
	else:
		return ytdl_info.get('id') + ' ' + pv_id

# convert $pv_id to VocaDB PV ID
to_vocadb_pv_id = {
	'SoundCloud': service_id_function_soundcloud
}

# convert VocaDB PV ID to $pv_id
from_vocadb_pv_id = {
	'SoundCloud': lambda x:re.search('([a-z0-9_-]+/[a-z0-9_-]+)', x).group(1), # leave the latter part (not the numeric id)
}

api_urls_add_pv = {
	'VocaDB': 'https://vocadb.net/Song/Create?PVUrl={}',
	'UtaiteDB': 'https://utaitedb.net/Song/Create?PVUrl={}',
}

user_agent = 'vocadb_tag.py (https://vocadb.net/Profile/u126)'

file_extensions = ('.mp3', '.m4a', '.ogg')

colorama.init(autoreset = True)

http = urllib3.PoolManager(
	headers = {
		'user-agent': user_agent,
	}
)

def main(args):
	#check_connectivity()

	write_mp3tag_format_string()

	# tentative
	open(cfg['tags_output_file'], mode='w', encoding='utf-8').close()
	if cfg['bom']:
		with open(cfg['tags_output_file'], mode='a', encoding='utf-8') as file:
			file.write('\ufeff') # bom, for mp3tag
			file.write('\n')

	for path in collect_paths(args.paths):
		write_tags(path)
		print()

def check_connectivity():
	"""
	Check to see if the VocaDB API can be reached.
	"""

	try:
		fetch_data('NicoNicoDouga', 'sm3186850')
	except:
		print(colorama.Fore.RED + 'Server could not be reached!')
		quit()

def write_mp3tag_format_string():
	with open(cfg['formatstring_output_file'], mode='w', encoding='utf-8') as file:
		format_string = []

		for field in cfg['metadata_tags']:
			format_string.append('%{}%'.format(field.lower()))

		file.write(cfg['tags_output_file_tag_delimiter'].join(format_string) + '\n')

def collect_paths(paths):
	"""
	Create a list of files from an Array of files and folders. Folders are scanned for certain file types.
	"""

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

def write_tags(path):
	""""""

	print(colorama.Fore.CYAN + path + ':')

	metadata = generate_metadata(path)

	if metadata is None:
		return None # vocadb has no data

	print(colorama.Fore.GREEN + 'Entry found!')
	print(
		colorama.Fore.CYAN +
		metadata['title'] +
		colorama.Fore.RESET +
		' - ' +
		colorama.Fore.CYAN +
		', '.join(metadata['producers']) + ' feat. ' +
		', '.join(metadata['vocalists']) +
		colorama.Fore.RESET +
		' | ' +
		'https://' + metadata['x_db'] + '.net/S/' + str(metadata['x_db_id'])
	)

	def metadata_returner(x):
		metadata_value = metadata[x.group(1)]

		if type(metadata_value) is list:
			metadata_value = cfg['metadata_multi_value_delimiter'].join(metadata_value)
		elif type(metadata_value) is int:
			metadata_value = str(metadata_value)
		elif type(metadata_value) is dict:
			# XXX
			temp = ""
			for key in metadata_value:
				if metadata_value[key]:
					temp += key + '+'
			metadata_value = temp

		if metadata_value == '':
			return cfg['metadata_empty_placeholder']

		return metadata_value

	with open(cfg['tags_output_file'], mode='a', encoding='utf-8') as file:
		metadata_values = []

		for field in cfg['metadata_tags']:
			metadata_value = re.sub('\$([a-z_]+)', metadata_returner, cfg['metadata_tags'][field]) # pattern, repl, string
			metadata_values.append(metadata_value)

		file.write(cfg['tags_output_file_tag_delimiter'].join(metadata_values) + '\n')

def generate_metadata(path):
	"""
	Generate metadata for a song.

	Args:
		path:
	"""

	db, request, service, pv_id = get_song_data(path)
	if not request:
		return None

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
		'x_urls': [],
	}

	metadata['x_db'] = db
	metadata['x_db_name'] = dbs[db]
	metadata['x_db_id'] = request['id']

	metadata['x_filename_ext'] = os.path.basename(path)
	metadata['x_path'] = path

	metadata['title'] = request['name']

	metadata['song_type'] = request['songType']

	if 'publishDate' in request:
		metadata['publish_date'] = request['publishDate']

		metadata['year'] = metadata['publish_date'][0:4] # it just werks

	if service in from_vocadb_pv_id:
		pv_id = from_vocadb_pv_id[service](pv_id)

	if pv_id:
		metadata['url'] = service_urls[service].format(pv_id)

	for pv in request['pvs']:
		if pv['pvType'] == 'Original':
			metadata['x_urls'].append(pv['url'])
		elif pv['pvId'] == pv_id:
			print(colorama.Fore.YELLOW + 'Have you downloaded a reprint?')

	for artist in request['artists']:
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

def get_song_data(path):
	""""""

	service = None
	pv_id = None
	ffprobe_output = None

	print('Examining path for PV ID:')
	for service in service_regexes:
		matches = re.search(service_regexes[service], path)

		if matches:
			pv_id = matches.group(1)
			print(f'o {service} | {pv_id}')
			db, request = query_api_song_by_pv(service, pv_id)
			if request:
				return db, request, service, pv_id
		else:
			print(f'x {service}')

	if cfg['ffprobe'] != False:
		import subprocess
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

		print('Examining tags for PV ID:')
		for service in service_regexes:
			matches = re.search('http.+' + service_regexes[service] + '.*', ffprobe_output)

			if matches:
				pv_id = matches.group(1)
				print(f'o {service} | {pv_id} | {matches.group(0)}')
				db, request = query_api_song_by_pv(service, pv_id)
				if request:
					return db, request, service, pv_id
			else:
				print(f'x {service}')

		print('Examining tags for title and artist:')
		matches = re.search('(?:title)=([^/\n]+)', ffprobe_output)
		if matches:
			title = matches.group(1)
			print("title | " + title)
			matches = re.search('(?:artist)=([^/\n]+)', ffprobe_output)
			if matches:
				artist = matches.group(1)
				print("artist | " + artist)
			else:
				artist = None
			db, request = query_api_song_by_search(title, artist)
			if request:
				return db, request, None, None

	print(colorama.Fore.RED + 'Entry not found!')
	return None, None, None, None

def get_ffprobe_path():
	""""""

	if cfg['ffprobe'] == True:
		# https://stackoverflow.com/q/9877462
		#from distutils.spawn import find_executable
		#return find_executable('ffprobe')
		return 'ffprobe'
	else:
		return cfg['ffprobe']

def query_api(db, operation, parameters):
	"""
	Query the *DB API.

	Args:
		db: The database name.
		operation: The API operation.
		parameters: The parameters (Dict).

	"""

	request = http.request(
		'GET',
		'https://' + db + '.net/api/' + operation,
		fields = parameters,
	)

	if not request.data == b'null':
		return json.loads(request.data)

	return None

def query_api_artist_by_search(artist):
	"""
	Query the *DB API for an artist.

	Args:
		artist: The artist.
	"""

	for db in dbs:
		request = query_api(
			db,
			'artists',
			{
				'query': artist,
			}
		)
		if request:
			if request['items']:
				return db, request['items'][0]

def query_api_song_by_search(title, artist):
	"""
	Query the *DB API for an artist.

	Args:
		title: The title.
		artist: (optional) The artist.
	"""

	artist_id = None
	if artist:
		db, request = query_api_artist_by_search(artist)
		if request:
			artist_id = request['id']

	for db in dbs:
		request = query_api(
			db,
			'songs',
			{
				'query': title,
				'fields': 'Artists,PVs',
				'artistId': artist_id,
			}
		)
		if request:
			if request['items']:
				return db, request['items'][0]

def query_api_song_by_pv(service, pv_id):
	"""
	Query the *DB API for a song, given a service and PV ID.

	Args:
		service: The PV service.
		pv_id: The PV ID.
	"""

	pv_id_original = pv_id # for soundcloud

	if service in to_vocadb_pv_id:
		pv_id = to_vocadb_pv_id[service](pv_id)

	for db in dbs:
		request = query_api(
			db,
			'songs/byPv',
			{
				'pvService': service,
				'pvId': pv_id,
				'fields': 'Artists,PVs',
				'lang': cfg['language'],
			}
		)

		if request:
			return db, request

	print(colorama.Fore.RED + 'Could not find a matching entry for this PV!')
	print('Add it?')
	for db in api_urls_add_pv:
		print(api_urls_add_pv[db].format(
			service_urls[service].format(pv_id_original)
		))

	return None, None

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
