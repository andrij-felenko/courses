$ truncate -s 1T src.img
$ dd if=/dev/urandom of=src.img bs=4096 count=10 conv=notrunc status=none
$ dd if=/dev/urandom of=src.img bs=4096 count=27 seek=134217728 conv=notrunc status=none
$ sync

$ ./sparsecp src.img copy.img
спосіб            карта SEEK_DATA/SEEK_HOLE
островів даних    2
перенесено        151552 Б
джерело           st_size 1099511627776, зайнято 151552 Б
копія             st_size 1099511627776, зайнято 151552 Б
