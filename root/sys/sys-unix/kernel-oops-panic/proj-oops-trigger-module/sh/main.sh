# Створення файла інструкцій збирання Makefile
cat << 'EOF' > Makefile
obj-m += oops_trigger_mod.o
all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
EOF

# Компіляція модуля ядра
make

# Завантаження згенерованого бінарного модуля .ko в ядро
sudo insmod oops_trigger_mod.ko

# Перевірка реєстрації та прав доступу до procfs файлу
ls -l /proc/oops_trigger

# 1. Тест м'якого збою Oops (завершується лише процес sh):
sudo sh -c 'echo null > /proc/oops_trigger'

# Аналіз отриманого логу у системному журналі dmesg
dmesg | tail -n 25

# 2. Тест фатальної паніки в контексті переривання (викликає Паніку та Kdump):
sudo sh -c 'echo irq_null > /proc/oops_trigger'
