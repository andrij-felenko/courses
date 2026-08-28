$ ./kvlog put місто Львів
$ ./kvlog put ріка Полтва
$ ls -l store.log
-rw-r--r-- 1 user user 98 ... store.log

$ head -c 40 /dev/urandom >> store.log     # «обрив» посеред третього запису
$ ./kvlog list
записів: 2, журнал: 98 Б, наступний номер: 3
$ ls -l store.log
-rw-r--r-- 1 user user 98 ... store.log
