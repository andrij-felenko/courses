# Детерміністичний, повністю відтворюваний Makefile
CC ?= gcc
AR ?= ar

# 1. Фіксація часової позначки останнього коміту
SOURCE_DATE_EPOCH ?= $(shell git log -1 --format=%ct 2>/dev/null || echo 1700000000)
export SOURCE_DATE_EPOCH

# 2. Нормалізація шляхів та усунення сторонніх метаданих
CFLAGS ?= -O2 -g -Wall \
          -ffile-prefix-map=$(CURDIR)=. \
          -fno-ident \
          -gno-record-gcc-switches

# 3. Детерміністичний ідентифікатор складання
LDFLAGS ?= -Wl,--build-id=sha1

# 4. Детерміністичне алфавітне сортування списку файлів
SRCS = $(sort $(wildcard src/*.c))
OBJS = $(SRCS:.c=.o)

.PHONY: all clean

all: bin/app

lib/libcalc.a: src/calc.o
	@mkdir -p lib
	# 5. Використання прапорця 'D' (deterministic mode)
	$(AR) Drcs $@ $^

bin/app: src/main.o lib/libcalc.a
	@mkdir -p bin
	$(CC) $(CFLAGS) -o $@ src/main.o -Llib -lcalc $(LDFLAGS)

src/%.o: src/%.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -rf src/*.o lib bin
