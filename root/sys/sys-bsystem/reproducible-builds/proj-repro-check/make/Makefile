# Недетерміністичний Makefile
CC ?= gcc
CFLAGS ?= -O2 -g -Wall

SRCS = $(wildcard src/*.c)
OBJS = $(SRCS:.c=.o)

all: bin/app

lib/libcalc.a: src/calc.o
	@mkdir -p lib
	ar rcs $@ $^

bin/app: src/main.o lib/libcalc.a
	@mkdir -p bin
	$(CC) $(CFLAGS) -o $@ src/main.o -Llib -lcalc

src/%.o: src/%.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -rf src/*.o lib bin
