#!/usr/bin/env python3

import argparse
import colorama
import json
import os
import re
import urllib3
import runpy

# https://stackoverflow.com/a/53222876
cfg = os.path.join(
	(
		os.environ.get('APPDATA') or
		os.environ.get('XDG_CONFIG_HOME') or
		os.path.join(os.environ['HOME'], '.config') or
		"./config"
	),
	"vocadb_tag.py"
)
cfg = runpy.run_path(cfg)

servers = {
	'https://vocadb.net': 'VocaDB',
	'https://utaitedb.net': 'UtaiteDB',
}

service_regexes = {
	'NicoNicoDouga': '(?:watch/)?([sn]m\d+)',
	'SoundCloud': '(?:soundcloud\.com/)([a-z0-9_-]+/[a-z0-9_-]+)',
	'Youtube': '(?:[?&]v=|youtu\.be/)?([A-Za-z0-9_-]{11})',
}

service_urls = {
	'NicoNicoDouga': 'https://www.nicovideo.jp/watch/{}',
	'SoundCloud': 'https://soundcloud.com/{}',
	'Youtube': 'https://www.youtube.com/watch?v={}',
}

def service_id_function_soundcloud(pv_id):
	""""""

	import yt_dlp

	try:
		ytdl = yt_dlp.YoutubeDL()
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

file_extensions = ('.mp3', '.m4a', '.ogg')

colorama.init(autoreset = True)

http = urllib3.PoolManager(
	headers = {
		'user-agent': 'vocadb_tag.py (https://vocadb.net/Profile/u126)',
	}
)

def main(args):
	""""""

	#check_connectivity()

	write_format_string()

	# tentative
	open(cfg['tags_output_file'], mode = 'w', encoding = 'utf-8').close()
	if cfg['bom']:
		with open(cfg['tags_output_file'], mode = 'a', encoding = 'utf-8') as file:
			file.write('\ufeff') # bom, for mp3tag
			file.write('\n')

	for path in collect_paths(args.paths):
		write_tags(path)
		print()

def check_connectivity():
	"""
	Check to see if the VocaDB API can be reached. Quit on failure.
	"""

	try:
		fetch_data('NicoNicoDouga', 'sm3186850')
	except:
		print(colorama.Fore.RED + 'Server could not be reached!')
		quit()

def write_format_string():
	"""
	Write the format string to a text file.
	"""

	with open(cfg['formatstring_output_file'], mode = 'w', encoding = 'utf-8') as file:
		format_string = []

		for field in cfg['metadata_tags']:
			format_string.append('%{}%'.format(field.lower()))

		file.write(cfg['tags_output_file_tag_delimiter'].join(format_string))

