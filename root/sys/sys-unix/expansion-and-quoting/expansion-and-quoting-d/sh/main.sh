$ set -x
$ FILE="my document.txt"
$ ls -l $FILE
+ ls -l my document.txt
ls: cannot access 'my': No such file or directory
ls: cannot access 'document.txt': No such file or directory

$ ls -l "$FILE"
+ ls -l 'my document.txt'
-rw-r--r-- 1 user user 4096 Aug 14 10:00 'my document.txt'
