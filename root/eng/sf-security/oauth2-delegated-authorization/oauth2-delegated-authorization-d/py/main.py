def delete_photo_handler(request, photo_id):
    # Отримуємо права, зашиті в токен доступу
    token_scopes = request.auth.get("scope", "").split()
    
    # Перевіряємо, чи має клієнт право на видалення
    if "photos.delete" not in token_scopes:
        return {"error": "insufficient_scope", "status": 403}
        
    db.photos.delete(photo_id)
    return {"status": "success"}
