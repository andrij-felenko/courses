# 📋 Анатомія SDP-дескриптора у WebRTC: Offer/Answer та атрибути сесії

Протокол опису сесій SDP (Session Description Protocol, RFC 4566 та RFC 8866) є декларативною мовою узгодження параметрів мультимедійного зв'язку у WebRTC. На відміну від класичної IP-телефонії SIP, де SDP використовувався для статичного опису портів RTP, у WebRTC протокол SDP зазнав глибокої модифікації: через механізм Offer/Answer (RFC 3264) та розширення Unified Plan (RFC 8829) він описує криптографічні відбитки сертифікатів DTLS, реквізити зв'язності ICE, мультиплексування потоків BUNDLE, формати кодеків та специфікації зворотного зв'язку керування заторами.

SDP-документ являє собою послідовність текстових рядків формату `<тип>=<значення>`, розділених символами повернення каретки та переведення рядка `\r\n` (CRLF). Пробіли довкола знака рівності суворо заборонені стандартом. Документ складається з двох основних частин: загальної **секції сесії** (Session-Level) та однієї чи кількох **секцій медіа** (Media-Level).

## Загальна структура та поля рівня сесії

Секція сесії починається з першого рядка документа і діє для всіх медіапотоків, якщо вони не перевизначають відповідні параметри всередині власної секції.

| Поле | Назва поля | Синтаксис стандарту | Опис та роль у WebRTC |
| :--- | :--- | :--- | :--- |
| `v=` | Protocol Version | `v=0` | Версія протоколу SDP. Завжди дорівнює `0`. |
| `o=` | Originator / Owner | `o=<user> <sess-id> <sess-ver> <nettype> <addrtype> <addr>` | Ідентифікатор джерела сесії. Містить унікальний `sess-id` та монотонно зростаючий лічильник версій `sess-ver`. |
| `s=` | Session Name | `s=-` | Назва сесії. У WebRTC не несе смислового навантаження і стандартно позначається дефісом `-`. |
| `t=` | Time Active | `t=0 0` | Час початку та завершення сесії NTP. Для необмежених за часом сесій WebRTC завжди встановлюється `0 0`. |
| `a=` | Session Attribute | `a=<атрибут>[:<значення>]` | Глобальні атрибути групування, можливостей ICE та семантики медіапотоків. |

Рядок `o=` (Origin) генерується ядром WebRTC автоматично. Наприклад:
```text
o=- 4829104829104829 2 IN IP4 127.0.0.1
```
Якщо клієнт оновлює сесію (наприклад, додає новий відеотрек або змінює бітрейт), значення `sess-ver` збільшується на одиницю (у прикладі — `2`). Це дозволяє віддаленому вузлу визначити, чи надійшов новий опис, чи повторний пакет.

### Атрибути групування BUNDLE

Критично важливим глобальним атрибутом у WebRTC є групування портів за специфікацією RFC 8843 (BUNDLE):

```text
a=group:BUNDLE 0 1 2
```

Без механізму BUNDLE кожен медіапотік (аудіотрек, відеотрек, DataChannel) вимагав би виділення окремої пари UDP-портів для RTP та RTCP, окремого проходження процедури ICE та окремого рукостискання DTLS. Атрибут `a=group:BUNDLE` повідомляє рушію, що медіасекції з ідентифікаторами `mid` `0`, `1` та `2` будуть передаватися через **єдиний спільний сокет UDP**. Це зменшує час встановлення зв'язку, економить сокетні дескриптори операційної системи та спрощує проходження трансляторів NAT.

Інший глобальний атрибут визначає семантику медіапотоків W3C MediaStream:
```text
a=msid-semantic: WMS *
```
Значення `WMS` (WebRTC Media Stream) вказує на підтримку зв'язування треків у логічні потоки, а зірочка `*` означає готовність приймати будь-які ідентифікатори потоків.

## Опис медіасекцій: синтаксис рядка `m=`

Кожна секція медіа починається з рядка `m=` (Media Description), який визначає тип медіа, порт, транспортний профіль та список числових кодів корисного вантажу (Payload Types):

```text
m=<media> <port> <proto> <fmt> [<fmt> ...]
```

