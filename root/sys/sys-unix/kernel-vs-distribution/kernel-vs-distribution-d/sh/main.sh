$ gcc -O2 -o hello-dyn    hello.c
$ gcc -O2 -static -o hello-st hello.c
$ ls -l hello-dyn hello-st
-rwxr-xr-x  16K  hello-dyn
-rwxr-xr-x 780K  hello-st

$ ldd hello-dyn
        libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6
$ ldd hello-st
        not a dynamic executable
