CC ?= clang
CXX ?= clang++
CFLAGS = -Wall -Wextra -Wpedantic -g -O1
CXXFLAGS = -Wall -Wextra -Wpedantic -std=c++20 -g -O1

SRC_C = host_test_framework.c
SRC_CPP = host_test_framework.cpp

.PHONY: all test-asan test-ubsan test-valgrind test-coverage clean

all: test-asan test-ubsan

# 1. AddressSanitizer (пошук виходу за межі пам'яті та UAF)
test-asan:
	$(CC) $(CFLAGS) -fsanitize=address $(SRC_C) -o test_asan_c
	$(CXX) $(CXXFLAGS) -fsanitize=address $(SRC_CPP) -o test_asan_cpp
	./test_asan_c
	./test_asan_cpp

# 2. UndefinedBehaviorSanitizer (пошук знакових переповнень і невалідних зсувів)
test-ubsan:
	$(CC) $(CFLAGS) -fsanitize=undefined $(SRC_C) -o test_ubsan_c
	$(CXX) $(CXXFLAGS) -fsanitize=undefined $(SRC_CPP) -o test_ubsan_cpp
	./test_ubsan_c
	./test_ubsan_cpp

# 3. Valgrind Memcheck (пошук неініціалізованої пам'яті)
test-valgrind:
	$(CC) $(CFLAGS) $(SRC_C) -o test_native_c
	valgrind --leak-check=full --track-origins=yes --error-exitcode=1 ./test_native_c

# 4. Покриття коду (gcov / lcov)
test-coverage:
	$(CC) $(CFLAGS) --coverage $(SRC_C) -o test_cov_c
	./test_cov_c
	lcov --capture --directory . --output-file coverage.info
	genhtml coverage.info --output-directory out_html

clean:
	rm -f test_* *.gcno *.gcda *.info
	rm -rf out_html
