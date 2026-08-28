# 1. Запуск застосунку суворо на Вузлі 0 (і ядра, і пам'ять)
numactl --cpunodebind=0 --membind=0 ./my_database_server

# 2. Запуск із рівномірним чергуванням пам'яті по всіх вузлах
numactl --interleave=all ./scientific_simulation

# 3. Виділення пам'яті на швидкому вузлі з можливістю виходу за його межі
numactl --preferred=0 ./web_backend

# 4. Перевірка апаратної топології системи
numactl --hardware
