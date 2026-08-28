# Головний Makefile
all: bin/app

# Включення фрагментів описів модулів
include lib/module.mk
include src/module.mk

# Лінкування єдиного кінцевого бінарника
bin/app: $(LIB_OBJS) $(SRC_OBJS)
	@mkdir -p $(@D)
	$(CC) $(LDFLAGS) $^ $(LDLIBS) -o $@
