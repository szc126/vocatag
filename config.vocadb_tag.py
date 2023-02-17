#!/usr/bin/env python3

language = 'Default' # Default, Japanese, Romaji, English

tags_output_file = '/tmp/vocadb_tag.log'
tags_output_file_tag_delimiter = '＄'
bom = False # mp3tag
formatstring_output_file = '/tmp/vocadb_tag.formatstring.log'

metadata_tags = {
	'__filename_ext': '$x_filename_ext', # mp3tag
	'title': lambda x: x['title'] + (' (feat. ' + ', '.join(x['vocalists_support']) + ')' if x['vocalists_support'] else ''),
	'artist': lambda x: ';'.join(
		x['band'] +
		x['vocalists']
	),
	'composer': lambda x: ';'.join(
		[s for s in [
			('カバー' if x['song_type'] in ['Cover', 'Remix'] and not 'Utaite' in x['x_vocalist_types'] else None),
			('歌ってみた' if x['song_type'] in ['Cover', 'Remix'] and 'Utaite' in x['x_vocalist_types'] else None),
		] if s] +
		x['composers'] +
		x['arrangers']
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
		.replace('Vocaloid', 'VOCALOID')
	,
	'url': '$url',
	'comment': '$song_type song | $x_db/S/$x_db_id',
}
metadata_multi_value_delimiter = ';' # as in "初音ミク; GUMI"
metadata_empty_placeholder = '-' # foobar2000

ffprobe = True # True, False, r"D:\bin\ffmpeg\ffprobe.exe"
