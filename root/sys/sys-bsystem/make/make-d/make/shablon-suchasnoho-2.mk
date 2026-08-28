# ==============================================================================
# Сучасний ідіоматичний Makefile для C/C++ проекту з автоматичними dep-файлами
# ==============================================================================

# 1. Налаштування оболонки та керуючих параметрів Make
SHELL := /bin/sh
.ONESHELL:
.DELETE_ON_ERROR:
export LC_ALL := C

# 2. Визначення тулчейну та стандартних прапорців
CC       ?= gcc
CXX      ?= g++
CPPFLAGS := -Iinclude -MMD -MP
CFLAGS   := -std=c11 -O2 -Wall -Wextra -pedantic -g
CXXFLAGS := -std=c++20 -O2 -Wall -Wextra -g
LDFLAGS  := 
LDLIBS   := -lm

# 3. Структура каталогів проекту
SRC_DIR   := src
INC_DIR   := include
BUILD_DIR := build
BIN_DIR   := bin
TARGET    := $(BIN_DIR)/app

# 4. Пошук джерел та генерація списків об'єктів
C_SRCS    := $(wildcard $(SRC_DIR)/*.c)
CPP_SRCS  := $(wildcard $(SRC_DIR)/*.cpp)

C_OBJS    := $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(C_SRCS))
CPP_OBJS  := $(patsubst $(SRC_DIR)/%.cpp,$(BUILD_DIR)/%.o,$(CPP_SRCS))
ALL_OBJS  := $(C_OBJS) $(CPP_OBJS)

# Список файлів залежностей (.d), які компілятор згенерує поруч із .o
DEPS      := $(ALL_OBJS:.o=.d)

# 5. Головні цілі
.PHONY: all clean test info

all: $(TARGET)

# Лінкування фінального виконуваного бінарного файлу
$(TARGET): $(ALL_OBJS) | $(BIN_DIR)
	$(if $(CPP_SRCS),$(CXX),$(CC)) $(LDFLAGS) $^ $(LDLIBS) -o $@
	@echo "✓ Проект успішно зібрано: $@"

# Шаблонне правило для вихідних файлів на C
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

# Шаблонне правило для вихідних файлів на C++
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp | $(BUILD_DIR)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

# Створення вихідних каталогів як order-only пререквізитів
$(BUILD_DIR) $(BIN_DIR):
	@mkdir -p $@

# 6. Очищення скомпільованих файлів
clean:
	@rm -rf $(BUILD_DIR) $(BIN_DIR)
	@echo "✓ Каталоги збірки очищено."

# 7. Діагностична інформація
info:
	@echo "Вихідні файли C:   $(C_SRCS)"
	@echo "Вихідні файли C++: $(CPP_SRCS)"
	@echo "Об'єктні файли:    $(ALL_OBJS)"
	@echo "Файли залежностей: $(DEPS)"

# 8. Підключення згенерованих компілятором файлів залежностей .d
# Префікс '-' ігнорує відсутність файлів під час першої збірки
-include $(DEPS)
