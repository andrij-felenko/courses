# ⚙️ Реалізація клієнта PEP 503 та верифікація SHA-256 хешів

Створення власного легкового клієнта для взаємодії з репозиторіями пакунків Python (Simple Repository API) є типовою інженерною задачею при розробці системних агентів автономного оновлення, безпекових аудиторів ланцюга постачання, інсталяторів для вбудованих Linux-систем (Embedded IoT) та утиліт валідації двійкових артефактів. Повноцінний менеджер `pip` має значний розмір і складну кодову базу; у багатьох прикладних сценаріях потрібен компактний, детермінований і безпечний модуль, здатний завантажити конкретне колесо `.whl` та математично довести його автентичність.

У цьому практичному проекті розглядається повна реалізація клієнта: від нормалізації імені проекту за стандартом PEP 503 та парсингу розмітки репозиторію до потокового обчислення криптографічного дайджесту SHA-256 і перевірки цілісності файлу.

---

## 1. Архітектура та послідовність етапів клієнта

Клієнт організовує обробку запиту у вигляді послідовного конвеєра, де кожен крок ізольовано від побічних ефектів і захищено від помилок введення-виведення:

```
[Вхід: назва проекту "Flask-OAuth2.0", індекс "https://pypi.org/simple/"]
                              │
                              ▼
1. Нормалізація імені за PEP 503:
   re.sub("[-_.]+", "-", name).lower() -> "flask-oauth2-0"
                              │
                              ▼
2. Мережевий запит: HTTP GET /simple/flask-oauth2-0/
   ├── Отримання тіла відповіді (HTML або JSON)
   └── Обробка кодів повернення (200 OK / 404 Not Found)
                              │
                              ▼
3. Парсинг та екстракція цільового посилання:
   ├── Пошук вузлів <a href="url#sha256=expected_hash">filename</a>
   ├── Оцінка сумісності тегів версій та платформи
   └── Виділення очікуваного дайджесту з URL-фрагмента
                              │
                              ▼
4. Потокове завантаження файлу (Streaming I/O):
   ├── Виділення фіксованого буфера розміром 64 КБ (65536 байтів)
   ├── Потоковий запис блоків у тимчасовий файл на диску
   └── Одночасне оновлення криптографічного контексту SHA256_Update()
                              │
                              ▼
5. Фіналізація та верифікація цілісності:
   ├── SHA256_Final() -> обчислення результуючого дайджесту
   ├── Порівняння: computed_digest == expected_digest
   ├── [Збіг] -> Атомарне перейменування тимчасового файлу в цільовий .whl
   └── [Збій] -> Негайне видалення тимчасового файлу, викидання винятку
```

### Потокова обробка та керування пам'яттю

Головною інженерною вимогою до клієнта є стабільність використання оперативної пам'яті. Сучасні пакети для машинного навчання (як-от `torch`, `scipy` чи `tensorflow`) постачаються у вигляді бінарних коліс розміром від 100 МБ до кількох гігабайтів. Якщо клієнт намагається завантажити весь вміст у монолітний буфер пам'яті перед обчисленням хешу, на вбудованих пристроях із лімітом пам'яті 256–512 МБ операційна система негайно знищує процес сигналом `SIGKILL` (Out-of-Memory Killer).

Щоб уникнути цього, клієнт реалізує потокове конвеєрне зчитування (Streaming Chunked I/O). Фіксований буфер розміром 64 КБ (65536 байтів) вирівняний за розміром сторінки пам'яті віртуальної пам'яті та типовим розміром вікна TCP-сокета. Кожна порція байтів, що надходить із мережевого сокета, негайно спрямовується за двома незалежними адресами:
1. Записується у файловий дескриптор відкритого тимчасового файлу на диску за допомогою системного виклику `write` або методу `file.write()`.
2. Передається криптографічному рушію через функцію оновлення проміжного стану `SHA256_Update()`.

