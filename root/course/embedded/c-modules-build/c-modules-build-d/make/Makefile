CC      = arm-none-eabi-gcc
CFLAGS  = -Os -Wall -Wextra -MMD -MP -DBOARD_V2
SRCS    = main.c led.c uart.c sensor.c
OBJS    = $(SRCS:.c=.o)          # список .o, зроблений заміною .c→.o

firmware.elf: $(OBJS)            # образ залежить від УСІХ об'єктних файлів
	$(CC) $(CFLAGS) $^ -o $@    # $^ — усі .o; $@ — firmware.elf

%.o: %.c                        # ШАБЛОН: будь-який .o з однойменного .c
	$(CC) $(CFLAGS) -c $< -o $@ # $< — конкретний .c; $@ — конкретний .o

-include $(OBJS:.o=.d)          # втягнути авто-залежності (.d поряд з кожним .o)

clean:
	rm -f $(OBJS) $(OBJS:.o=.d) firmware.elf
