obj-m += p2p_dma_demo.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all: module client_c client_cpp

module:
	make -C $(KDIR) M=$(PWD) modules

client_c: client.c
	gcc -O2 -Wall client.c -o client_c

client_cpp: client.cpp
	g++ -O2 -Wall -std=c++20 client.cpp -o client_cpp

clean:
	make -C $(KDIR) M=$(PWD) clean
	rm -f client_c client_cpp
