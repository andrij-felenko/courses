# Перевірка статусу BGP-сусідів
birdc show protocols

# Перевірка активних BFD-сесій та виміряної затримки
birdc show bfd sessions

# Перегляд експортованих маршрутів до конкретного комутатора
birdc show route export to_leaf1

# Детальна інформація про маршрут з усіма BGP-атрибутами
birdc show route for 198.51.100.1/32 all

# Динамічне перечитування конфігурації без переривання сесій
birdc configure
