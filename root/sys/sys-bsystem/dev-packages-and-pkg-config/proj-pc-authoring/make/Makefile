# Makefile споживача
CC ?= gcc
CFLAGS ?= -Wall -Wextra -O2
PKG_CONFIG ?= pkg-config

# Динамічні прапорці
DYN_CFLAGS := $(shell $(PKG_CONFIG) --cflags geomcalc)
DYN_LIBS   := $(shell $(PKG_CONFIG) --libs geomcalc)
DYN_RPATH  := -Wl,-rpath,$(shell $(PKG_CONFIG) --variable=libdir geomcalc)

# Статичні прапорці
STATIC_CFLAGS := $(shell $(PKG_CONFIG) --static --cflags geomcalc)
STATIC_LIBS   := $(shell $(PKG_CONFIG) --static --libs geomcalc)

all: client client_static

# Збірка динамічного клієнта
client: client.c
	$(CC) $(CFLAGS) $(DYN_CFLAGS) $< $(DYN_RPATH) $(DYN_LIBS) -o $@

# Збірка повністю статичного бінарника
client_static: client.c
	$(CC) -static $(CFLAGS) $(STATIC_CFLAGS) $< $(STATIC_LIBS) -o $@

clean:
	rm -f client client_static
