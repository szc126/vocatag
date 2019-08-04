#!/usr/bin/env python3

LANGUAGE = 'Default' # Default, Japanese, Romaji, English

OUTPUT_FILE = 'vocadb_tag OUT.log'
OUTPUT_DELIMITER = '\t'
FORMATSTRING_OUTPUT_FILE = 'vocadb_tag OUT FS.log'

METADATA_FORMAT = {
	'TITLE': '$title',
	'ARTIST': '$vocalists',
	'COMPOSER': '$producers',
	'DATE': '$year',
	'URL': '$url',
	'COMMENT': '$song_type song ; $x_db_id@$x_db',
}
METADATA_DELIMITER = '; ' # as in "初音ミク; GUMI"