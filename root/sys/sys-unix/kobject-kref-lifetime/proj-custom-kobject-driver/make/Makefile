obj-m += sample_kobject_module.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	make -C $(KDIR) M=$(PWD) modules
	$(CC) -O2 -pthread test_kobject_stress.c -o test_stress_c
	g++ -O2 -std=c++20 test_kobject_stress.cpp -o test_stress_cpp

clean:
	make -C $(KDIR) M=$(PWD) clean
	rm -f test_stress_c test_stress_cpp