### 1. Медіасекція аудіо
```text
m=audio 9 UDP/TLS/RTP/SAVPF 111 103 104 9 0 8 106 105 13 110 112 113 126
```
- `media`: `audio`.
- `port`: `9`. У WebRTC при використанні BUNDLE та Trickle ICE фактичний порт не визначається в рядку `m=`, тому записується фіктивне значення `9` (RFC 8843 Discard Port). Реальні порти передаються через ICE-кандидати.
- `proto`: `UDP/TLS/RTP/SAVPF` — захищений транспортний профіль RTP із шифруванням SRTP (SAVP — Secure Audio-Video Profile) та розширеним зворотним зв'язком AVPF (RFC 4585 / RFC 5124) поверх DTLS/UDP.
- `fmt`: Список динамічних та статичних номерів корисного вантажу RTP Payload Types (наприклад, `111` для Opus).

### 2. Медіасекція відео
```text
m=video 9 UDP/TLS/RTP/SAVPF 96 97 98 99 100 101 102 121 127 120 125
```
- `media`: `video`.
- `proto`: `UDP/TLS/RTP/SAVPF`.
- `fmt`: Список типів відеокодеків (H.264, VP8, VP9, AV1) та їхніх допоміжних потоків ретрансляції RTX і корекції помилок RED/ULPFEC.

### 3. Тракт довільних даних (DataChannel)
```text
m=application 9 UDP/DTLS/SCTP webrtc-datachannel
```
- `media`: `application`.
- `proto`: `UDP/DTLS/SCTP` (або `DTLS/SCTP` згідно з новішим RFC 8841).
- `fmt`: `webrtc-datachannel` — фіксований рядок, що декларує інкапсуляцію протоколу SCTP для DataChannels.

## Атрибути безпеки та транспорту

Усередині кожної медіасекції розміщуються атрибути, що задають параметри захисту каналу та узгодження ролей.

### Реквізити зв'язності ICE
```text
a=ice-ufrag:8xTk
a=ice-pwd:abc123def456ghi789jkl012
a=ice-options:trickle
```
- `a=ice-ufrag`: Ім'я користувача (User Fragment) довжиною щонайменше 4 символи, яке використовується для автентифікації пакетів STUN Binding Request під час перевірок зв'язності.
- `a=ice-pwd`: Пароль сесії ICE (щонайменше 22 символи), за допомогою якого обчислюється HMAC-підпис STUN `MESSAGE-INTEGRITY`.
- `a=ice-options:trickle`: Повідомляє про підтримку технології Trickle ICE (RFC 8838) — асинхронної передачі кандидатів без очікування завершення повного збору локальних адрес.

### Криптографічний відбиток DTLS та узгодження ролей
```text
a=fingerprint:sha-256 3B:7D:9E:0A:4F:1C:82:55:6E:9B:02:14:8A:77:33:F1:C0:D4:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22
a=setup:actpass
```
- `a=fingerprint`: Криптографічний хеш сертифіката X.509, згенерованого локальним рушієм WebRTC. Під час рукостискання DTLS віддалена сторона перевіряє, що отриманий сертифікат відповідає цьому відбитку. Це унеможливлює атаку посередника (Man-in-the-Middle), оскільки сигнальний канал вважається захищеним (наприклад, WSS/HTTPS).
- `a=setup`: Роль вузла під час встановлення сесії DTLS:
  - `actpass`: Ініціатор (Offer) готовий виступати як клієнтом (`active`), так і сервером (`passive`).
  - `active`: Вузол зобов'язується надіслати `ClientHello` DTLS (типове значення для Answer).
  - `passive`: Вузол очікує на `ClientHello` та відповідає пакетом `ServerHello`.

### Параметри порту SCTP
```text
a=sctp-port:5000
a=max-message-size:262144
```
- `a=sctp-port`: Номер порту асоціації SCTP (стандартне значення — `5000`).
- `a=max-message-size`: Максимальний розмір одного повідомлення DataChannel у байтах (у прикладі — 256 КіБ).

## Атрибути конфігурації кодеків

Для кожного коду `Payload Type`, вказаного у рядку `m=`, формуються специфічні атрибути зіставлення формату та зворотного зв'язку.

