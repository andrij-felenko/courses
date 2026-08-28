# Безпечний патерн виконання операції з секретом
{
    # Тимчасово вимикаємо трасування, якщо воно було активне
    { set +x; } 2>/dev/null
    
    # Виконуємо операцію з секретом у закритому режимі
    curl -sSf -H "Authorization: Bearer ${VAULT_SECRET_TOKEN}" \
         "https://vault.internal.net/v1/secret/data/db" > /tmp/db_creds.json
         
    # Відновлюємо трасування, якщо необхідно
    set -x
}
