# Перелік усіх активних цільових юнітів у пам'яті PID 1
systemctl list-units --type=target

# Перелік усіх встановлених таргетів (включаючи неактивні)
systemctl list-unit-files --type=target

# Відображення прямого дерева залежностей для вказаного таргета
systemctl list-dependencies multi-user.target

# Відображення зворотного дерева залежностей (хто залежить від цього таргета)
systemctl list-dependencies --reverse network.target
