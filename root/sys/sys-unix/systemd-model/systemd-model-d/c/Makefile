CFLAGS ?= -O2 -g -Wall -Wextra -std=c11
SD_CFLAGS := $(shell pkg-config --cflags libsystemd)
SD_LIBS := $(shell pkg-config --libs libsystemd)

all: worker unitctl

worker: worker.c listen_fds.c listen_fds.h
	$(CC) $(CFLAGS) $(SD_CFLAGS) -o $@ worker.c listen_fds.c $(SD_LIBS)

unitctl: unitctl.c
	$(CC) $(CFLAGS) $(SD_CFLAGS) -o $@ unitctl.c $(SD_LIBS)

clean:
	rm -f worker unitctl

.PHONY: all clean
