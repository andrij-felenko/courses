# Запит запису A з увімкненим DNSSEC (опція +dnssec встановлює прапорець DO=1)
dig +dnssec +multiline example.com A @8.8.8.8

# Запит відкритих ключів DNSKEY зони
dig +dnssec +multiline example.com DNSKEY @8.8.8.8

# Запит запису DS у батьківського сервера TLD
dig +dnssec +multiline example.com DS @a.gtld-servers.net

# Повна автономна валідація від кореневого якоря утилітою delv
delv @8.8.8.8 www.example.com A
