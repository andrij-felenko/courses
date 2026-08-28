# У конфізі — тільки ПОСИЛАННЯ на секрет, ніколи саме значення.
manifest = {
    "db_host": "prod-db.internal",                  # звичайний конфіг — так і лежить у файлі
    "db_password": {"secret": "dh/db/password"},    # секрет — лише адреса у сховищі
}

# На старті резолвер міняє посилання на справжнє значення.
def resolve(m, store):
    return {
        "db_host": m["db_host"],
        "db_password": store.get(m["db_password"]["secret"]),  # значення лише тут, у пам'яті
    }
# db_password не існує ні в git, ні в образі — тільки в поверненій структурі, тільки після старту.
