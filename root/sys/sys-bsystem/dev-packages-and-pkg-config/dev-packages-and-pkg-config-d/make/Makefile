# Makefile
CC ?= gcc
CFLAGS ?= -Wall -Wextra -O2
PKG_CONFIG ?= pkg-config

# Отримуємо прапорці від pkg-config
PNG_CFLAGS := $(shell $(PKG_CONFIG) --cflags libpng)
PNG_LIBS := $(shell $(PKG_CONFIG) --libs libpng)

CFLAGS += $(PNG_CFLAGS)
LDLIBS += $(PNG_LIBS)

img_proc: src/main.o
	$(CC) $(LDFLAGS) $^ $(LDLIBS) -o $@

src/main.o: src/main.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f src/*.o img_proc
