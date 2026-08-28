# Твій «продукт зв'язку» — це чужий HTTP-виклик.
# Уся телефонія за ним: оператори, залізо, маршрути — сховані.
from twilio.rest import Client

client = Client(account_sid, auth_token)

call = client.calls.create(
    to="+380671234567",       # кому дзвонимо
    from_="+15551234567",     # з якого номера (виданого сервісом)
    url="https://example.com/say-hello.xml",  # що казати, коли піднімуть
)

print(call.sid)  # ідентифікатор дзвінка — можна стежити за станом
