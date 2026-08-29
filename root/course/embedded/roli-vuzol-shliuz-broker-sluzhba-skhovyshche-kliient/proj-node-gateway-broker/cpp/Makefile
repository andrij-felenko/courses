CXX      ?= g++
CXXFLAGS ?= -std=c++23 -Wall -Wextra -O2

node: main.o protocol.o link.o
	$(CXX) $(CXXFLAGS) -o $@ $^

main.o: main.cpp link.hpp node.hpp protocol.hpp
protocol.o: protocol.cpp protocol.hpp
link.o: link.cpp link.hpp protocol.hpp

clean:
	rm -f node *.o

.PHONY: clean
