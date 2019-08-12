#!/usr/bin/env python3

language = 'Default' # Default, Japanese, Romaji, English

tags_output_file = '.vocadb_tag.log'
tags_output_file_tag_delimiter = ' #~~# '
bom = False # mp3tag
formatstring_output_file = '.vocadb_tag.formatstring.log'

metadata_tags = {
	'TITLE': '$title',
	'ARTIST': '$vocalists',
	'COMPOSER': '$producers',
	'DATE': '$year',
	'URL': '$url',
	'COMMENT': '$song_type song | $x_db_id@$x_db_name',
	'__filename_ext': '$x_filename_ext', # mp3tag
}
metadata_multi_value_delimiter = '\\\\' # as in "初音ミク; GUMI"

ffprobe = True # True, False, <path>
