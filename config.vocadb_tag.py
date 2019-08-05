#!/usr/bin/env python3

language = 'Default' # Default, Japanese, Romaji, English

tags_output_file = 'vocadb_tag OUT.log'
tags_output_file_tag_delimiter = '\t'
formatstring_output_file = 'vocadb_tag OUT FS.log'

metadata_tags = {
	'TITLE': '$title',
	'ARTIST': '$vocalists',
	'COMPOSER': '$producers',
	'DATE': '$year',
	'URL': '$url',
	'COMMENT': '$song_type song ; $x_db_id@$x_db',
}
metadata_multi_value_delimiter = '; ' # as in "初音ミク; GUMI"