Завдяки цьому підходу накладні витрати пам'яті процесу залишаються суворо обмеженими константою в кілька десятків кілобайтів незалежно від того, чи завантажується невеликий скрипт розміром 5 КБ, чи масивне бінарне колесо розміром 2 ГБ.

---

## 2. Реалізація клієнта мовами Python, C та C++

:::tabs
```python
import hashlib
import html.parser
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import List, Optional, Tuple


def normalize_package_name(name: str) -> str:
    """Приведення імені проекту до канонічного вигляду за PEP 503."""
    return re.sub(r"[-_.]+", "-", name).lower()


class SimpleIndexParser(html.parser.HTMLParser):
    """Парсер HTML-сторінки репозиторію PEP 503 на базі скінченного автомата."""

    def __init__(self):
        super().__init__()
        self.links: List[Tuple[str, str, Optional[str]]] = []
        self._current_href: Optional[str] = None
        self._current_text: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        if tag == "a":
            attrs_dict = dict(attrs)
            self._current_href = attrs_dict.get("href")
            self._current_text = []

    def handle_data(self, data: str):
        if self._current_href is not None:
            self._current_text.append(data)

    def handle_endtag(self, tag: str):
        if tag == "a" and self._current_href is not None:
            filename = "".join(self._current_text).strip()
            url_parts = urllib.parse.urldefrag(self._current_href)
            base_url = url_parts.url
            expected_hash = None
            if url_parts.fragment.startswith("sha256="):
                expected_hash = url_parts.fragment[len("sha256="):]
            self.links.append((filename, base_url, expected_hash))
            self._current_href = None
            self._current_text = []


def fetch_and_verify_package(
    index_url: str,
    package_name: str,
    target_filename: str,
    output_path: str
) -> bool:
    """Завантаження та потокова перевірка хешу пакета з захистом від OOM."""
    norm_name = normalize_package_name(package_name)
    project_url = f"{index_url.rstrip('/')}/{norm_name}/"

    req = urllib.request.Request(
        project_url,
        headers={"User-Agent": "MinimalPipClient/1.0", "Accept": "text/html"}
    )

    with urllib.request.urlopen(req) as resp:
        html_content = resp.read().decode("utf-8")

    parser = SimpleIndexParser()
    parser.feed(html_content)

    matched = [
        (url, h) for fn, url, h in parser.links if fn == target_filename
    ]
    if not matched:
        raise FileNotFoundError(f"Файл {target_filename} не знайдено в індексі {project_url}")

    rel_url, expected_sha256 = matched[0]
    download_url = urllib.parse.urljoin(project_url, rel_url)

    # Потокове завантаження блоками по 64 КБ
    hasher = hashlib.sha256()
    with urllib.request.urlopen(download_url) as resp, open(output_path, "wb") as out_file:
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
            out_file.write(chunk)

    computed_sha256 = hasher.hexdigest()
    if expected_sha256 and computed_sha256.lower() != expected_sha256.lower():
        raise ValueError(
            f"Помилка хешу! Очікувано: {expected_sha256}, отримано: {computed_sha256}"
        )

    return True
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <openssl/sha.h>

#define CHUNK_SIZE 65536

typedef struct {
    char filename[256];
    char url[512];
    char expected_sha256[65];
} PackageRelease;

/* Нормалізація імені проекту згідно з PEP 503 (чистий C99) */
void normalize_package_name(const char* input, char* output, size_t out_len) {
    size_t in_len = strlen(input);
    size_t j = 0;
    int last_was_dash = 0;

    for (size_t i = 0; i < in_len && j + 1 < out_len; ++i) {
        char c = input[i];
        if (c == '-' || c == '_' || c == '.') {
            if (!last_was_dash && j > 0) {
                output[j++] = '-';
                last_was_dash = 1;
            }
        } else {
            output[j++] = (char)tolower((unsigned char)c);
            last_was_dash = 0;
        }
    }
    if (j > 0 && output[j - 1] == '-') {
        j--;
    }
    output[j] = '\0';
}

/* Потокове обчислення SHA-256 контрольної суми відкритого двійкового файлу */
int verify_file_sha256(FILE* file, const char* expected_hex) {
    SHA256_CTX ctx;
    SHA256_Init(&ctx);

    unsigned char buffer[CHUNK_SIZE];
    size_t bytes_read;

    fseek(file, 0, SEEK_SET);
    while ((bytes_read = fread(buffer, 1, sizeof(buffer), file)) > 0) {
        SHA256_Update(&ctx, buffer, bytes_read);
    }

    unsigned char digest[SHA256_DIGEST_LENGTH];
    SHA256_Final(digest, &ctx);

    char computed_hex[SHA256_DIGEST_LENGTH * 2 + 1];
    for (int i = 0; i < SHA256_DIGEST_LENGTH; ++i) {
        sprintf(computed_hex + (i * 2), "%02x", digest[i]);
    }
    computed_hex[64] = '\0';

    return (strcmp(computed_hex, expected_hex) == 0);
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <array>
#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <openssl/sha.h>

namespace pip_client {

// Нормалізація імені проекту за стандартом PEP 503 з нульовим виділенням динамічної пам'яті
std::string normalize_project_name(std::string_view name) {
    std::string result;
    result.reserve(name.size());
    bool last_was_dash = false;

    for (char ch : name) {
        if (ch == '-' || ch == '_' || ch == '.') {
            if (!last_was_dash && !result.empty()) {
                result.push_back('-');
                last_was_dash = true;
            }
        } else {
            result.push_back(static_cast<char>(std::tolower(static_cast<unsigned char>(ch))));
            last_was_dash = false;
        }
    }
    if (!result.empty() && result.back() == '-') {
        result.pop_back();
    }
    return result;
}

// RAII-обгортка над криптографічним контекстом OpenSSL SHA256
class Sha256StreamVerifier {
public:
    Sha256StreamVerifier() {
        SHA256_Init(&ctx_);
    }

    void update(const char* data, std::size_t length) {
        SHA256_Update(&ctx_, data, length);
    }

    std::string finalize() {
        std::array<unsigned char, SHA256_DIGEST_LENGTH> digest{};
        SHA256_Final(digest.data(), &ctx_);

        std::ostringstream oss;
        for (unsigned char byte : digest) {
            oss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
        }
        return oss.str();
    }

private:
    SHA256_CTX ctx_;
};

// Потокова перевірка цілісності вхідного бінарного потоку std::istream
bool verify_stream_integrity(std::istream& stream, std::string_view expected_sha256) {
    Sha256StreamVerifier verifier;
    std::vector<char> buffer(65536);

    while (stream.read(buffer.data(), static_cast<std::streamsize>(buffer.size())) || stream.gcount() > 0) {
        verifier.update(buffer.data(), static_cast<std::size_t>(stream.gcount()));
    }

    std::string computed = verifier.finalize();
    return (computed == expected_sha256);
}

} // namespace pip_client
```
:::