def collect_paths(paths):
	"""
	Create a list of files from an Array of files and folders. Folders are scanned for certain file types.

	Args:
		paths: Paths to files and/or folders (Array).

	Returns:
		Paths to music files (Array).
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

	return sorted(collected_paths)

def write_tags(path):
	"""
	Write tags for a song to a text file.

	Args:
		path: A path to a song.
	"""

	print(colorama.Fore.CYAN + path + ':')

	metadata = generate_metadata(path)

	# search failed
	if metadata is None:
		with open(cfg['tags_output_file'], mode = 'a', encoding = 'utf-8') as file:
			file.write('\n')
		return None

	print(colorama.Fore.GREEN + 'Entry found!')
	print(
		colorama.Fore.CYAN +
		metadata['title'] +
		colorama.Fore.RESET +
		' - ' +
		colorama.Fore.CYAN +
		', '.join(metadata['composers']) + ' feat. ' +
		', '.join(metadata['vocalists']) +
		colorama.Fore.RESET +
		' | ' +
		metadata['x_db'] + '/S/' + str(metadata['x_db_id'])
	)

	# XXX
	def to_tag_string(x):
		if type(x) is list:
			x = cfg['metadata_multi_value_delimiter'].join(x)
		elif type(x) is int:
			x = str(x)
		elif type(x) is dict:
			x = x.keys()
			x = cfg['metadata_multi_value_delimiter'].join(x)

		if x == '':
			x = cfg['metadata_empty_placeholder']

		return x

	# XXX
	#for k in metadata:
		#metadata[k] = to_tag_string(metadata[k]))

	def metadata_returner(x):
		return to_tag_string(metadata[x.group(1)])

	with open(cfg['tags_output_file'], mode = 'a', encoding = 'utf-8') as file:
		metadata_values = []

		for field in cfg['metadata_tags']:
			if callable(cfg['metadata_tags'][field]):
				metadata_value = cfg['metadata_tags'][field](metadata)
			else:
				metadata_value = re.sub('\$([a-z_]+)', metadata_returner, cfg['metadata_tags'][field]) # pattern, repl, string
			metadata_values.append(metadata_value)

		file.write(cfg['tags_output_file_tag_delimiter'].join(metadata_values) + '\n')

def generate_metadata(path):
	"""
	Generate metadata for a song.

	Args:
		path: A path to a song.

	Returns:
		Metadata (Dict).

		Nothing, (None) if metadata could not be generated.
	"""

	server, request, pv_index, detection_method = get_song_data(path)
	if not request:
		return None

	# "is not None": 0 is falsy
	service = request['pvs'][pv_index]['service'] if pv_index is not None else None
	pv_id = request['pvs'][pv_index]['pvId'] if pv_index is not None else None
	uploader = request['pvs'][pv_index]['author'] if pv_index is not None else None

	metadata = {
		'title': None,
		'song_type': None,
		'date': None,
		'year': None,
		'composers': [],
		'arrangers': [],
		'band': [],
		'vocalists': [],
		'vocalists_support': [],
		'url': [],
		'uploader': None,

		# meta-metadata
		'x_db': None,
		'x_db_id': None,
		'x_vocalist_types': {},
		'x_urls': [],
		'x_detection_method': detection_method,
		'x_is_reprint': None,
	}

	metadata['x_db'] = server
	metadata['x_db_name'] = servers[server]
	metadata['x_db_id'] = request['id']

	metadata['x_filename_ext'] = os.path.basename(path)
	metadata['x_path'] = path

	metadata['title'] = request['name']

	metadata['song_type'] = request['songType']

	if 'publishDate' in request:
		metadata['date'] = request['publishDate']

		metadata['year'] = request['publishDate'][0:4] # it just werks

	if service in from_vocadb_pv_id:
		pv_id = from_vocadb_pv_id[service](pv_id)

	if pv_id:
		metadata['url'] = service_urls[service].format(pv_id)
		metadata['uploader'] = uploader

	for pv in request['pvs']:
		if pv['pvType'] == 'Original':
			metadata['x_urls'].append(pv['url'])
		elif pv['pvId'] == pv_id:
			print(
				colorama.Fore.YELLOW + 'Have you downloaded a reprint? (' +
				colorama.Fore.RESET + uploader +
				colorama.Fore.YELLOW + ')'
			)
			metadata['x_is_reprint'] = uploader

	for artist in request['artists']:
		#print(artist)
		#print()

		# what's the difference between 'roles' and 'effectiveRoles'

		if (
			('Vocalist' in artist['roles']) or
			('Vocalist' in artist['categories'] and 'Default' in artist['roles'])
		):
			# `'artist' in artist`: custom artist vocalists: KeyError: 'artist'
			if 'artist' in artist and 'artistType' in artist['artist']:
				artist_type = artist['artist']['artistType']
				metadata['x_vocalist_types'][artist_type] = True

			if artist['isSupport']:
				metadata['vocalists_support'].append(artist['name'])
			else:
				metadata['vocalists'].append(artist['name'])

		if (
			('Circle' in artist['categories']) or
			('Composer' in artist['roles']) or
			('Producer' in artist['categories'] and 'Default' in artist['roles']) or
			('VoiceManipulator' in artist['roles']) # XXX
		):
			metadata['composers'].append(artist['name'])

		if (
			('Arranger' in artist['roles']) or
			('Arranger' in artist['categories'] and 'Default' in artist['roles'])
		) and (
			request['songType'] == 'Remix'
		):
			metadata['arrangers'].append(artist['name'])

		if (
			('Band' in artist['roles']) or
			('Band' in artist['categories'] and 'Default' in artist['roles'])
		):
			metadata['band'].append(artist['name'])

	return metadata

def get_song_data(path):
	"""
	Generate metadata for a song.

	Args:
		path: A path to a song.

	Returns:
		Song data (tuple).
		Database; *DB data (Dict); PV index; detection method.

		Nothing, (None) if appropriate.
	"""

	service = None
	pv_id = None
	ffprobe_output = None

	print('Examining path for PV ID:')
	for service in service_regexes:
		matches = re.search(service_regexes[service], path)

		if matches:
			pv_id = matches.group(1)
			print(f'o {service} | {pv_id}')
			server, request = query_api_song_by_pv(service, pv_id)
			if request:
				pv_index = which_pv(request, service, pv_id)
				return server, request, pv_index, 'path-pv'
		else:
			print(f'x {service}')

	# ignore this :)
	if path.lower().endswith('.url'):
		print('Examining Internet Shortcut for PV ID:')
		with open(path, mode = 'r', encoding = 'utf-8') as file:
			file_content = file.read()
			for service in service_regexes:
				matches = re.search('http.+' + service_regexes[service] + '.*', file_content)

				if matches:
					pv_id = matches.group(1)
					print(f'o {service} | {pv_id} | {matches.group(0)}')
					server, request = query_api_song_by_pv(service, pv_id)
					if request:
						pv_index = which_pv(request, service, pv_id)
						return server, request, pv_index, 'tags-pv'
				else:
					print(f'x {service}')
		cfg['ffprobe'] = False

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
			matches = re.search('(?:URL|url)=http.+' + service_regexes[service] + '.*', ffprobe_output)

			if matches:
				pv_id = matches.group(1)
				print(f'o {service} | {pv_id} | {matches.group(0)}')
				server, request = query_api_song_by_pv(service, pv_id)
				if request:
					pv_index = which_pv(request, service, pv_id)
					return server, request, pv_index, 'tags-pv'
			else:
				print(f'x {service}')

		print('Examining tags for title and artist:')
		matches = re.search('(?:title|TITLE)=([^/\n]+)', ffprobe_output)
		if matches:
			title = matches.group(1)
			print("title | " + title)
			matches = re.search('(?:artist|ARTIST)=([^/\n]+)', ffprobe_output)
			if matches:
				artist = matches.group(1)
				print("artist | " + artist)
			else:
				artist = None
			server, request = query_api_song_by_search(title, artist)
			if request:
				print(colorama.Back.YELLOW + 'This may be wrong.')
				return server, request, None, 'tags-search'

	print(colorama.Fore.RED + 'Entry not found!')
	return None, None, None, None

def which_pv(request, service, pv_id):
	"""
	Look through the PVs listed in *DB data, and find the one that matches the given data.

	Args:
		request: *DB data (Dict).
		service: A PV service.
		pv_id: A PV ID.

	Returns:
		The index of the PV in the DB* data.
	"""

	for i, pv in enumerate(request['pvs']):
		pv_id_new = pv['pvId']
		if service in from_vocadb_pv_id:
			pv_id_new = to_vocadb_pv_id[service](pv_id)
		if (service == pv['service'] and pv_id == pv_id_new):
			return i

def get_ffprobe_path():
	"""
	Get the path of a ffprobe executable/binary.

	Returns:
		The path of an ffprobe executable/binary.
	"""

	if cfg['ffprobe'] == True:
		# https://stackoverflow.com/q/9877462
		#from distutils.spawn import find_executable
		#return find_executable('ffprobe')
		return 'ffprobe'
	else:
		return cfg['ffprobe']

def query_api(server, operation, parameters):
	"""
	Query the *DB API.

	Args:
		server: The database name.
		operation: The API operation.
		parameters: Parameters (Dict).

	Returns:
		*DB data (Dict).

		Nothing, (None) if the API does not return data.
	"""

	request = http.request(
		'GET',
		server + '/api/' + operation,
		fields = parameters,
	)

	if not request.data == b'null':
		return json.loads(request.data)

	return None

def query_api_artist_by_search(artist):
	"""
	Query the *DB API for an artist.

	Args:
		artist: An artist.

	Returns:
		Database name; *DB data (Dict).

		Nothing, (None) if the API does not return results.
	"""

	for server in servers:
		request = query_api(
			server,
			'artists',
			{
				'query': artist,
			}
		)
		if request:
			if request['items']:
				return server, request['items'][0]

	return None, None

def query_api_song_by_search(title, artist):
	"""
	Query the *DB API for a song.

	Args:
		title: A title.
		artist: (optional) An artist.

	Returns:
		Database name; *DB data (Dict).

		Nothing, (None) if the API does not return results.
	"""

	artist_id = None
	if artist:
		server, request = query_api_artist_by_search(artist)
		if request:
			artist_id = request['id']

	for server in servers:
		if artist_id:
			request = query_api(
				server,
				'songs',
				{
					'query': title,
					'fields': 'Artists,PVs',
					'artistId[]': artist_id,
					'sort': 'RatingScore',
					'childVoicebanks': True,
				}
			)
		else:
			request = query_api(
				server,
				'songs',
				{
					'query': title,
					'fields': 'Artists,PVs',
					'sort': 'RatingScore',
				}
			)
		if request:
			if request['items']:
				return server, request['items'][0]

	return None, None

def query_api_song_by_pv(service, pv_id):
	"""
	Query the *DB API for a song, given a service and PV ID.

	Args:
		service: A PV service.
		pv_id: A PV ID.

	Returns:
		Database name; *DB data (Dict).

		Nothing, (None) if the API does not return results.
	"""

	pv_id_original = pv_id # for soundcloud

	if service in to_vocadb_pv_id:
		pv_id = to_vocadb_pv_id[service](pv_id)

	for server in servers:
		request = query_api(
			server,
			'songs/byPv',
			{
				'pvService': service,
				'pvId': pv_id,
				'fields': 'Artists,PVs',
				'lang': cfg['language'],
			}
		)

		if request:
			return server, request

	print(colorama.Fore.RED + 'Could not find a matching entry for this PV!')
	print('Add it?')
	for server in servers:
		print(server + '/Song/Create?pvUrl={}'.format(
			service_urls[service].format(pv_id_original)
		))

	return None, None

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = 'For PATH(s), retrieve song metadata from VocaDB or UtaiteDB.')
	parser.add_argument(
		'paths',
		metavar = 'PATH',
		help = 'Files or folders. Folders will be scanned for certain file ' +
			'types: ' + ' '.join(file_extensions),
		nargs = '+',
	)
	args = parser.parse_args()

	main(args)
