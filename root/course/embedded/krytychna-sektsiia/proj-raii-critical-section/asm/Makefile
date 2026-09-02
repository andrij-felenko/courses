# Складання асемблерного шару драйвера критичних секцій.
#
#   make                      # cortex-m7, з підтримкою D-Cache
#   make CPU=cortex-m4        # без кешу, BASEPRI лишається
#   make CPU=cortex-m0plus    # лише PRIMASK: решта модулів згортається #if-ами
#   make disasm               # дизасемблювати зібрану бібліотеку
#
# Результат — libcsasm.a: її лінкують до прошивки поруч із C/C++ шаром,
# оголошення C лежать в include/cs_asm.h.

CROSS   ?= arm-none-eabi-
CPU     ?= cortex-m7

CC       = $(CROSS)gcc
AR       = $(CROSS)ar
OBJDUMP  = $(CROSS)objdump

CPUFLAGS = -mcpu=$(CPU) -mthumb

# Кеш даних є лише на Cortex-M7 (і на M55); на решті ядер регістрів
# DCCMVAC/DCIMVAC просто не існує, тому модуль туди не потрапляє.
ifeq ($(CPU),cortex-m7)
CPUFLAGS += -mfpu=fpv5-d16 -mfloat-abi=hard
DEFS     += -DCS_HAS_DCACHE=1
endif

# -x assembler-with-cpp: файли .S проходять препроцесор, звідси #include і #if.
ASFLAGS  = $(CPUFLAGS) $(DEFS) -x assembler-with-cpp -Iinclude -Wall -g -ffunction-sections

SRCS = $(wildcard src/*.S)
OBJS = $(patsubst src/%.S,build/%.o,$(SRCS))

all: build/libcsasm.a

build/libcsasm.a: $(OBJS)
	$(AR) rcs $@ $^

build/%.o: src/%.S include/cortex_m.inc | build
	$(CC) $(ASFLAGS) -c $< -o $@

build:
	mkdir -p build

disasm: build/libcsasm.a
	$(OBJDUMP) -d --no-show-raw-insn $<

clean:
	rm -rf build

.PHONY: all disasm clean
