chmod +x log_analyzer.awk

# 1. Прямий аналіз кількох лог-файлів одночасно:
./log_analyzer.awk /var/log/nginx/access.log /var/log/nginx/access.log.1

# 2. Потоковий аналіз стиснених архівів gzip без розпакування на диск:
zcat /var/log/nginx/access.log.*.gz | ./log_analyzer.awk

# 3. Аналіз потоку в реальному часі через tail:
tail -n 50000 /var/log/nginx/access.log | ./log_analyzer.awk

# 4. Фільтрація логів за певний часовий інтервал перед аналізом:
awk '$4 ~ /^\[25\/Aug\/2026:14:/' /var/log/nginx/access.log | ./log_analyzer.awk
