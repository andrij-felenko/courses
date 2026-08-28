# ── Makefile для прошивки під ARM Cortex-M (arm-none-eabi-gcc) ──
# Збирає всі .c у build/, лінкує в .elf, робить .bin і .hex, заливає.

# 1. Тулчейн: префікс і власне інструменти.
PREFIX  = arm-none-eabi-          # спільний початок імен усіх утиліт крос-тулчейну
CC      = $(PREFIX)gcc            # компілятор (він же кличе лінкер на кроці лінкування)
OBJCOPY = $(PREFIX)objcopy        # витягує сирий образ (.bin/.hex) з .elf
SIZE    = $(PREFIX)size           # показує, скільки зайняли .text/.data/.bss

# 2. Що збираємо і з чого — ЄДИНЕ джерело правди.
TARGET  = firmware               # базове ім'я образу (буде firmware.elf, .bin, .hex)
BUILD   = build                  # окрема тека для всього згенерованого
SRCS    = main.c led.c uart.c sensor.c startup_stm32f407.s
# кожен новий модуль додаєте САМЕ сюди — і більше ніде

# 3. Виводимо список об'єктних файлів із SRCS: замінюємо суфікс і кладемо в build/.
#    main.c → build/main.o, startup_stm32f407.s → build/startup_stm32f407.o
OBJS    = $(addprefix $(BUILD)/,$(patsubst %.c,%.o,$(patsubst %.s,%.o,$(SRCS))))

# 4. Прапорці збірки — усе, що стосується ЦЬОГО чипа, живе тут.
CPU     = -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16
CFLAGS  = $(CPU) -Os -g3 -Wall -Wextra -ffunction-sections -fdata-sections
CFLAGS += -MMD -MP                       # ← попутно генерувати .d із залежностями
CFLAGS += -DSTM32F407xx -Iinc            # макрос для HAL і тека із заголовками

# 5. Прапорці лінкування — компонувальний скрипт, бібліотеки, викидання зайвого.
LDSCRIPT = STM32F407VGTx_FLASH.ld        # карта пам'яті чипа (дає виробник)
LDFLAGS  = $(CPU) -T$(LDSCRIPT) --specs=nano.specs --specs=nosys.specs
LDFLAGS += -Wl,--gc-sections             # викинути невживані секції (economy флешу)
LDFLAGS += -Wl,-Map=$(BUILD)/$(TARGET).map   # карта пам'яті для розбору «що скільки з'їло»

# 6. Бібліотеки — СТРОГО в кінці команди лінкування (див. пастку нижче).
LDLIBS   = -lm                           # математична libm (sinf, sqrtf, …)

# ── Цілі ──────────────────────────────────────────────────────────

all: $(BUILD)/$(TARGET).bin $(BUILD)/$(TARGET).hex   # ← ціль за замовчуванням

# Лінкування: усі .o + бібліотеки → .elf. $^ підставить весь список OBJS.
$(BUILD)/$(TARGET).elf: $(OBJS)
	$(CC) $(LDFLAGS) $^ $(LDLIBS) -o $@
	$(SIZE) $@                            # одразу показати зайнятий обсяг

# Сирий двійковий образ для прошивальника (без ELF-обгортки).
$(BUILD)/$(TARGET).bin: $(BUILD)/$(TARGET).elf
	$(OBJCOPY) -O binary $< $@

# Intel HEX — інший формат образу, який їдять багато прошивальників.
$(BUILD)/$(TARGET).hex: $(BUILD)/$(TARGET).elf
	$(OBJCOPY) -O ihex $< $@

# Шаблон: будь-який build/X.o з X.c. | $(BUILD) — теку створити ПЕРШОЮ.
$(BUILD)/%.o: %.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

# Той самий шаблон для асемблера (стартовий код виробника — часто .s).
$(BUILD)/%.o: %.s | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

# Створити теку build/. Order-only (за |), тож її час не тягне перезбірку.
$(BUILD):
	mkdir -p $(BUILD)

flash: $(BUILD)/$(TARGET).elf            # залити образ у чип через st-flash/openocd
	st-flash write $(BUILD)/$(TARGET).bin 0x08000000

clean:                                    # стерти все згенероване одним махом
	rm -rf $(BUILD)

.PHONY: all flash clean                   # це дієслова, не файли — робити ЗАВЖДИ

# 7. Затягнути згенеровані залежності від заголовків. Дефіс = «нема .d — мовчи».
-include $(OBJS:.o=.d)
