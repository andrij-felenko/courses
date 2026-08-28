# Антипатерн (SC2181):
run_backup
if [ $? -ne 0 ]; then
    echo "Збій!"
fi

# Ідіоматична перевірка:
if ! run_backup; then
    echo "Збій!"
fi
