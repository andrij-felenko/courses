PREFIX ?= /usr
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/share/man/man1
SYSTEMDDIR ?= /lib/systemd/system

CC ?= gcc
CXX ?= g++
CFLAGS += -Wall -Wextra -O2
CXXFLAGS += -Wall -Wextra -O2 -std=c++17

TARGET = sysmon

all: $(TARGET)

$(TARGET): sysmon.c
	$(CC) $(CFLAGS) $< -o $@

cpp-build: sysmon.cpp
	$(CXX) $(CXXFLAGS) $< -o $(TARGET)

install: $(TARGET)
	install -d $(DESTDIR)$(BINDIR)
	install -m 0755 $(TARGET) $(DESTDIR)$(BINDIR)/$(TARGET)
	install -d $(DESTDIR)$(SYSTEMDDIR)
	install -m 0644 sysmon.service $(DESTDIR)$(SYSTEMDDIR)/sysmon.service

clean:
	rm -f $(TARGET)

.PHONY: all cpp-build install clean
