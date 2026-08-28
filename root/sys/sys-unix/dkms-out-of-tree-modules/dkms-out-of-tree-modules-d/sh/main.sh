PACKAGE_NAME="my_device_driver"
PACKAGE_VERSION="1.0"

# Описуємо, скільки модулів збирається і як вони називаються
BUILT_MODULE_NAME[0]="my_device"
# Вказуємо шлях, куди встановити зібраний модуль всередині /lib/modules/...
DEST_MODULE_LOCATION[0]="/kernel/drivers/misc"

# Опціонально: автоматично встановлювати при завантаженні системи/оновленні ядра
AUTOINSTALL="yes"

# Команда для збирання. Якщо не вказана, за замовчуванням виконується make
MAKE[0]="make -C $kernel_source_dir M=$dkms_tree/$PACKAGE_NAME/$PACKAGE_VERSION/build"
# Команда для очищення
CLEAN="make -C $kernel_source_dir M=$dkms_tree/$PACKAGE_NAME/$PACKAGE_VERSION/build clean"
