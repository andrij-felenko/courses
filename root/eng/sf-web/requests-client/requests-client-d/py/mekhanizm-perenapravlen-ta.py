response = requests.post(
    "http://example.com/login",
    data={"user": "alice"},
    allow_redirects=True
)

# Якщо сервер відповів 301 на HTTPS-версію, response містить фінальну відповідь
print(response.status_code) # 200
print(response.url)         # 'https://example.com/dashboard'

# Історія перенаправлень зберігається у вигляді ланцюжка
for prev in response.history:
    print(f"Крок: {prev.status_code} -> {prev.headers.get('Location')}")
