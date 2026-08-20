# 📋 Анатомія SOAP: конверт, повідомлення про помилки та структура WSDL

### Простір імен і структура конверта: порівняння SOAP 1.1 та SOAP 1.2

Протокол SOAP передає структуровані повідомлення у вигляді XML-документа, чий кореневий елемент завжди зветься `<Envelope>` («конверт»). Конверт належить до фіксованого простору імен, який однозначно визначає версію протоколу та правила його інтерпретації синтаксичним аналізатором. Кожен вузол мережі, що отримує повідомлення, спочатку звіряє простір імен кореневого елемента: якщо версія не підтримується, сервер зобов'язаний негайно припинити розбір і повернути спеціалізовану помилку несумісності версій.

| Характеристика | SOAP 1.1 (W3C Note 2000) | SOAP 1.2 (W3C Recommendation 2003) |
| :--- | :--- | :--- |
| **Простір імен конверта** | `http://schemas.xmlsoap.org/soap/envelope/` | `http://www.w3.org/2003/05/soap-envelope` |
| **MIME-тип HTTP-запиту** | `text/xml; charset=utf-8` | `application/soap+xml; charset=utf-8` |
| **Заголовок HTTP-дії** | Окремий HTTP-заголовок `SOAPAction: "action_uri"` | Параметр `action="action_uri"` у заголовку `Content-Type` |
| **Значення mustUnderstand** | Числа `"1"` (обов'язково) або `"0"` (ні) | Булеві літерали `"true"`, `"false"`, `"1"`, `"0"` |
| **Атрибут цільового вузла** | `actor="URI"` | `role="URI"` (або стандартні псевдоніми) |
| **Кореневі елементи помилки** | `<faultcode>`, `<faultstring>`, `<detail>` | `<Code>`, `<Reason>`, `<Detail>` |
| **Код статусу помилки клієнта** | Завжди `HTTP 500 Internal Server Error` | Дозволено `HTTP 400 Bad Request` |

У версії SOAP 1.1 виклик обов'язково супроводжувався окремим службовим HTTP-заголовком `SOAPAction`. Цей заголовок дозволяв маршрутизаторам, фаєрволам і проксі-серверам визначити цільову дію всередині запиту без розбору великого XML-тіла. У версії SOAP 1.2 цей заголовок ліквідували як надлишковий і включили параметр `action` безпосередньо у значення стандартного заголовка `Content-Type`.

#### Базовий шаблон конверта SOAP 1.1

У версії SOAP 1.1 кореневий елемент `<Envelope>` містить опційний елемент `<Header>` і обов'язковий елемент `<Body>`. Будь-який вміст поза цими елементами вважається синтаксичною помилкою.

```xml
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Header>
    <!-- Необов'язкові службові метадані, безпека, маршрутизація, контекст транзакцій -->
  </soap:Header>
  <soap:Body>
    <!-- Обов'язкове корисне навантаження або стандартизований блок помилки <soap:Fault> -->
  </soap:Body>
</soap:Envelope>
```

#### Базовий шаблон конверта SOAP 1.2

У версії SOAP 1.2 правила структуризації збереглися, проте змінилися простори імен та вимоги до обробки окремих службових атрибутів.

```xml
<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap12:Header>
    <!-- Необов'язкові блоки заголовків версії 1.2 -->
  </soap12:Header>
  <soap12:Body>
    <!-- Обов'язкове корисне навантаження або елемент <soap12:Fault> -->
  </soap12:Body>
</soap12:Envelope>
```

---

### Атрибути блоків заголовка: `mustUnderstand`, `actor` та `role`

Елемент `<Header>` слугує контейнером для розширюваних модулів інфраструктури. Кожен безпосередній дочірній елемент заголовка називається блоком заголовка (Header Block). Блоки заголовка можуть нести інформацію про цифрові підписи, ідентифікатори користувачів, термін дійсності повідомлення або маршрути доставки. Щоб керувати поведінкою обробників, протокол визначає три ключові службові атрибути.

#### 1. Атрибут обов'язкової обробки: `mustUnderstand`

Атрибут `mustUnderstand` гарантує, що критично важливі правила обробки не будуть проігноровані проміжним або кінцевим сервером. Це центральний механізм забезпечення надійності в гетерогенних мережах.

- Якщо елемент заголовка містить `mustUnderstand="1"` (або `"true"` у версії 1.2), вузол, якому адресовано цей блок, зобов'язаний повністю розуміти семантику цього блоку та успішно виконати всі пов'язані з ним дії.
- Якщо приймальний вузол не має встановленого плагіна, модуля або програмної логіки для обробки такого заголовка (наприклад, не вміє перевіряти заголовок цифрового підпису нового типу), він зобов'язаний негайно перервати виконання всієї операції.
- Сервер не має права виконувати бізнес-логіку з тіла повідомлення, якщо хоча б один обов'язковий блок заголовка не був успішно розпізнаний. У відповідь формується стандартизоване повідомлення про помилку з кодом `soap:MustUnderstand`.
- Якщо атрибут відсутній або має значення `"0"` (`"false"`), вузол має право проігнорувати невідомий заголовок і продовжити виконання запиту.

#### 2. Атрибути адресації вузла: `actor` (SOAP 1.1) та `role` (SOAP 1.2)

Повідомлення SOAP рідко подорожує безпосередньо від клієнта до фінального коду обробки: на шляху можуть стояти шлюзи безпеки, корпоративні шини даних (ESB), проксі-сервери логування та аудиту. Атрибут адресації визначає, який саме вузол у ланцюжку передачі має зняти й опрацювати конкретний блок заголовка.

У специфікації SOAP 1.2 визначено три стандартні ролі:
1. `http://www.w3.org/2003/05/soap-envelope/role/next` — блок адресовано першому-ліпшому вузлу, який отримає це повідомлення наступним за чергою. Проміжний вузол зобов'язаний прочитати цей заголовок, виконати його інструкції і, якщо заголовок не призначений для подальшої ретрансляції, видалити його з конверта перед відправкою далі.
2. `http://www.w3.org/2003/05/soap-envelope/role/ultimateReceiver` — блок призначений виключно для кінцевого одержувача повідомлення, який виконує прикладну логіку. Усі проміжні шлюзи та маршрутизатори зобов'язані пропустити цей заголовок без змін, не намагаючись його обробляти чи валідувати. Якщо атрибут ролі не вказано явно, за замовчуванням застосовується саме ця роль.
3. `http://www.w3.org/2003/05/soap-envelope/role/none` — блок не призначений для прямої автоматичної обробки жодним вузлом у ланцюжку. Ця роль використовується для передачі спільних допоміжних даних (наприклад, сертифікатів або криптографічних ключів), на які посилаються інші заголовки через внутрішні URI-посилання.

#### 3. Атрибут `relay` (SOAP 1.2)

У версії SOAP 1.2 з'явився додатковий булевий атрибут `relay="true"`. Він вказує проміжному вузлу, що якщо блок заголовка, адресований ролі `next`, був успішно прочитаний, але не вимагав модифікації чи видалення, його слід зберегти в конверті та передати наступним вузлам ланцюжка.

---

### Стандартизовані звіти про помилки: елемент `<Fault>`

Будь-яка виняткова ситуація, що виникає під час синтаксичного аналізу, валідації заголовків або виконання бізнес-методу, повертається клієнту у вигляді спеціального дочірнього елемента `<Fault>` всередині `<Body>`. Якщо в повідомленні присутній `<Fault>`, він зобов'язаний бути єдиним дочірнім елементом тіла.

#### 1. Детальна структура Fault у SOAP 1.1

Специфікація SOAP 1.1 визначає чотири обов'язкові та додаткові елементи звіту про помилку:

```xml
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <soap:Fault>
      <faultcode>soap:Client</faultcode>
      <faultstring>Некоректний ідентифікатор банківського рахунку</faultstring>
      <faultactor>http://api.bank.example.com/payment-gateway</faultactor>
      <detail>
        <err:PaymentError xmlns:err="http://bank.example.com/errors">
          <err:Code>INVALID_ACCOUNT_FORMAT</err:Code>
          <err:Field>accountNumber</err:Field>
          <err:Reason>Номер рахунку повинен містити рівно 16 цифр стандарту IBAN</err:Reason>
        </err:PaymentError>
      </detail>
    </soap:Fault>
  </soap:Body>
</soap:Envelope>
```

Значення полів звіту SOAP 1.1:
- `<faultcode>` — кваліфіковане ім'я помилки (QName) для машинного аналізу. Стандарт вимагає використання однієї з чотирьох базових категорій:
  1. `soap:VersionMismatch` — сервер виявив простір імен конверта, який він не підтримує.
  2. `soap:MustUnderstand` — безпосередній заголовок з атрибутом `mustUnderstand="1"` не був розпізнаний сервером.
  3. `soap:Client` — повідомлення було неправильно сформоване клієнтом або містило неприпустимі дані. Повторна відправка такого самого запиту призведе до аналогічного збою.
  4. `soap:Server` — помилка сталася через внутрішній збій сервера або недоступність зовнішніх ресурсів (бази даних, стороннього API). Клієнт може повторити запит пізніше.
- `<faultstring>` — текст помилки для людини, який пояснює причину виникнення збою природною мовою.
- `<faultactor>` — необов'язковий URI-ідентифікатор конкретного мережевого вузла, на якому виникла помилка в ланцюжку посередників.
- `<detail>` — структурований XML-блок із прикладними даними про помилку. Стандарт вимагає, щоб елемент `<detail>` був присутній обов'язково, якщо помилка виникла під час виконання вмісту `<Body>`, і був відсутній, якщо збій стався під час аналізу заголовків `<Header>`.

#### 2. Детальна структура Fault у SOAP 1.2

У SOAP 1.2 структуру звіту про помилку суттєво переробили для підвищення модульності та багатомовності.

```xml
<soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <soap12:Fault>
      <soap12:Code>
        <soap12:Value>soap12:Sender</soap12:Value>
        <soap12:Subcode>
          <soap12:Value xmlns:bank="http://bank.example.com/faults">bank:AccountLocked</soap12:Value>
        </soap12:Subcode>
      </soap12:Code>
      <soap12:Reason>
        <soap12:Text xml:lang="uk-UA">Рахунок платника тимчасово заблоковано фінмоніторингом</soap12:Text>
        <soap12:Text xml:lang="en-US">The payer account is temporarily locked by compliance</soap12:Text>
      </soap12:Reason>
      <soap12:Node>http://api.bank.example.com/node-01</soap12:Node>
      <soap12:Role>http://www.w3.org/2003/05/soap-envelope/role/ultimateReceiver</soap12:Role>
      <soap12:Detail>
        <bank:LockInfo>
          <bank:ReasonCode>SUSPICIOUS_TRANSFER_VOLUME</bank:ReasonCode>
          <bank:LockTimestamp>2026-08-20T10:15:00Z</bank:LockTimestamp>
        </bank:LockInfo>
      </soap12:Detail>
    </soap12:Fault>
  </soap12:Body>
</soap12:Envelope>
```

Складові елементи Fault у SOAP 1.2:
- `<soap12:Code>` — ієрархічний код помилки. Містить обов'язковий елемент `<soap12:Value>` верхнього рівня (`soap12:Sender`, `soap12:Receiver`, `soap12:MustUnderstand`, `soap12:VersionMismatch`, `soap12:DataEncodingUnknown`) та необов'язковий вкладений `<soap12:Subcode>`, який дозволяє сервісам вказувати власні специфічні підкоди помилок без порушення базової класифікації.
- `<soap12:Reason>` — контейнер для повідомлень про помилку різними мовами через елементи `<soap12:Text>` з обов'язковим атрибутом `xml:lang`.
- `<soap12:Node>` — URI вузла, де виникла проблема (аналог `faultactor`).
- `<soap12:Role>` — роль, яку виконував вузол у момент збою.
- `<soap12:Detail>` — прикладний блок із довільними XML-елементами помилки.

---

### Повна структура мови опису контрактів: WSDL 1.1

Мова WSDL 1.1 відокремлює абстрактний опис структур даних та операцій від конкретних транспортних протоколів і фізичних адрес розташування сервера. Усі компоненти розміщуються всередині кореневого елемента `<wsdl:definitions>`.

```xml
<?xml version="1.0" encoding="utf-8"?>
<wsdl:definitions name="PaymentService"
    targetNamespace="http://bank.example.com/payments"
    xmlns:tns="http://bank.example.com/payments"
    xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
    xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema">

  <!-- 1. Рівень визначення типів даних (XSD-схеми) -->
  <wsdl:types>
    <xsd:schema targetNamespace="http://bank.example.com/payments"
                elementFormDefault="qualified">

      <!-- Елемент виклику операції (обгортка Wrapped) -->
      <xsd:element name="ProcessPayment">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="accountNumber" type="xsd:string" />
            <xsd:element name="amount" type="xsd:decimal" />
            <xsd:element name="currency" type="xsd:string" />
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>

      <!-- Елемент відповіді сервісу -->
      <xsd:element name="ProcessPaymentResponse">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="transactionId" type="xsd:string" />
            <xsd:element name="status" type="xsd:string" />
            <xsd:element name="timestamp" type="xsd:dateTime" />
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>

      <!-- Елемент прикладного звіту про помилку -->
      <xsd:element name="PaymentFault">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="errorCode" type="xsd:string" />
            <xsd:element name="errorMessage" type="xsd:string" />
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>

    </xsd:schema>
  </wsdl:types>

  <!-- 2. Рівень визначення логічних повідомлень -->
  <wsdl:message name="ProcessPaymentInputMessage">
    <wsdl:part name="parameters" element="tns:ProcessPayment" />
  </wsdl:message>

  <wsdl:message name="ProcessPaymentOutputMessage">
    <wsdl:part name="parameters" element="tns:ProcessPaymentResponse" />
  </wsdl:message>

  <wsdl:message name="PaymentFaultMessage">
    <wsdl:part name="fault" element="tns:PaymentFault" />
  </wsdl:message>

  <!-- 3. Рівень порту типів (абстрактний інтерфейс методів) -->
  <wsdl:portType name="PaymentPortType">
    <wsdl:operation name="ProcessPayment">
      <wsdl:input message="tns:ProcessPaymentInputMessage" />
      <wsdl:output message="tns:ProcessPaymentOutputMessage" />
      <wsdl:fault name="PaymentFault" message="tns:PaymentFaultMessage" />
    </wsdl:operation>
  </wsdl:portType>

  <!-- 4. Рівень прив'язування (стиль серіалізації та транспорт) -->
  <wsdl:binding name="PaymentSoapBinding" type="tns:PaymentPortType">
    <soap:binding transport="http://schemas.xmlsoap.org/soap/http" style="document" />
    <wsdl:operation name="ProcessPayment">
      <soap:operation soapAction="http://bank.example.com/payments/ProcessPayment" style="document" />
      <wsdl:input>
        <soap:body use="literal" />
      </wsdl:input>
      <wsdl:output>
        <soap:body use="literal" />
      </wsdl:output>
      <wsdl:fault name="PaymentFault">
        <soap:fault name="PaymentFault" use="literal" />
      </wsdl:fault>
    </wsdl:operation>
  </wsdl:binding>

  <!-- 5. Рівень служби (фізичні мережеві ендпоінти) -->
  <wsdl:service name="PaymentService">
    <wsdl:port name="PaymentSoapPort" binding="tns:PaymentSoapBinding">
      <soap:address location="https://api.bank.example.com/soap/v1/payments" />
    </wsdl:port>
  </wsdl:service>

</wsdl:definitions>
```

#### Примітиви обміну повідомленнями у `<portType>`

Елемент `<portType>` підтримує чотири базові взаємодії між вузлами:
1. **Request-Response:** парні теги `<wsdl:input>` та `<wsdl:output>`. Клієнт надсилає запит і блокується в очікуванні відповіді.
2. **One-Way:** лише тег `<wsdl:input>`. Клієнт надсилає повідомлення без очікування результату чи підтвердження виконання.
3. **Solicit-Response:** спочатку `<wsdl:output>`, потім `<wsdl:input>`. Сервер надсилає запит клієнту й очікує на відповідь від нього.
4. **Notification:** лише тег `<wsdl:output>`. Сервер розсилає сповіщення підписаним клієнтам без очікування на відповідь.

---

### Заголовки безпеки WS-Security (WSS)

Специфікація OASIS WS-Security надає засоби автентифікації, перевірки цілісності та шифрування окремих блоків XML-повідомлення незалежно від транспортного протоколу. Усі засоби захисту зосереджені всередині спеціалізованого блоку `<wsse:Security>` у заголовку повідомлення.

#### 1. Автентифікація через `UsernameToken` з парольним дайджестом

Щоб уникнути передачі відкритого пароля через мережу та запобігти атакам повторного відтворення (Replay Attacks), клієнт генерує унікальне випадкове число (Nonce), фіксує поточний час (Created) і обчислює криптографічний геш.

```xml
<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
               xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
               soap:mustUnderstand="1">
  <wsu:Timestamp wsu:Id="TS-1">
    <wsu:Created>2026-08-20T10:00:00Z</wsu:Created>
    <wsu:Expires>2026-08-20T10:05:00Z</wsu:Expires>
  </wsu:Timestamp>
  <wsse:UsernameToken wsu:Id="User-1">
    <wsse:Username>bank_client_prod</wsse:Username>
    <!-- Парольний дайджест замість відкритого тексту -->
    <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">
      W6kYnF7Zf5Q9pL3k8b4V1m0x2Ys=
    </wsse:Password>
    <wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">
      bXlSYW5kb21Ob25jZTEyMw==
    </wsse:Nonce>
    <wsu:Created>2026-08-20T10:00:00Z</wsu:Created>
  </wsse:UsernameToken>
</wsse:Security>
```

Формула обчислення дайджесту пароля:

```
PasswordDigest = Base64( SHA1( RawNonceBytes + UTF8(CreatedTimestamp) + UTF8(RawPassword) ) )
```

Сервер, отримавши такий токен, витягує збережений пароль користувача зі своєї захищеної бази, повторює обчислення гешу за надісланими `Nonce` і `Created` та порівнює результат. Якщо час створення перевищує допустиме вікно валідності або значення `Nonce` вже зустрічалося в журналі нещодавніх запитів, сервер відхиляє запит як спробу повторного відтворення перехопленого пакету.

#### 2. Цифровий підпис: XML-Signature (`<ds:Signature>`)

Цифровий підпис гарантує, що ані корисне навантаження в `<soap:Body>`, ані критичні поля заголовків не були підроблені чи модифіковані сторонніми посередниками під час передачі через проміжні брокери та черги.

```xml
<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
  <ds:SignedInfo>
    <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#" />
    <ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256" />
    <ds:Reference URI="#Body-Id-42">
      <ds:Transforms>
        <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#" />
      </ds:Transforms>
      <ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256" />
      <ds:DigestValue>k4mN8vX9Y...=</ds:DigestValue>
    </ds:Reference>
  </ds:SignedInfo>
  <ds:SignatureValue>
    h7K2pL0m9Q...==
  </ds:SignatureValue>
  <ds:KeyInfo>
    <wsse:SecurityTokenReference>
      <wsse:Reference URI="#X509Cert-1" ValueType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3" />
    </wsse:SecurityTokenReference>
  </ds:KeyInfo>
</ds:Signature>
```

Процес формування підпису складається з трьох послідовних кроків:
1. **Ексклюзивна канонікалізація (Exclusive XML Canonicalization, C14N):** цільовий XML-фрагмент нормалізується — видаляються незначущі пробіли, атрибути сортуються за абеткою, кодування переводиться в UTF-8, а невикористані оголошення просторів імен вилучаються. Це гарантує, що текстові зміни відступів у проміжних системах не змінять результат гешування.
2. **Обчислення контрольної суми (Digest):** над канонічним фрагментом обчислюється криптографічний геш (наприклад, SHA-256), який записується в елемент `<ds:DigestValue>`.
3. **Підписання службової структури:** блок `<ds:SignedInfo>` канонікалізується, гешується і шифрується закритим ключем відправника за алгоритмом RSA чи ECDSA, формуючи остаточний рядок `<ds:SignatureValue>`.

#### 3. Шифрування окремих елементів: XML-Encryption (`<xenc:EncryptedData>`)

Якщо повідомлення містить конфіденційні банківські реквізити чи медичні дані, клієнт може зашифрувати лише окремі дочірні теги всередині `<soap:Body>`, залишивши решту структури відкритою для аналізу маршрутизаторами.

```xml
<xenc:EncryptedData xmlns:xenc="http://www.w3.org/2001/04/xmlenc#"
                   Type="http://www.w3.org/2001/04/xmlenc#Element">
  <xenc:EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#aes256-cbc" />
  <ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
    <xenc:EncryptedKey>
      <xenc:EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p" />
      <xenc:CipherData>
        <xenc:CipherValue>Y2lwaGVyX2tleV9kYXRh...==</xenc:CipherValue>
      </xenc:CipherData>
    </xenc:EncryptedKey>
  </ds:KeyInfo>
  <xenc:CipherData>
    <xenc:CipherValue>ZW5jcnlwdGVkX3BheWxvYWRfZGF0YQ...==</xenc:CipherValue>
  </xenc:CipherData>
</xenc:EncryptedData>
```

Шифрування здійснюється за гібридною схемою: корисні дані шифруються швидким симетричним ключем за алгоритмом AES-256-CBC, а сам сеансовий симетричний ключ шифрується відкритим асиметричним ключем RSA кінцевого одержувача. Завдяки цьому проміжні сервери маршрутизують конверт без можливості підглянути зашифровані банківські дані.

---

### Маршрутизація адресації: специфікація WS-Addressing

Стандарт **WS-Addressing** вводить універсальний механізм адресації кінцевих точок та ідентифікації сесій передачі, який повністю абстрагує логіку програми від конкретного транспортного протоколу. Усі адресні заголовки використовують простір імен `http://www.w3.org/2005/08/addressing`.

```xml
<soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
  <wsa:To soap:mustUnderstand="1">https://api.bank.example.com/soap/v1/payments</wsa:To>
  <wsa:Action soap:mustUnderstand="1">http://bank.example.com/payments/ProcessPayment</wsa:Action>
  <wsa:MessageID>urn:uuid:550e8400-e29b-41d4-a716-446655440000</wsa:MessageID>
  <wsa:ReplyTo>
    <wsa:Address>https://client.bank.example.com/soap/v1/callbacks</wsa:Address>
    <wsa:ReferenceParameters>
      <client:SessionToken xmlns:client="http://client.example.com">SES-9941</client:SessionToken>
    </wsa:ReferenceParameters>
  </wsa:ReplyTo>
  <wsa:FaultTo>
    <wsa:Address>https://audit.bank.example.com/soap/v1/alerts</wsa:Address>
  </wsa:FaultTo>
</soap:Header>
```

Призначення ключових полів WS-Addressing:
- `<wsa:To>` — остаточна адреса кінцевого вузла обробки. Дозволяє шлюзам спрямовувати повідомлення через черги навіть тоді, коли фізична адреса HTTP-з'єднання вказує лише на проміжний проксі-сервер.
- `<wsa:Action>` — обов'язковий URI-ідентифікатор виконуваної операції. Замінює застарілий транспортний заголовок `SOAPAction`.
- `<wsa:MessageID>` — глобально унікальний ідентифікатор повідомлення (UUID), що використовується для дедуплікації запитів та побудови кореляційних ланцюжків.
- `<wsa:ReplyTo>` — адреса кінцевої точки, куди сервер повинен надіслати відповідь. Дозволяє розділяти синхронний транспорт: клієнт надсилає запит через HTTP, закриває з'єднання, а сервер відправляє результат на зворотний ендпоінт клієнта окремим з'єднанням.
- `<wsa:FaultTo>` — окрема адреса для надсилання звітів про аварійні збої (Fault), що дозволяє спрямовувати помилки до спеціалізованих сервісів моніторингу та безпеки.

---

### Надійна доставка: специфікація WS-ReliableMessaging (WS-RM)

Протокол **WS-ReliableMessaging** забезпечує гарантовану доставку повідомлень між відправником і одержувачем через ненадійні мережеві з'єднання з підтримкою контролю послідовності (`InOrder`) та усунення дублікатів (`ExactlyOnce`).

Процес обміну повідомленнями будується навколо концепції послідовності (Sequence):
1. **Створення послідовності:** клієнт надсилає повідомлення `<wsrm:CreateSequence>` і отримує від сервера унікальний `Identifier` послідовності.
2. **Нумерація повідомлень:** кожне наступне бізнес-повідомлення несе заголовок із номером у черзі:
   ```xml
   <wsrm:Sequence xmlns:wsrm="http://docs.oasis-open.org/ws-rx/wsrm/200702">
     <wsrm:Identifier>urn:uuid:seq-9941-abcd</wsrm:Identifier>
     <wsrm:MessageNumber>1</wsrm:MessageNumber>
   </wsrm:Sequence>
   ```
3. **Підтвердження доставки:** сервер періодично або за запитом повертає блок підтвердження діапазонів отриманих номерів:
   ```xml
   <wsrm:SequenceAcknowledgement xmlns:wsrm="http://docs.oasis-open.org/ws-rx/wsrm/200702">
     <wsrm:Identifier>urn:uuid:seq-9941-abcd</wsrm:Identifier>
     <wsrm:AcknowledgementRange Lower="1" Upper="5" />
   </wsrm:SequenceAcknowledgement>
   ```
4. **Закриття послідовності:** після передачі останнього повідомлення відправник надсилає `<wsrm:TerminateSequence>`.

---

### Розподілені транзакції: WS-AtomicTransaction та WS-Coordination

Для проведення узгоджених змін у декількох гетерогенних базах даних за протоколом двофазної фіксації (Two-Phase Commit, 2PC) застосовується стандарт **WS-AtomicTransaction**.

Координатор розподіленої транзакції створює контекст координації, який передається в заголовку кожного SOAP-запиту:

```xml
<wscoor:CoordinationContext xmlns:wscoor="http://docs.oasis-open.org/ws-tx/wscoor/2006/06">
  <wscoor:CoordinationType>http://docs.oasis-open.org/ws-tx/wsat/2006/06</wscoor:CoordinationType>
  <wscoor:Identifier>urn:uuid:tx-global-7744</wscoor:Identifier>
  <wscoor:RegistrationService>
    <wsa:Address>https://coordinator.bank.example.com/RegistrationService</wsa:Address>
  </wscoor:RegistrationService>
</wscoor:CoordinationContext>
```

Протокол виконання 2PC:
- **Фаза 1 (Prepare):** координатор надсилає кожному сервісу команду `<wsat:Prepare>`. Кожен сервіс блокує локальні ресурси в базі даних і відповідає `<wsat:Prepared>` (готовий до фіксації) або `<wsat:Aborted>` (помилка).
- **Фаза 2 (Commit / Rollback):** якщо всі учасники відповіли `Prepared`, координатор розсилає команду `<wsat:Commit>`. Якщо хоча б один вузол повідомив про збій, усім учасникам надсилається команда `<wsat:Rollback>`, що гарантує абсолютну атомарність змін.

---

### Декларація політик: стандарт WS-Policy

Стандарт **WS-Policy** надає гнучкий фреймворк для опису вимог і можливостей сервісу (автентифікація, шифрування, надійна доставка) безпосередньо всередині WSDL. Замість написання інструкцій у текстових регламентах сервер публікує машиночитні правила через елемент `<wsp:Policy>`.

```xml
<wsp:Policy wsu:Id="PaymentSecurityPolicy"
            xmlns:wsp="http://schemas.xmlsoap.org/ws/2004/09/policy"
            xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
            xmlns:sp="http://docs.oasis-open.org/ws-sx/ws-securitypolicy/200702">
  <sp:AsymmetricBinding>
    <wsp:Policy>
      <sp:InitiatorToken>
        <wsp:Policy>
          <sp:X509Token sp:IncludeToken="http://docs.oasis-open.org/ws-sx/ws-securitypolicy/200702/IncludeToken/AlwaysToRecipient" />
        </wsp:Policy>
      </sp:InitiatorToken>
      <sp:AlgorithmSuite>
        <wsp:Policy>
          <sp:Basic256 />
        </wsp:Policy>
      </sp:AlgorithmSuite>
    </wsp:Policy>
  </sp:AsymmetricBinding>
  <sp:SignedParts>
    <sp:Body />
    <sp:Header Name="To" Namespace="http://www.w3.org/2005/08/addressing" />
  </sp:SignedParts>
</wsp:Policy>
```

Клієнтський генератор коду інтерпретує твердження політики (Policy Assertions) і автоматично налаштовує криптографічний конвеєр стаба відповідно до вимог сервера.

---

### Специфікація двійкової оптимізації: MTOM та XOP

При передачі великих файлів за протоколом MTOM MIME-заголовок HTTP-пакета набуває складної структури:

```http
POST /soap/v1/documents HTTP/1.1
Host: api.bank.example.com
Content-Type: multipart/related; type="application/xop+xml";
              start="<root_envelope@bank.example.com>";
              start-info="text/xml";
              boundary="MIME_boundary_9941"

--MIME_boundary_9941
Content-Type: application/xop+xml; charset=utf-8; type="text/xml"
Content-Transfer-Encoding: binary
Content-ID: <root_envelope@bank.example.com>

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:xop="http://www.w3.org/2004/08/xop/include">
  <soap:Body>
    <m:UploadReport xmlns:m="http://bank.example.com/docs">
      <m:reportName>QuarterlyAudit.pdf</m:reportName>
      <m:fileContent>
        <xop:Include href="cid:binary_report_part_2@bank.example.com" />
      </m:fileContent>
    </m:UploadReport>
  </soap:Body>
</soap:Envelope>

--MIME_boundary_9941
Content-Type: application/pdf
Content-Transfer-Encoding: binary
Content-ID: <binary_report_part_2@bank.example.com>

%PDF-1.7 ... [чисті двійкові байти файлу без перекодування у Base64] ...
--MIME_boundary_9941--
```

Диспетчер вебсервісу вичитує корисне навантаження безпосередньо з двійкового MIME-потоку, повністю виключаючи 33-відсоткове роздуття обсягу даних та економлячи час процесора на розбирання Base64-рядків.
