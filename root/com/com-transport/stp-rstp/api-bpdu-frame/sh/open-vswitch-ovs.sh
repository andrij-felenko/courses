# Створення віртуального комутатора
ovs-vsctl add-br ovs-br0

# Увімкнення протоколу RSTP
ovs-vsctl set Bridge ovs-br0 rstp_enable=true

# Налаштування пріоритету Bridge ID (4096 = 0x1000)
ovs-vsctl set Bridge ovs-br0 status:rstp_priority=4096

# Виведення детальної інформації про порти RSTP
ovs-vsctl get Bridge ovs-br0 status
ovs-appctl rstp/show ovs-br0
