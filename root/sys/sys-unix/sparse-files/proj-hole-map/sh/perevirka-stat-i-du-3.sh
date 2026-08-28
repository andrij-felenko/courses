$ dd if=/dev/zero of=zeros.bin bs=1M count=64 status=none
$ du -h zeros.bin
64M     zeros.bin

$ ./sparsecp zeros.bin a.img        # карта: у джерелі дір немає — і в копії не буде
спосіб            карта SEEK_DATA/SEEK_HOLE
островів даних    1
перенесено        67108864 Б
джерело           st_size 67108864, зайнято 67108864 Б
копія             st_size 67108864, зайнято 67108864 Б
$ du -h a.img
64M     a.img

$ ./sparsecp -z zeros.bin b.img     # пошук нулів: діру вигадано на порожньому місці
спосіб            пошук нульових вікон
перенесено        0 Б
пропущено нулів   67108864 Б
джерело           st_size 67108864, зайнято 67108864 Б
копія             st_size 67108864, зайнято 0 Б
$ du -h b.img
0       b.img
