# Makefile.customer — Надається клієнту у складі relink kit

TOOLCHAIN_PREFIX ?= arm-none-eabi-
CC = $(TOOLCHAIN_PREFIX)gcc
LD = $(TOOLCHAIN_PREFIX)ld
OBJCOPY = $(TOOLCHAIN_PREFIX)objcopy

CFLAGS = -mcpu=cortex-m4 -mthumb -O2 -Ilgpl_src/include
LDFLAGS = -T scripts/linker_script.ld -Wl,--gc-sections

# 1. Компіляція модифікованого клієнтом коду LGPL-бібліотеки
lgpl_codec.o: lgpl_src/codec.c
	$(CC) $(CFLAGS) -c $< -o $@

# 2. Перелінкування пропрієтарного об'єктного файлу з новою бібліотекою
firmware.elf: obj/proprietary_engine.o lgpl_codec.o
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

firmware.bin: firmware.elf
	$(OBJCOPY) -O binary $< $@

clean:
	rm -f lgpl_codec.o firmware.elf firmware.bin

.PHONY: clean
