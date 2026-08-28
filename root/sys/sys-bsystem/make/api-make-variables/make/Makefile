# 1. Заміна підрядка: $(subst from,to,text)
SRC_FIX := $(subst bad,good,src/bad_module.c)
# Значення: src/good_module.c

# 2. Заміна за шаблоном: $(patsubst pattern,replacement,text)
OBJS := $(patsubst src/%.c,build/%.o,src/main.c src/net.c)
# Значення: build/main.o build/net.o

# Короткий еквівалент patsubst через substitution reference:
OBJS_SHORT := $(SRCS:src/%.c=build/%.o)

# 3. Видалення зайвих початкових, кінцевих і повторюваних пробілів: $(strip string)
CLEAN_FLAGS := $(strip   -O2    -Wall    -g   )
# Значення: -O2 -Wall -g

# 4. Пошук входження підрядка: $(findstring find,in)
HAS_DEBUG := $(findstring DEBUG,$(CFLAGS))
# Якщо підрядок знайдено, повертає його значення, інакше — порожній рядок

# 5. Фільтрація елементів списку за шаблоном: $(filter pattern...,text)
HEADERS := $(filter %.h %.hpp,$(ALL_PROJECT_FILES))

# 6. Виключення елементів списку за шаблоном: $(filter-out pattern...,text)
NON_TEST_SRCS := $(filter-out %_test.c %_bench.c,$(ALL_C_SRCS))

# 7. Лексикографічне сортування зі знищенням дублікатів: $(sort list)
UNIQUE_INCLUDE_DIRS := $(sort $(dir $(ALL_OBJS)))

# 8. Вибір конкретного слова або підрахунок слів:
FIRST_WORD := $(firstword $(SRCS))
LAST_WORD  := $(lastword $(SRCS))
NTH_WORD   := $(word 2,$(SRCS))
WORD_COUNT := $(words $(SRCS))
