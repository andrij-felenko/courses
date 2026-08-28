# 1. Умовна функція: $(if condition,then-part[,else-part])
# Умова вважається істинною, якщо після розгортання вона містить хоча б один непорожній символ
OUTPUT_DIR := $(if $(DEBUG),build/debug,build/release)

# 2. Логічні комбінатори: $(or a,b,c), $(and a,b)
TARGET_ARCH := $(or $(ARCH),$(TARGET_CPU),x86_64)

# 3. Цикл обходу списку зі створенням локальної змінної: $(foreach var,list,text)
INCLUDE_FLAGS := $(foreach dir,$(INCLUDE_DIRS),-I$(dir))

# 4. Виклик команди операційної системи у фазі читання: $(shell command)
# Команда виконується один раз під час підстановки; символи \n замінюються на пробіли
GIT_REVISION := $(shell git rev-parse --short HEAD 2>/dev/null || echo "release")
PKG_LIBS     := $(shell pkg-config --libs libpng)

# 5. Генерація діагностичних повідомлень у вивід збірки:
$(info [INFO] Збірка бінарного файлу для цілі $(TARGET_ARCH))
$(warning [WARN] Змінна OPTIMIZATION_LEVEL не задана, використовується -O2)
# $(error [FATAL] Не знайдено сумісний компілятор C++) — негайно перериває роботу Make

# 6. Інспекція походження змінної: $(origin variable_name)
# Повертає: 'undefined', 'default', 'environment', 'file', 'command line', 'override', 'automatic'
IS_OVERRIDDEN := $(filter command line,$(origin CFLAGS))

# 7. Інспекція типу присвоєння: $(flavor variable_name)
# Повертає: 'undefined', 'recursive' (для =), 'simple' (для := та ::=)
VAR_KIND := $(flavor CFLAGS)

# 8. Динамічна оцінка та ін'єкція правил у граф: $(eval text)
# Дозволяє генерувати правила збірки на льоту всередині циклів foreach
define GENERATE_RULE
build/$(1).o: src/$(1).c
	$$(CC) $$(CFLAGS) -c $$< -o $$@
endef

$(foreach mod,engine parser lexer,$(eval $(call GENERATE_RULE,$(mod))))