### 1. Зіставлення кодека (`a=rtpmap`)
```text
a=rtpmap:<payload-type> <кодек>/<тактова-частота>[/<канали>]
```
Приклади:
```text
a=rtpmap:111 opus/48000/2
a=rtpmap:96 H264/90000
a=rtpmap:97 rtx/90000
```
- Для аудіокодека Opus тактова частота таймстемпів RTP завжди становить `48000` Гц, кількість каналів — `2` (стерео).
- Для відеокодеків частота таймстемпів фіксована на рівні `90000` Гц (відповідає кроку таймера 90 кГц, прийнятому у транспортних потоках MPEG).
- Тип `rtx` позначає допоміжний потік ретрансляції втрачених пакетів для відповідного відеокодека.

### 2. Параметри формату кодека (`a=fmtp`)
Атрибут `a=fmtp` передає специфічні параметри ініціалізації енкодера й декодера:

```text
a=fmtp:111 minptime=10;useinbandfec=1
a=fmtp:96 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42e01f
a=fmtp:97 apt=96
```
- Для Opus:
  - `minptime=10`: Мінімальна тривалість аудіофрейму (10 мс).
  - `useinbandfec=1`: Увімкнення вбудованої корекції помилок (In-band Forward Error Correction).
- Для H.264:
  - `packetization-mode=1`: Режим пакетування Non-Interleaved (кадри NALU інкапсулюються з урахуванням агрегованих пакетів STAP-A та фрагментованих FU-A, RFC 6184).
  - `profile-level-id=42e01f`: Шістнадцятковий код профілю (перші два символи `42` — Constrained Baseline Profile, останні два `1f` — рівень Level 3.1, що дозволяє роздільну здатність 720p30).
- Для RTX:
  - `apt=96` (Associated Payload Type): Вказує, що потік ретрансляції `97` захищає основні відеопакети типу `96`.

### 3. Зворотний зв'язок керування потоком (`a=rtcp-fb`)
Атрибути `a=rtcp-fb` декларують підтримувані механізми реакції на втрати та перевантаження:

```text
a=rtcp-fb:96 nack
a=rtcp-fb:96 nack pli
a=rtcp-fb:96 ccm fir
a=rtcp-fb:96 goog-remb
a=rtcp-fb:96 transport-cc
```
- `nack`: Запит на повторну передачу конкретного втраченого RTP-пакета за номером `Sequence Number` (RFC 4585).
- `nack pli`: Індикація втрати зображення (Picture Loss Indication) — запит до кодера згенерувати повний ключовий IDR-кадр.
- `ccm fir`: Запит на оновлення внутрішньокадрового стану (Full Intra Request, RFC 5104).
- `goog-remb`: Оцінка максимального бітрейту приймачем (Receiver Estimated Maximum Bitrate).
- `transport-cc`: Підтримка сучасного зворотного зв'язку затримки на транспортному рівні (Transport-Wide Congestion Control).

### 4. Розширення заголовків RTP (`a=extmap`)
```text
a=extmap:1 urn:ietf:params:rtp-hdrext:sdes:mid
a=extmap:2 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01
a=extmap:3 urn:ietf:params:rtp-hdrext:sdes:rtp-stream-id
```
Ці атрибути призначають короткі числові ідентифікатори (ID від `1` до `14` для 1-байтового заголовка розширення RTP) стандартним URI. Наприклад, ID `2` додає до кожного вихідного RTP-пакета наскрізний 16-бітовий лічильник `Transport-Wide Sequence Number`, необхідний для роботи алгоритму TWCC.

### 5. Ідентифікація джерела медіа (`a=ssrc`)
```text
a=ssrc:314159265 cname:user@host.internal
a=ssrc:314159265 msid:audio-stream-id audio-track-id
```
- `cname` (Canonical End-Point Identifier): Канонічне ім'я джерела, яке використовується для синхронізації часу між окремими аудіо- та відеотреками (Lip Synchronization).
- `msid`: Зв'язує конкретний апаратний SSRC із програмними об'єктами `MediaStreamTrack` у JavaScript API.

### 6. Напрям передачі медіа (Directional Attributes)
Атрибути напряму визначають, чи передає вузол медіапотік, чи лише приймає його:

