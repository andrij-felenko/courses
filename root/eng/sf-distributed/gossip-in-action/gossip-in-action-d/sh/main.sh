# Перевірка версій метаданих та лічильників пульсу кожного вузла Cassandra
nodetool gossipinfo

# Перевірка розподілу токенів та відповідності адрес
nodetool ring

# Детальний стан членства та протоколу в Consul
consul members -detailed

# Моніторинг затримок та втрат пліток у Memberlist
# Метрика: memberlist.gossip.messages_received
# Метрика: memberlist.health.score (LWL рахунок)
