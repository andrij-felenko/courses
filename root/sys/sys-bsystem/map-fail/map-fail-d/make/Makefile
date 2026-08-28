# Makefile
CC      := arm-none-eabi-gcc
CXX     := arm-none-eabi-g++
LDSCRIPT := linker/STM32F401RETx_FLASH.ld

LDFLAGS := -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16
LDFLAGS += -T$(LDSCRIPT)
LDFLAGS += -Wl,-Map=$(BUILD_DIR)/firmware.map,--cref
LDFLAGS += -Wl,--gc-sections
LDFLAGS += -Wl,--print-memory-usage

$(BUILD_DIR)/firmware.elf: $(OBJS)
	$(CC) $(OBJS) $(LDFLAGS) -o $@
