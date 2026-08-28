cache = {}

def get_user(user_id):
    if user_id in cache:            # тактика: кеш заради швидкодії
        return cache[user_id]
    user = db.query_user(user_id)   # дорогий похід у базу
    cache[user_id] = user
    return user

def rename_user(user_id, name):
    db.update_user(user_id, name)
    # А ось прихована ціна: без цього рядка кеш віддаватиме старе ім'я.
    cache.pop(user_id, None)        # інвалідація — борг, який породив кеш
