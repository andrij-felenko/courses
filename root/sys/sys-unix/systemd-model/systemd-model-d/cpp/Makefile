CXXFLAGS ?= -O2 -g -Wall -Wextra -std=c++23
SD_CFLAGS := $(shell pkg-config --cflags libsystemd)
SD_LIBS := $(shell pkg-config --libs libsystemd)

all: worker unitctl

worker: src/worker.cpp src/listen_socket.cpp src/listen_socket.hpp src/notify.hpp src/unique_fd.hpp
	$(CXX) $(CXXFLAGS) $(SD_CFLAGS) -o $@ src/worker.cpp src/listen_socket.cpp $(SD_LIBS)

unitctl: src/unitctl.cpp
	$(CXX) $(CXXFLAGS) $(SD_CFLAGS) -o $@ src/unitctl.cpp $(SD_LIBS)

clean:
	rm -f worker unitctl

.PHONY: all clean
