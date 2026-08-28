obj-m += lockup_trigger.o
KDIR ?= /lib/modules/$(shell uname -r)/build

all: module cli

module:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

cli:
	gcc -O2 -Wall lockup_ctl.c -o lockup_ctl_c
	g++ -O2 -std=c++20 -Wall lockup_ctl.cpp -o lockup_ctl_cpp

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	rm -f lockup_ctl_c lockup_ctl_cpp
