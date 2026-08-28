$ stat -c '%n  size=%s  blocks=%b по %B Б' src.img copy.img
src.img   size=1099511627776  blocks=296 по 512 Б
copy.img  size=1099511627776  blocks=296 по 512 Б

$ du -h --apparent-size src.img copy.img
1.0T    src.img
1.0T    copy.img

$ du -h src.img copy.img
148K    src.img
148K    copy.img
