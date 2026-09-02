# Один бінарник ttyx. terminfo лінкується окремою бібліотекою (-ltinfo),
# бо тільки terminfo_caps.c її й потребує.
CC      ?= cc
CFLAGS  ?= -std=c11 -O2 -Wall -Wextra -D_GNU_SOURCE
LDLIBS  ?= -ltinfo

OBJ = main.o termios_flags.o termios_profiles.o tty_session.o \
      tty_signals.o tty_input.o readpass.o pty_packet.o terminfo_caps.o \
      termios_abi.o termios2_baud.o

ttyx: $(OBJ)
	$(CC) $(CFLAGS) -o $@ $(OBJ) $(LDLIBS)

$(OBJ): termios_flags.h termios_profiles.h tty_session.h tty_signals.h \
        tty_input.h readpass.h pty_packet.h terminfo_caps.h \
        termios_abi.h termios2_baud.h

clean:
	rm -f ttyx $(OBJ)

.PHONY: clean
