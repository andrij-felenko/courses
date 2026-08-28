import json
import urllib
import urllib2
import cookielib

# Створення сховища cookie
cookie_jar = cookielib.CookieJar()
cookie_processor = urllib2.HTTPCookieProcessor(cookie_jar)

# Налаштування менеджера автентифікації
password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
password_mgr.add_password(None, "https://api.example.com", "user", "secret")
auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr)

# Збирання конвеєра відкриття
opener = urllib2.build_opener(cookie_processor, auth_handler)
urllib2.install_opener(opener)

# Підготовка тіла та заголовків
payload = json.dumps({"query": "status"}).encode("utf-8")
request = urllib2.Request(
    "https://api.example.com/v1/data",
    data=payload,
    headers={
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
        "User-Agent": "CustomApp/1.0"
    }
)

# Виконання запиту та ручне перехоплення статус-кодів
try:
    response = opener.open(request, timeout=10)
    body = response.read()
except urllib2.HTTPError as exc:
    print(f"Помилка HTTP {exc.code}: {exc.read()}")
except urllib2.URLError as exc:
    print(f"Помилка мережі: {exc.reason}")
