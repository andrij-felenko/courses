$ cc -m32 -c checksum.c -o narrow.o
$ nm -u narrow.o
                 U lseek
                 U open
                 U stat

$ cc -m32 -D_FILE_OFFSET_BITS=64 -c checksum.c -o wide.o
$ nm -u wide.o
                 U lseek64
                 U open64
                 U stat64

$ cc -m32 -D_FILE_OFFSET_BITS=64 -D_TIME_BITS=64 -c checksum.c -o wide64.o
$ nm -u wide64.o
                 U lseek64
                 U open64
                 U __stat64_time64
