# Детермінована збірка прошивки. Запускається ВСЕРЕДИНІ контейнера
# docker/Dockerfile.builder з кореня змонтованого дерева:
#     make -f make/Makefile
# Усе, що зазвичай робить збірку неповторюваною — час, шляхи, порядок
# файлів, UID у заголовках архівів — прибито тут.

.SUFFIXES:

# Однакова локаль у всіх утилітах: sort, ar і сам компілятор залежать від неї
export LC_ALL := C
export LANG   := C

# Час збірки приходить ззовні (build.sh бере git log -1 --format=%ct).
# Дефолт лишений тільки щоб ручний запуск не падав.
SOURCE_DATE_EPOCH ?= 1700000000
export SOURCE_DATE_EPOCH

# Повний SHA-1 коміту підставляє build.sh; нулі означають «збирали не з релізу»
FW_GIT_COMMIT ?= 0000000000000000000000000000000000000000

# Ідентифікатор тулчейну беремо з образу: Dockerfile поклав туди хеш архіву
TOOLCHAIN_SHA   := $(shell cut -c1-12 /opt/toolchain/.sha256 2>/dev/null || echo unknown00000)
FW_TOOLCHAIN_ID := gcc-13.2-$(TOOLCHAIN_SHA)

CROSS   := arm-none-eabi-
CC      := $(CROSS)gcc
AR      := $(CROSS)ar
OBJCOPY := $(CROSS)objcopy
SIZE    := $(CROSS)size
PYTHON  := python3

BUILD   := build
OBJ     := $(BUILD)/obj
SRCDIR  := $(CURDIR)

CPU     := -mcpu=cortex-m4 -mthumb

CFLAGS  := $(CPU) -std=c11 -Os -g3 -ffreestanding -fno-common
CFLAGS  += -Wall -Wextra -Werror
# -Wdate-time робить помилкою кожен __DATE__/__TIME__ у коді: саме вони
# найчастіше й лишають плаваючий рядок у .rodata.
CFLAGS  += -Wdate-time
CFLAGS  += -ffunction-sections -fdata-sections
CFLAGS  += -Ic/include
# Нормалізація шляхів: у DWARF, у __FILE__ і в діагностику препроцесора
# має потрапити «.», а не /home/<хто-збирав>/…
CFLAGS  += -ffile-prefix-map=$(SRCDIR)=.
CFLAGS  += -fmacro-prefix-map=$(SRCDIR)=.
CFLAGS  += -fdebug-prefix-map=$(SRCDIR)=.
CFLAGS  += -DSOURCE_DATE_EPOCH=$(SOURCE_DATE_EPOCH)UL
CFLAGS  += -DFW_GIT_COMMIT='"$(FW_GIT_COMMIT)"'
CFLAGS  += -DFW_TOOLCHAIN_ID='"$(FW_TOOLCHAIN_ID)"'

# --build-id=none прибирає хеш компонування, який ld інакше кладе в окрему
# секцію й міняє при будь-якому дрібному відхиленні середовища.
LDFLAGS := $(CPU) -nostdlib -T c/linker.ld
LDFLAGS += -Wl,--build-id=none -Wl,--gc-sections -Wl,-Map=$(BUILD)/firmware.map

# D — детермінований режим ar: нулі замість UID/GID і Jan 1 1970 у заголовку
ARFLAGS := Dcr

# $(sort) прибиває порядок, у якому readdir() віддає імена: без нього
# порядок об'єктних файлів у секції .text залежить від файлової системи.
LIB_SRCS := $(sort $(wildcard c/src/crc32.c c/src/build_meta.c))
APP_SRCS := $(sort $(filter-out $(LIB_SRCS),$(wildcard c/src/*.c)))
LIB_OBJS := $(patsubst c/src/%.c,$(OBJ)/%.o,$(LIB_SRCS))
APP_OBJS := $(patsubst c/src/%.c,$(OBJ)/%.o,$(APP_SRCS))

.PHONY: all clean check-stamp

all: $(BUILD)/firmware.sha256

$(OBJ)/%.o: c/src/%.c | $(OBJ)
	$(CC) $(CFLAGS) -MMD -MP -c $< -o $@

# rm перед ar обов'язковий: ключ r ДОПИСУЄ в наявний архів, тож без
# видалення стара збірка протікає в нову й ламає повторюваність.
$(BUILD)/libmeta.a: $(LIB_OBJS)
	rm -f $@
	$(AR) $(ARFLAGS) $@ $^

$(BUILD)/firmware.elf: $(APP_OBJS) $(BUILD)/libmeta.a c/linker.ld
	$(CC) $(LDFLAGS) $(APP_OBJS) $(BUILD)/libmeta.a -o $@
	$(SIZE) $@

$(BUILD)/firmware.bin: $(BUILD)/firmware.elf
	$(OBJCOPY) -O binary $< $@
	# Розмір і CRC32 образу відомі лише після компонування — їх у секцію
	# .meta вписує stamp_meta.py, детерміновано й на місці.
	$(PYTHON) py/stamp_meta.py $@

$(BUILD)/firmware.sha256: $(BUILD)/firmware.bin
	cd $(BUILD) && sha256sum firmware.bin firmware.elf > firmware.sha256

# Окрема ціль для CI: перечитати образ і звірити вписаний CRC
check-stamp: $(BUILD)/firmware.bin
	$(PYTHON) py/stamp_meta.py --verify $<

$(OBJ):
	mkdir -p $(OBJ)

clean:
	rm -rf $(BUILD)

-include $(LIB_OBJS:.o=.d) $(APP_OBJS:.o=.d)
