import requests

# 1. Створення сирого декларативного запиту
req = requests.Request(
    method="POST",
    url="https://api.example.com/v1/items",
    params={"category": "електроніка", "limit": 10},
    json={"name": "Датчик тиску", "price": 450.0},
    headers={"Accept": "application/json", "X-Custom-Trace": "9a7f"},
    auth=("admin", "secret_pass")
)

# 2. Сесія виконує підготовку та нормалізацію
session = requests.Session()
prepared = session.prepare_request(req)

# Огляд сформованого зліпка запиту
print(prepared.method)   # 'POST'
print(prepared.url)      # 'https://api.example.com/v1/items?category=%D0%B5%D0%BB%D0%B5%D0%BA%D1%82%D1%80%D0%BE%D0%BD%D1%96%D0%BA%D0%B0&limit=10'
print(prepared.headers)  # CaseInsensitiveDict з автоматично доданими Content-Type, Content-Length, Authorization
print(prepared.body)     # b'{"name": "\xd0\x94\xd0\xb0\xd1\x82\xd1\x87\xd0\xb8\xd0\xba \xd1\x82\xd0\xb8\xd1\x81\xd0\xba\xd1\x83", "price": 450.0}'
