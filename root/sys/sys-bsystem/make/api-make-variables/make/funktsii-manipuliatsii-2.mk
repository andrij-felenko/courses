# 1. Виділення частини каталогу зі збереженням слеша: $(dir names...)
DIRS := $(dir src/core/engine.c include/config.h top.c)
# Значення: src/core/ include/ ./

# 2. Виділення імені файлу без каталогу: $(notdir names...)
FILES := $(notdir src/core/engine.c include/config.h)
# Значення: engine.c config.h

# 3. Виділення суфікса (розширення): $(suffix names...)
EXTENSIONS := $(suffix src/main.c src/util.cpp include/types.h)
# Значення: .c .cpp .h

# 4. Виділення базового імені без суфікса: $(basename names...)
BASE_NAMES := $(basename src/main.c include/types.h)
# Значення: src/main include/types

# 5. Додавання префікса або суфікса до кожного елемента списку:
INC_FLAGS := $(addprefix -I,include /opt/sdk/include)
# Значення: -Iinclude -I/opt/sdk/include

OBJ_LIST := $(addsuffix .o,main util network)
# Значення: main.o util.o network.o

# 6. Читання реальної файлової системи за маскою (globbing): $(wildcard pattern...)
FOUND_SOURCES := $(wildcard src/*.c src/drivers/*.c)

# 7. Обчислення абсолютних та канонічних шляхів:
ABS_PATH := $(abspath ../common/include)
# Розгортає відносні точки без перевірки існування файлу

REAL_PATH := $(realpath /etc/os-release)
# Розгортає всі символічні посилання та повертає канонічний шлях
