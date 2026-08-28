# Встановлення необхідних системних пакетів у середовищі Debian / Ubuntu / Raspberry Pi OS
sudo apt-get update && sudo apt-get install -y libcamera-dev pkg-config g++

# Компіляція вихідного файлу з автоматичним підключенням шляхів та прапорців лінкування
g++ -std=c++17 libcamera_capture.cpp -o libcamera_capture $(pkg-config --cflags --libs libcamera)

# Надання прав доступу до відеовузлів користувачу (якщо не налаштовано udev-правила)
sudo usermod -a -G video,render $USER

# Запуск скомпільованого бінарного файлу
./libcamera_capture
