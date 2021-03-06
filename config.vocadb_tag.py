#!/usr/bin/env python3

language = 'Default' # Default, Japanese, Romaji, English

tags_output_file = '.vocadb_tag.log'
tags_output_file_tag_delimiter = ' #~~# '
bom = False # mp3tag
formatstring_output_file = '.vocadb_tag.formatstring.log'

metadata_tags = {
	'__filename_ext': '$x_filename_ext', # mp3tag
	'x_title': lambda x: x['title'] + (' (feat. ' + ' ,'.join(x['vocalists_support']) + ')' if x['vocalists_support'] else ''),
	'x_artist': '$vocalists',
	'x_composer': '$composers',
	'date': '$year',
	'genre': '$x_vocalist_types',
	'url': '$url',
	'x_comment': '$x_is_reprint | $x_detection_method | $song_type song | $x_db_id@$x_db_name',
}
metadata_multi_value_delimiter = '#' # as in "初音ミク; GUMI"
metadata_empty_placeholder = '-' # foobar2000

ffprobe = True # True, False, r"D:\bin\ffmpeg\ffprobe.exe"
