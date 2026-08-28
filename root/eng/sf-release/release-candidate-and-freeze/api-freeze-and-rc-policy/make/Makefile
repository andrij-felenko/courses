# Видалення абсолютних шляхів файлової системи хоста з налагоджувальних секцій DWARF
CFLAGS += -ffile-prefix-map=$(WORKSPACE_DIR)=.
CFLAGS += -fmacro-prefix-map=$(WORKSPACE_DIR)=.
CFLAGS += -fdebug-prefix-map=$(WORKSPACE_DIR)=.

# Заборона використання недетермінованих макросів часу та дати
CFLAGS += -Werror=date-time

# Фіксація порядку секцій лінкером для усунення випадкових перестановок
LDFLAGS += -Wl,--sort-section=alignment
LDFLAGS += -Wl,--build-id=none
