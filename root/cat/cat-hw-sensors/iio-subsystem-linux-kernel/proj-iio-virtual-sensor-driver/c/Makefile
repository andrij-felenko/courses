obj-m += iio_virtual_driver.o
iio_virtual_driver-y := src/iio_virtual_sensor.o src/iio_trigger_buffer.o

ccflags-y := -I$(src)/include

KDIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
