# 1. Завантаження системного оточення тулчейну ESP-IDF
. $IDF_PATH/export.sh

# 2. Встановлення цільового чипа без відкриття діалогів
idf.py set-target esp32s3

# 3. Збірка прошивки з перевіркою попереджень як помилок
idf.py -B build_ci \
       -DSDKCONFIG_DEFAULTS="sdkconfig.defaults;sdkconfig.ci" \
       build
