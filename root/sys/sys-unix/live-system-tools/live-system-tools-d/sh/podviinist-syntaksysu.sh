# 1. Стандарт POSIX / System V: опції ПОЧИНАЮТЬСЯ з одного дефісу
$ ps -ef
$ ps -u root -l

# 2. Стандарт BSD: опції записуються БЕЗ ДЕФІСУ
$ ps aux
$ ps axms

# 3. Довгі опції GNU: починаються з двох дефісів
$ ps --forest --User root
