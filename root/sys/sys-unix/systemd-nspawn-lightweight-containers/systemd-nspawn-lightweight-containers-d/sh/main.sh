# Перелік усіх активних контейнерів та віртуальних машин
machinectl list

# Отримання детального статусу та дерева процесів контейнера
machinectl status web-node1

# Відкриття інтерактивної консолі (PTY) усередині контейнера
machinectl shell web-node1

# Примусове завершення роботи контейнера
machinectl poweroff web-node1
