CC      ?= cc
CFLAGS  ?= -std=c11 -Wall -Wextra -O2

node: main.o frame.o link.o
	$(CC) $(CFLAGS) -o $@ $^

main.o: main.c frame.h link.h
frame.o: frame.c frame.h
link.o: link.c link.h frame.h

clean:
	rm -f node *.o

.PHONY: clean
