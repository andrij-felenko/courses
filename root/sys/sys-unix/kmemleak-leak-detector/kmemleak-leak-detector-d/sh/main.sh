# Примусово запустити синхронне сканування пам'яті
echo scan > /sys/kernel/debug/kmemleak

# Очистити список поточних знайдених витоків (скинути базлайн)
echo clear > /sys/kernel/debug/kmemleak

# Змінити інтервал фонового сканування на 300 секунд
echo scan=300 > /sys/kernel/debug/kmemleak

# Вимкнути фонове автоматичне сканування
echo scan=off > /sys/kernel/debug/kmemleak

# Повністю вимкнути Kmemleak у працюючій системі
echo off > /sys/kernel/debug/kmemleak
