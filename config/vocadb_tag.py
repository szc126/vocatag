#!/usr/bin/env python3

language = 'Default' # Default, Japanese, Romaji, English

tags_output_file = '/tmp/vocadb_tag.log'
tags_output_file_tag_delimiter = 'ㄅ'
bom = False # mp3tag
formatstring_output_file = '/tmp/vocadb_tag.formatstring.log'

metadata_tags = {
	'__filename_ext': '$x_filename_ext', # mp3tag
	'title': lambda x: x['title'] + (' (' + x['year'] + ')' if x['song_type'] == 'Remaster' else '') + (' (feat. ' + ', '.join(x['vocalists_support']) + ')' if x['vocalists_support'] else ''),
	'artist': lambda x: ';'.join(
		x['band'] +
		x['vocalists']
	),
	'composer': lambda x: ';'.join(
		x['composers'] +
		[s for s in x['arrangers'] if not s in x['composers']] +
		[s for s in [
			('カバー' if x['song_type'] in ['Cover', 'Remix'] and not 'Utaite' in x['x_vocalist_types'] else None),
			('歌ってみた' if x['song_type'] in ['Cover', 'Remix'] and 'Utaite' in x['x_vocalist_types'] else None),
		] if s]
	),
	'date': '$year',
	'genre': lambda x: ';'.join(
		[s for s in [
			('S:Re' if x['x_is_reprint'] else None),
			'V' + ('アレンジ' if x['song_type'] == 'Remix' else ''),
		] if s] +
		list(x['x_vocalist_types'].keys())
	)
		.replace('Producer', 'ヒト')
		.replace('Utaite', 'ヒト')
		.replace('OtherVocalist', 'ヒト')
		.replace('CoverArtist', 'ヒト')
		.replace('Vocaloid', 'VOCALOID')
	,
	'url': lambda x: x['url']
		.replace('https://youtu.be/', 'https://www.youtube.com/watch?v=')
		if x['url'] else ''
	,
	'comment': '$song_type song | $x_db/S/$x_db_id',
}
metadata_multi_value_delimiter = ';' # as in "初音ミク; GUMI"
metadata_empty_placeholder = '-' # for foobar2000

ffprobe = True # True, False, r"D:\bin\ffmpeg\ffprobe.exe"
