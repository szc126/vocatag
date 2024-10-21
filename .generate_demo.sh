#!/usr/bin/env bash

touch BV1wW411W7jq.m4a
touch hqiQSyE4CgI.mp3
touch nm10875677.mp3
ffmpeg -f lavfi -i anullsrc -t 1 -metadata 'title=Kasane Territory' -metadata 'artist=Teto Kasane' 'Kasane Teto - Kasane Territory.mp3'
ffmpeg -f lavfi -i anullsrc -t 1 -metadata 'URL=https://www.bilibili.com/video/BV1TE411379f/' '处处吻.mp3'