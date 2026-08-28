obj-m += my_netdev_notifier.o

# Шлях до каталогів заголовків і конфігурації поточного ядра
KDIR := /lib/modules/$(shell uname -r)/build
PWD  := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
