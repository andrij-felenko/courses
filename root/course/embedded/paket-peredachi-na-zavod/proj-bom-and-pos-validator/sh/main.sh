# Автоматична верифікація перед створенням релізного архіву
./bom_cpl_validator 02_SMT_Assembly/BOM_Production.csv 02_SMT_Assembly/Centroid_PickAndPlace.csv
RETVAL=$?

if [ $RETVAL -ne 0 ]; then
    echo "[ПОМИЛКА] Валідація не пройшла! Виявлено розбіжності між BOM і CPL."
    echo "Архів релізу НЕ буде створено."
    exit 1
fi

echo "[УСПІХ] Усі компоненти узгоджені. Створюємо архів виробничого пакета..."
zip -r "RELEASE_PACKAGE_$(date +%Y%m%d).zip" 01_PCB_Fabrication 02_SMT_Assembly 03_Firmware_Provisioning 04_Testing_QA SHA256SUMS.txt
