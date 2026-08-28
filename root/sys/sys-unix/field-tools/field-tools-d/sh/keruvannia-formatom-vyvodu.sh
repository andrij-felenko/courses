# users.txt (ID, Ім'я)
# 101 John
# 102 Alice
# 103 Bob

# departments.txt (ID, Відділ)
# 101 Engineering
# 103 Marketing

# Left Join із заміною відсутніх відділів на 'NONE':
join -1 1 -2 1 -a 1 -e 'NONE' -o 1.1,1.2,2.2 users.txt departments.txt
# Вивід:
# 101 John Engineering
# 102 Alice NONE
# 103 Bob Marketing
