CC      ?= gcc
CFLAGS  ?= -std=c11 -O2 -Wall -Wextra -Wpedantic -Iinclude -Isrc
LDLIBS  := -lm

SRC := src/bumpless_pid.c src/plant.c src/main.c
BIN := bumpless-demo

$(BIN): $(SRC)
	$(CC) $(CFLAGS) -o $@ $(SRC) $(LDLIBS)

clean:
	rm -f $(BIN)

.PHONY: clean
