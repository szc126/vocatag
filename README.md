```console
$ /media/e-docs/docs/prog/g.z/vocatag/vocadb_tag.py /tmp/demo
/tmp/demo/nm10875677.mp3:
Examining path for PV ID:
o NicoNicoDouga | nm10875677
Entry found!
桜色舞うころ - プルメリ日和 feat. 白鐘ヒメカ | https://vocadb.net/S/163950

/tmp/demo/sm3761595.mp3:
Examining path for PV ID:
o NicoNicoDouga | sm3761595
Entry found!
ブラック★ロックシューター - ryo feat. 歌和サクラ | https://utaitedb.net/S/50685

/tmp/demo/sm9189786.m4a:
Examining path for PV ID:
o NicoNicoDouga | sm9189786
Entry found!
君の体温 - クワガタP feat. 初音ミク | https://vocadb.net/S/1318

/tmp/demo/zz4b7bBZ1N8.webm.ogg:
Examining path for PV ID:
x NicoNicoDouga
x SoundCloud
o Youtube | zz4b7bBZ1N8
Entry found!
ヴェノマニア公の狂気 - mothy feat. 神威がくぽ | https://vocadb.net/S/1277

$ cat /tmp/vocadb_tag.log
nm10875677.mp3＄桜色舞うころ＄白鐘ヒメカ＄カバー;プルメリ日和＄2010＄V;UTAU＄https://www.nicovideo.jp/watch/nm10875677＄Cover song | 163950@VocaDB
sm3761595.mp3＄ブラック★ロックシューター＄歌和サクラ＄歌ってみた;ryo＄2008＄V;ヒト＄https://www.nicovideo.jp/watch/sm3761595＄Cover song | 50685@UtaiteDB
sm9189786.m4a＄君の体温＄初音ミク＄クワガタP＄2009＄V;VOCALOID＄https://www.nicovideo.jp/watch/sm9189786＄Original song | 1318@VocaDB
zz4b7bBZ1N8.webm.ogg＄ヴェノマニア公の狂気 (feat. MEIKO, GUMI, KAITO, 初音ミク, 巡音ルカ)＄神威がくぽ＄mothy＄2010＄V;VOCALOID＄https://www.youtube.com/watch?v=zz4b7bBZ1N8＄Original song | 1277@VocaDB
$ cat /tmp/vocadb_tag.formatstring.log
%__filename_ext%＄%title%＄%artist%＄%composer%＄%date%＄%genre%＄%url%＄%comment%
```
