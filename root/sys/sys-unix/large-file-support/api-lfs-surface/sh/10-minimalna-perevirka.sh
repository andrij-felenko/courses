$ cc -m32 probe.c -o narrow
$ cc -m32 $(getconf LFS_CFLAGS) probe.c -o wide

$ ./narrow big.iso
sizeof(off_t) = 4
open: Value too large for defined data type (errno 75)

$ ./wide big.iso
sizeof(off_t) = 8
розмір у байтах = 4700372992
