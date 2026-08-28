firmware.elf: main.o led.o uart.o
	gcc main.o led.o uart.o -o firmware.elf

main.o: main.c led.h uart.h
	gcc -c main.c -o main.o

led.o: led.c led.h
	gcc -c led.c -o led.o

uart.o: uart.c uart.h
	gcc -c uart.c -o uart.o