---

## 3. Детальний аналіз реалізації та інженерні тонкощі

Розглянуті реалізації трьома мовами програмування ілюструють фундаментальні відмінності в роботі з ресурсами операційної системи та структурами даних:

### Python: скінченний автомат розмітки та високорівневі сокети

У Python-реалізації парсер HTML побудовано на основі стандартного класу `html.parser.HTMLParser`. На відміну від сторонніх важких бібліотек (як-от `BeautifulSoup` чи `lxml`), стандартний парсер не створює в пам'яті повне дерево об'єктів документа (DOM), а працює як потоковий подієвий автомат:
- При вході у тег `<a>` метод `handle_starttag` захоплює атрибут `href`.
- Метод `handle_data` накопичує символи назви файлу.
- Метод `handle_endtag` спрацьовує при закритті тегу `</a>`, миттєво викликаючи функцію `urllib.parse.urldefrag` для відокремлення URL від фрагмента `#sha256=...`.

Така архітектура дозволяє обробляти HTML-сторінки проектів із тисячами випущених релізів за лічені мілісекунди без створення навантаження на інтерпретатор.

### C: низькорівнева робота з буферами та криптоконтекстом

Мова C демонструє безпосередній контакт із системними структурами бібліотеки OpenSSL (`libcrypto`):
1. Структура `SHA256_CTX` містить проміжний стан криптографічного гешування: лічильник оброблених бітів, залишок неповного 64-байтового блоку та вісім 32-бітних слів внутрішнього стану алгоритму (State Words `A..H`).
2. Функція `SHA256_Init()` ініціалізує контекст магічними константами (перші 32 дробові біти квадратних коренів перших восьми простих чисел).
3. Цикл `fread()` зчитує байти з файлового дескриптора напряму у виділений на стеку буфер `buffer[65536]`, викликаючи `SHA256_Update()`.
4. Функція `SHA256_Final()` застосовує обов'язкове доповнення (Padding) згідно зі стандартом FIPS PUB 180-4 (байт `0x80`, нульові байти та 64-бітне представлення повної довжини повідомлення) і вивантажує фінальний 32-байтовий бінарний дайджест.
5. Форматування дайджесту у 64-символьний шістнадцятковий рядок виконується через покроковий запис у масив символів без додаткових динамічних алокацій пам'яті (`malloc`).

