# Перевірка моделі зареєстрованої плати
cat /proc/device-tree/model
# Custom Industrial Carrier Board for Raspberry Pi CM4

# Перевірка сумісності термодатчика
cat /proc/device-tree/soc/i2c@7e804000/sensor@48/compatible
# ti,tmp102

# Зворотне декомпілювання активного дерева ядра у вихідний текст
dtc -I fs -O dts /proc/device-tree > current-running-tree.dts