```text
a=sendrecv
a=sendonly
a=recvonly
a=inactive
```
- `sendrecv`: Вузол готовий як відправляти власний медіапотік, так і приймати потік від віддаленого піра (типовий стан для двостороннього відеозв'язку).
- `sendonly`: Вузол транслює медіа, але ігнорує вхідний трафік (наприклад, радіо- або телетрансляція).
- `recvonly`: Вузол лише приймає медіа і не транслює локальні камери чи мікрофони (режим пасивного глядача).
- `inactive`: Медіапотік тимчасово призупинено (режим Mute або вимкнення відеокамери). Порти лишаються відкритими, DTLS-сесія активна, але кодери зупиняють генерацію RTP-пакетів.

Під час переговорів Offer/Answer напрями дзеркально узгоджуються: якщо Offer пропонує `a=sendonly`, коректний Answer зобов'язаний відповісти `a=recvonly` (або `a=inactive`, якщо приймач не бажає отримувати даний потік).

### 7. Багатопотокове кодування (Simulcast)
Для адаптації якості відео під різні канали зв'язку у великих конференціях WebRTC підтримує технологію Simulcast (RFC 8853). Відправник генерує одночасно кілька варіантів одного відеопотоку з різною роздільною здатністю (наприклад, висока High 1080p, середня Medium 720p, низька Low 360p):

```text
a=rid:h send
a=rid:m send
a=rid:l send
a=simulcast:send h;m;l
```
- `a=rid:<id> send`: Оголошує унікальний ідентифікатор потоку (Restriction Identifier).
- `a=simulcast:send h;m;l`: Декларує одночасне надсилання трьох роздільних потоків. Медіасервер (SFU — Selective Forwarding Unit) аналізує зворотний зв'язок кожного клієнта і пересилає слабким мобільним пристроям лише потік `l`, а швидким настільним клієнтам — потік `h`.

### 8. Реєстр розширень заголовків RTP (RTP Header Extensions)
Розширення заголовків RTP (RFC 5285 / RFC 8285) дозволяють передавати метадані з кожним медіапакетом без дешифрування його корисного вантажу. У WebRTC стандартизовано наступний набір розширень:

| URI розширення | Стандарт | Призначення у WebRTC |
| :--- | :--- | :--- |
| `urn:ietf:params:rtp-hdrext:sdes:mid` | RFC 8843 | Ідентифікатор медіасекції `mid` для демультиплексування BUNDLE-потоків. |
| `urn:ietf:params:rtp-hdrext:sdes:rtp-stream-id` | RFC 8852 | Ідентифікатор треку для маршрутизації Simulcast-потоків (`rid`). |
| `http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01` | draft-holmer | 16-бітовий наскрізний послідовний номер для контуру TWCC. |
| `urn:ietf:params:rtp-hdrext:ssrc-audio-level` | RFC 6464 | Рівень гучності аудіосигналу (0–127 дБ) для індикації активного мовця без декодування звуку. |
| `urn:ietf:params:rtp-hdrext:toffset` | RFC 5450 | Зсув часу передачі (Transmission Time Offset) для точного обліку джиттера пакування. |
| `urn:3gpp:video-orientation` | 3GPP TS 26.114 | Координати орієнтації відеокамери (CVO: поворот на 0°, 90°, 180°, 270°) під час обертання смартфона. |

## Формат кандидата зв'язності (`a=candidate`)

Кандидати зв'язності описують доступні мережеві адреси для встановлення транспорту:

```text
a=candidate:<foundation> <component-id> <transport> <priority> <ip-address> <port> typ <candidate-type> [raddr <rel-addr> rport <rel-port>] [generation <gen>] [ufrag <ufrag>]
```

| Параметр | Приклад | Призначення |
| :--- | :--- | :--- |
| `foundation` | `1` | Унікальний числовий або текстовий маркер типу кандидата та базової IP-адреси. |
| `component-id` | `1` | Ідентифікатор компонента (завжди `1` для RTP/RTCP у режимі `rtcp-mux`). |
| `transport` | `udp` | Транспортний протокол (переважно `udp`, рідше `tcp`). |
| `priority` | `2122260223` | 32-бітове ціле число, що визначає черговість перевірки (обчислюється за типом адреси та метрикою інтерфейсу). |
| `ip-address` | `192.168.1.50` | IP-адреса інтерфейсу або зовнішньої точки транслятора NAT. |
| `port` | `54320` | Номер UDP-порту. |
| `typ` | `host` | Тип кандидата: `host` (локальний), `srflx` (STUN), `relay` (TURN), `prflx` (виявлений під час перевірки). |
| `raddr`, `rport` | `raddr 0.0.0.0 rport 0` | Базова адреса (Related Address), з якої було отримано рефлексивного або ретрансляційного кандидата. |

Приклади реальних кандидатів:
```text
a=candidate:4234997325 1 udp 2122260223 192.168.1.50 54320 typ host generation 0
a=candidate:1688198902 1 udp 1686052607 203.0.113.4 54320 typ srflx raddr 192.168.1.50 rport 54320 generation 0
a=candidate:3451239871 1 udp 41885695 198.51.100.1 34780 typ relay raddr 203.0.113.4 rport 54320 generation 0
```

## Повний приклад узгодження: Offer та Answer

Нижче наведено повний парний приклад SDP-дескрипторів для сесії, що містить аудіо (Opus), відео (H.264) та DataChannel у режимі Unified Plan з єдиним BUNDLE-транспортом.

### SDP Offer (Ініціатор)
```text
v=0
o=- 719284918239102 1 IN IP4 127.0.0.1
s=-
t=0 0
a=group:BUNDLE 0 1 2
a=msid-semantic: WMS *
m=audio 9 UDP/TLS/RTP/SAVPF 111 9
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:K4x9
a=ice-pwd:9xY1z8W2v7U3t6S5r4Q3p2O1n
a=ice-options:trickle
a=fingerprint:sha-256 A1:B2:C3:D4:E5:F6:07:18:29:3A:4B:5C:6D:7E:8F:90:12:34:56:78:9A:BC:DE:F0:12:34:56:78:9A:BC:DE:F0
a=setup:actpass
a=mid:0
a=rtcp-mux
a=sendrecv
a=rtpmap:111 opus/48000/2
a=fmtp:111 minptime=10;useinbandfec=1
a=rtpmap:9 G722/8000
a=ssrc:10001 cname:peerA@webrtc
m=video 9 UDP/TLS/RTP/SAVPF 96 97
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:K4x9
a=ice-pwd:9xY1z8W2v7U3t6S5r4Q3p2O1n
a=ice-options:trickle
a=fingerprint:sha-256 A1:B2:C3:D4:E5:F6:07:18:29:3A:4B:5C:6D:7E:8F:90:12:34:56:78:9A:BC:DE:F0:12:34:56:78:9A:BC:DE:F0
a=setup:actpass
a=mid:1
a=rtcp-mux
a=sendrecv
a=rtpmap:96 H264/90000
a=fmtp:96 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42e01f
a=rtpmap:97 rtx/90000
a=fmtp:97 apt=96
a=rtcp-fb:96 nack
a=rtcp-fb:96 nack pli
a=rtcp-fb:96 transport-cc
a=extmap:1 urn:ietf:params:rtp-hdrext:sdes:mid
a=extmap:2 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01
a=ssrc:20001 cname:peerA@webrtc
m=application 9 UDP/DTLS/SCTP webrtc-datachannel
c=IN IP4 0.0.0.0
a=ice-ufrag:K4x9
a=ice-pwd:9xY1z8W2v7U3t6S5r4Q3p2O1n
a=ice-options:trickle
a=fingerprint:sha-256 A1:B2:C3:D4:E5:F6:07:18:29:3A:4B:5C:6D:7E:8F:90:12:34:56:78:9A:BC:DE:F0:12:34:56:78:9A:BC:DE:F0
a=setup:actpass
a=mid:2
a=sctp-port:5000
a=max-message-size:262144
```

### SDP Answer (Відповідач)
Відповідач обирає взаємно підтримувані кодеки (наприклад, залишає лише Opus для аудіо та H.264 для відео, відкидаючи G.722), фіксує свою роль DTLS як `active` та повертає власний сертифікат і параметри ICE:

```text
v=0
o=- 839102839102941 1 IN IP4 127.0.0.1
s=-
t=0 0
a=group:BUNDLE 0 1 2
a=msid-semantic: WMS *
m=audio 9 UDP/TLS/RTP/SAVPF 111
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:R8w2
a=ice-pwd:3bZ9y8X7w6V5u4T3s2R1q0P9o
a=ice-options:trickle
a=fingerprint:sha-256 99:88:77:66:55:44:33:22:11:00:AA:BB:CC:DD:EE:FF:FE:DC:BA:98:76:54:32:10:FE:DC:BA:98:76:54:32:10
a=setup:active
a=mid:0
a=rtcp-mux
a=sendrecv
a=rtpmap:111 opus/48000/2
a=fmtp:111 minptime=10;useinbandfec=1
a=ssrc:30001 cname:peerB@webrtc
m=video 9 UDP/TLS/RTP/SAVPF 96 97
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:R8w2
a=ice-pwd:3bZ9y8X7w6V5u4T3s2R1q0P9o
a=ice-options:trickle
a=fingerprint:sha-256 99:88:77:66:55:44:33:22:11:00:AA:BB:CC:DD:EE:FF:FE:DC:BA:98:76:54:32:10:FE:DC:BA:98:76:54:32:10
a=setup:active
a=mid:1
a=rtcp-mux
a=sendrecv
a=rtpmap:96 H264/90000
a=fmtp:96 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42e01f
a=rtpmap:97 rtx/90000
a=fmtp:97 apt=96
a=rtcp-fb:96 nack
a=rtcp-fb:96 nack pli
a=rtcp-fb:96 transport-cc
a=extmap:1 urn:ietf:params:rtp-hdrext:sdes:mid
a=extmap:2 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01
a=ssrc:40001 cname:peerB@webrtc
m=application 9 UDP/DTLS/SCTP webrtc-datachannel
c=IN IP4 0.0.0.0
a=ice-ufrag:R8w2
a=ice-pwd:3bZ9y8X7w6V5u4T3s2R1q0P9o
a=ice-options:trickle
a=fingerprint:sha-256 99:88:77:66:55:44:33:22:11:00:AA:BB:CC:DD:EE:FF:FE:DC:BA:98:76:54:32:10:FE:DC:BA:98:76:54:32:10
a=setup:active
a=mid:2
a=sctp-port:5000
a=max-message-size:262144
```

### 9. Атрибути відновлення втрат (FEC та Redundancy)
Для захисту відеопотоку від пакетних втрат без очікування RTT на повторну доставку WebRTC узгоджує механізми прямої корекції помилок FEC:

```text
a=rtpmap:120 red/90000
a=rtpmap:121 ulpfec/90000
a=rtpmap:122 flexfec-03/90000
a=fmtp:122 repair-window=10000
```
- `red` (Redundant Audio/Video Data, RFC 2198): Дозволяє інкапсулювати основний пакет разом із дублікатом попереднього пакета в єдину RTP-датаграму.
- `ulpfec` (Uneven Level Protection FEC, RFC 5109): Застосовує алгоритм XOR-матриць з підвищеним захистом важливих заголовків відеокадрів.
- `flexfec-03` (Flexible FEC, RFC 8627): Сучасний алгоритм двовимірного інтерлівінгу та корекції втрат, параметр `repair-window` задає часове вікно захисту в мікросекундах (10 000 мкс = 10 мс).

### 10. Заборона SDES (RFC 4568) та обов'язковість DTLS
У ранніх системах VoIP ключі шифрування SRTP передавалися безпосередньо у відкритому тексті SDP через атрибут `a=crypto:` (SDES — Session Description Protocol Security Descriptions):

```text
a=crypto:1 AES_CM_128_HMAC_SHA1_80 inline:d0Rmdm5egNVxTELtmXVqNWGydfWtxnvTR1mA4kZu
```
У специфікаціях WebRTC використання атрибута `a=crypto:` **суворо заборонено** (RFC 8827). Якщо сигнальний сервер або проміжний проксі скомпрометовано, відкритий ключ `inline` дає зловмиснику можливість миттєво розшифрувати весь медіатрафік. WebRTC вимагає виключно `a=fingerprint:` з узгодженням ключів через криптографічний протокол DTLS безпосередньо між кінцевими вузлами.

### 11. Пріоритет пар кандидатів ICE (Candidate Pair Priority)
Коли обидва вузли обмінялися списками `a=candidate`, рушій формує матрицю пар кандидатів (локальний + віддалений) і сортує їх за формулою пріоритету (RFC 8445):

```
Pair_Priority
= 2³² · min(G, D) + 2 · max(G, D) + (G > D ? 1 : 0)
```
де `G` — числовий пріоритет кандидата керуючого вузла (Controlling Agent, зазвичай ініціатор Offer), а `D` — пріоритет кандидата підпорядкованого вузла (Controlled Agent, Answer). Така арифметика гарантує унікальний порядок перевірок для обох сторін без виникнення циклічних блокувань.

## Автомат станів сигналізації та інваріанти валідації

Процес узгодження SDP керується автоматом станів об'єкта `RTCPeerConnection` (властивість `signalingState`):

```text
[stable] ──(setLocalDescription: Offer)──> [have-local-offer]
[stable] ──(setRemoteDescription: Offer)─> [have-remote-offer]

[have-local-offer] ──(setRemoteDescription: Answer)──> [stable]
[have-remote-offer] ──(setLocalDescription: Answer)──> [stable]
```

- **Стан `stable`**: Початковий і фінальний стан, у якому сесія узгоджена і немає незавершених Offer/Answer операцій.
- **Стан `have-local-offer`**: Локальний вузол згенерував Offer і передав його сигнальному серверу, очікуючи на відповідь Answer.
- **Стан `have-remote-offer`**: Вузол отримав Offer від віддаленого піра і готує відповідний Answer.
- **Механізм `rollback`**: Якщо обидва вузли одночасно згенерували Offer (стан Glare), один із них (з нижчим пріоритетом у протоколі Perfect Negotiation) виконує відкат сесії за допомогою `setLocalDescription({type: "rollback"})`, повертаючись у стан `stable`.

### Типові помилки та антипатерни (SDP Munging)

Практика ручної текстової модифікації SDP-рядків у коді JavaScript (відома як SDP Munging) є найпоширенішим джерелом аварійних збоїв сесій:

1. **Ручна зміна бітрейту через `b=AS:`**: Застарілий спосіб обмеження швидкості кодера через вставку рядка `b=AS:1000` у SDP. У сучасному WebRTC це призводить до ігнорування або скидання параметрів контуру GCC. Замість цього слід використовувати API `RTCRtpSender.setParameters({ encodings: [{ maxBitrate: 1000000 }] })`.
2. **Зміна пріоритету кодеків перестановкою PT**: Перестановка номерів у рядку `m=video 9 ... 96 98` без синхронної зміни атрибутів `a=rtpmap` та `a=fmtp` руйнує таблицю зіставлення декодера. Сучасний спосіб — метод `RTCRtpTransceiver.setCodecPreferences()`.
3. **Порушення інваріанту BUNDLE**: Видалення медіасекції з рядка `a=group:BUNDLE` без виставлення нульового порту `m=... 0` для відкинутого треку призводить до виклику `InvalidAccessError` у браузері.
### 5. Переузгодження параметрів та перезапуск ICE (ICE Restart)
У процесі тривалого зв'язку виникають ситуації, коли клієнт перемикається з домашнього Wi-Fi на мобільну мережу LTE або додає трансляцію екрана. У таких випадках ініціюється процедура переузгодження (Renegotiation):

- **Збільшення лічильника версії `o=`**: Новий Offer надсилається з тим самим `sess-id`, але зі збільшеним `sess-ver`.
- **Перезапуск ICE (`ice-restart`)**: При зміні мережевого інтерфейсу локальні IP-адреси стають недійсними. Щоб уникнути створення нового об'єкта `RTCPeerConnection` та повного розриву медіапотоку, клієнт генерує Offer з абсолютно новими значеннями `a=ice-ufrag` та `a=ice-pwd`. Отримавши нові реквізити, віддалений вузол негайно запускає процедуру збору кандидатів і перевірки зв'язності на новому інтерфейсі, продовжуючи приймати медіа на старому каналі до моменту успішного перемикання (Make-Before-Break).
