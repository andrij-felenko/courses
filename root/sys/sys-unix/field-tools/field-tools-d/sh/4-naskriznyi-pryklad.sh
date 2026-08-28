#!/bin/sh
export LC_ALL=C

# 1. Витягуємо IP-адреси з журналу, рахуємо кількість запитів і сортуємо за IP:
# tr -s ' ' стискає пробіли -> cut бере першу колонку (IP) -> sort | uniq -c рахує частоту
cut -d' ' -f1 access.log | LC_ALL=C sort | uniq -c | tr -s ' ' | sed 's/^ //' | cut -d' ' -f1,2 > ip_counts.txt
# Формат ip_counts.txt: КІЛЬКІСТЬ IP

# 2. Формуємо файл IP -> КІЛЬКІСТЬ, відсортований за IP:
cut -d' ' -f2,1 --output-delimiter=',' ip_counts.txt | LC_ALL=C sort -t, -k1,1 > ip_by_key.csv

# 3. З'єднуємо з таблицею країн geoip.csv (IP,COUNTRY) через join:
# Результат: IP,КІЛЬКІСТЬ,COUNTRY
join -t, -1 1 -2 1 -o 1.1,1.2,2.2 ip_by_key.csv <(LC_ALL=C sort -t, -k1,1 geoip.csv) > ip_with_geo.csv

# 4. Знаходимо всі IP, яких НЕМАЄ в білому списку whitelist.txt, за допомогою comm:
# comm -23 вибирає елементи, присутні тільки в першому файлі
comm -23 <(cut -d, -f1 ip_with_geo.csv | LC_ALL=C sort) \
         <(LC_ALL=C sort whitelist.txt) > suspicious_ips.txt

# 5. Серіалізуємо список підозрілих IP в один рядок для виклику блокування iptables:
BLOCKED_LIST=$(paste -sd, suspicious_ips.txt)
echo "Підозрілі адреси для блокування: ${BLOCKED_LIST}"
