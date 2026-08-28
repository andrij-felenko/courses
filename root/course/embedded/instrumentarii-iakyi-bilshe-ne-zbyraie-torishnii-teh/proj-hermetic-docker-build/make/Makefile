# Визначення часу збірки через SOURCE_DATE_EPOCH або фіксований дефолт
SOURCE_DATE_EPOCH ?= 1700000000

CC      := arm-none-eabi-gcc
OBJCOPY := arm-none-eabi-objcopy
AR      := arm-none-eabi-ar

# Нормалізація шляхів до файлів у DWARF та макросах
SRCDIR  := $(CURDIR)
CFLAGS  += -ffile-prefix-map=$(SRCDIR)=.
CFLAGS  += -fmacro-prefix-map=$(SRCDIR)=.
CFLAGS  += -fdebug-prefix-map=$(SRCDIR)=.
CFLAGS  += -Wl,--build-id=none
CFLAGS  += -DSOURCE_DATE_EPOCH=$(SOURCE_DATE_EPOCH)
CFLAGS  += -O2 -g -Wall -Wextra -Werror

# Детермінований режим архівації бібліотек
ARFLAGS := Dcr

# Стабільне сортування списку об'єктних файлів
SRCS    := $(sort $(wildcard src/*.c))
OBJS    := $(SRCS:.c=.o)

all: build/firmware.bin

build/firmware.elf: $(OBJS) | build
	$(CC) $(CFLAGS) -T linker.ld $(OBJS) -o $@

build/firmware.bin: build/firmware.elf
	$(OBJCOPY) -O binary $< $@

build:
	mkdir -p build

clean:
	rm -rf build src/*.o
