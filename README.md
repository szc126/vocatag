```console
$ /tmp/vocatag/vocadb_tag.py /tmp/demo/
/tmp/demo/hqiQSyE4CgI.mp3:
Examining path for PV ID:
x NicoNicoDouga
x SoundCloud
o Youtube | hqiQSyE4CgI
Have you downloaded a reprint? (mikumikunoado)
Entry found!
ブラック★ロックシューター - ryo feat. 歌和サクラ | https://utaitedb.net/S/50685

/tmp/demo/nm10875677.mp3:
Examining path for PV ID:
o NicoNicoDouga | nm10875677
Entry found!
桜色舞うころ - プルメリ日和 feat. 白鐘ヒメカ | https://vocadb.net/S/163950

/tmp/demo/zz4b7bBZ1N8.webm.ogg:
Examining path for PV ID:
x NicoNicoDouga
x SoundCloud
o Youtube | zz4b7bBZ1N8
Entry found!
ヴェノマニア公の狂気 - mothy feat. 神威がくぽ | https://vocadb.net/S/1277

/tmp/demo/君の体温.m4a:
Examining path for PV ID:
x NicoNicoDouga
x SoundCloud
x Youtube
Examining tags for PV ID:
x NicoNicoDouga
x SoundCloud
x Youtube
Examining tags for title and artist:
title | 君の体温
artist | 初音ミク
This may be wrong.
Entry found!
君の体温 - クワガタP feat. 初音ミク | https://vocadb.net/S/1318

$ cat /tmp/vocadb_tag.log
hqiQSyE4CgI.mp3＄ブラック★ロックシューター＄歌和サクラ＄歌ってみた;ryo＄2008＄S:Re;V;ヒト＄https://www.youtube.com/watch?v=hqiQSyE4CgI＄Cover song | 50685@UtaiteDB
nm10875677.mp3＄桜色舞うころ＄白鐘ヒメカ＄カバー;プルメリ日和＄2010＄V;UTAU＄-＄Cover song | 163950@VocaDB
zz4b7bBZ1N8.webm.ogg＄ヴェノマニア公の狂気 (feat. MEIKO, GUMI, KAITO, 初音ミク, 巡音ルカ)＄神威がくぽ＄mothy＄2010＄V;VOCALOID＄https://www.youtube.com/watch?v=zz4b7bBZ1N8＄Original song | 1277@VocaDB
君の体温.m4a＄君の体温＄初音ミク＄クワガタP＄2009＄V;VOCALOID＄-＄Original song | 1318@VocaDB
$ cat /tmp/vocadb_tag.formatstring.log
%__filename_ext%＄%title%＄%artist%＄%composer%＄%date%＄%genre%＄%url%＄%comment%
```
