# Makefile внутрішнього збирання релізного релінк-пакета

CC = arm-none-eabi-gcc
OBJCOPY = arm-none-eabi-objcopy
STRIP = arm-none-eabi-strip

CFLAGS = -mcpu=cortex-m4 -mthumb -O2 -fvisibility=hidden \
         -ffunction-sections -fdata-sections -Wall

all: relink_package

# Збирання пропрієтарного об'єктного файлу
proprietary_engine.o: proprietary_engine.c
	$(CC) $(CFLAGS) -c $< -o $@
	$(STRIP) --strip-debug $@
	$(OBJCOPY) --localize-hidden $@

# Формування комплекту для передачі клієнту
relink_package: proprietary_engine.o
	mkdir -p dist_relink_kit/obj
	mkdir -p dist_relink_kit/lgpl_src
	mkdir -p dist_relink_kit/scripts
	cp proprietary_engine.o dist_relink_kit/obj/
	cp -r ../submodules/lgpl_codec/* dist_relink_kit/lgpl_src/
	cp linker_script.ld dist_relink_kit/scripts/
	cp Makefile.customer dist_relink_kit/Makefile
	cp README_RELINK.txt dist_relink_kit/
	tar -czf customer_relink_bundle.tar.gz dist_relink_kit
