import urllib.parse

raw_url = "https://api.example.com:8443/v1/search?query=blue%20sky&category=books#top"

# 1. Розбір URL на компоненти
# Рекомендується urlsplit замість застарілого urlparse (не відокремлює params у шляху)
res = urllib.parse.urlsplit(raw_url)

print(f"Схема:    {res.scheme}")     # https
print(f"Хост:     {res.hostname}")   # api.example.com
print(f"Порт:     {res.port}")       # 8443
print(f"Шлях:     {res.path}")       # /v1/search
print(f"Запит:    {res.query}")      # query=blue%20sky&category=books
print(f"Фрагмент: {res.fragment}")   # top

# 2. Розбір рядка запиту в словник
params = urllib.parse.parse_qs(res.query)
print(f"Параметри: {params}")
# Виведе: {'query': ['blue sky'], 'category': ['books']} (значення автоматично розкодовано)

# 3. Модифікація та зворотне збирання
params['query'] = ['C++ & Python']
params['page'] = ['1']

# Кодування параметрів за правилами RFC 3986 (quote_via=urllib.parse.quote)
new_query = urllib.parse.urlencode(params, doseq=True, quote_via=urllib.parse.quote)

# Збирання URL назад
new_url = urllib.parse.urlunsplit((
    res.scheme,
    res.netloc,
    res.path,
    new_query,
    res.fragment
))
print(f"Новий URL: {new_url}")
# https://api.example.com:8443/v1/search?query=C%2B%2B%20%26%20Python&category=books&page=1#top
