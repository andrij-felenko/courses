$ cat /tmp/gen/stats
getattr 23
readdir 2
open    5
read    9

$ ls -l /tmp/gen/squares > /dev/null
$ cat /tmp/gen/stats
getattr 37
readdir 3
open    6
read    11