### C++: ідіоматичний підхід RAII та безпека винятків

Реалізація мовою C++ демонструє сучасні стандарти безпеки пам'яті та керування ресурсами:
- **Інкапсуляція життєвого циклу:** Клас `Sha256StreamVerifier` автоматично ініціалізує `SHA256_CTX` у конструкторі, що гарантує відсутність неініціалізованих полів.
- **Відсутність зайвих копіювань:** Застосування типу `std::string_view` у функції нормалізації дозволяє передавати рядкові літерали та фрагменти тексту без виділення пам'яті на купі.
- **Універсальність потоків:** Функція `verify_stream_integrity` приймає узагальнене посилання на `std::istream&`. Це дозволяє використовувати одну й ту саму логіку для перевірки як файлів на диску (`std::ifstream`), так і пам'яттєвих буферів (`std::istringstream`) або мережевих сокетних потоків (`boost::asio::ip::tcp::iostream`).
- **Стійкість до збоїв:** Застосування `std::vector<char>` із фіксованим виділенням гарантує коректне звільнення буфера при виникненні будь-яких системних винятків вводу-виводу.

---

## 4. Критичні пастки та крайові випадки безпеки

1. **Атаки через стан гонитви (TOCTOU Race Condition):**
   Якщо клієнт завантажує файл безпосередньо за цільовим шляхом `/tmp/package.whl`, інший невідомий локальний процес може замінити файл на шкідливий у проміжку часу між моментом завершення перевірки хешу та моментом відкриття файлу для розпакування (Time-of-Check to Time-of-Use). Безпечний патерн полягає у відкритті тимчасового файлу з ексклюзивними правами доступу (`0600`), валідації дайджесту відкритого дескриптора файлу через системні виклики `fstat` / `fseek` і виконанні атомарного розпакування.
2. **Невідповідність кодувань і спеціальних символів:**
   Деякі назви проектів містять символи за межами ASCII або небезпечні комбінації шляхів на кшталт `../../malicious`. Перед виконанням мережевого запиту клієнт зобов'язаний суворо перевіряти нормалізоване ім'я за регулярним виразом `^[a-z0-9]+(-[a-z0-9]+)*$`. Будь-які невідповідні символи повинні негайно відхилятися.
3. **Хеш-колізії та застарілі алгоритми:**
   Ранні специфікації підтримували алгоритм MD5 (`#md5=...`). Наразі MD5 є криптографічно скомпрометованим: генерація колізій займає лічені секунди на споживчому процесорі. Сучасні клієнти зобов'язані відхиляти індекси, які надають лише MD5-хеші, вимагаючи щонайменше SHA-256 або BLAKE2b.
