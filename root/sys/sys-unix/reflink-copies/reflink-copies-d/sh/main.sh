$ ls -lh vm.img
-rw-r--r-- 1 ann ann 40G Aug  6 09:12 vm.img

$ df --output=avail -h /srv
Avail
 118G

$ time cp vm.img backup.img
real    0m0.021s

$ df --output=avail -h /srv
Avail
 118G
