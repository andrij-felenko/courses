# ⚙️ Програмне керування правилами брандмауера через libnftables

Практичний приклад створення та завантаження правил брандмауера nftables через бібліотечний інтерфейс `libnftables` демонструє програмну взаємодію простору користувача з підсистемою Netfilter. Код формує конфігурацію правиласету у форматі JSON або мові `nft`, завантажує її в ядро атомарною транзакцією та перевіряє отримані вердикти обробки.

У багатьох високопродуктивних мережевих інфраструктурах — від контейнерних оркестраторів Kubernetes (через CNI плагіни, такі как Calico або Cilium) до хмарних інфраструктурних балансувальників трафіку та систем захисту від DDoS-атак — виникнення чи зміна правил брандмауера відбувається динамічно під час виконання програми. Виклик зовнішньої утиліти командного рядка `nft` через `system()` або `fork()`/`execve()` створює неприпустимі накладні витрати на виділення нових процесів, створення текстових файлів та парсинг виводу. Саме для швидкої програмної взаємодії розроблено C-бібліотеку `libnftables`.

## 1. Архітектура взаємодії через libnftables

Бібліотека `libnftables` надає абстракцію контексту `struct nft_ctx`, яка обгортає низькорівневий сокет Netlink (`mnl_socket_open()`) та забезпечує транзакційну передачу команд ядру Linux.

Основні переваги використання `libnftables`:

- **Транзакційність**: кілька команд створення таблиць, ланцюжків, наборів (sets) та правил передаються ядру єдиним Netlink-повідомленням (batch). Якщо хоча б одна команда містить помилку або посилається на неіснуючий інтерфейс, ядро скасовує виконання всього пакета (atomic rollback).
- **Перехоплення виводу у пам'ять**: за допомогою функції `nft_ctx_buffer_output()` стандартний вивід правилсету або повідомлень про помилки спрямовується у внутрішній текстовий буфер у пам'яті програми, що усуває необхідність створення тимчасових файлів або конвеєрів (pipes).
- **Формат JSON (JSON API)**: крім стандартної мови правил `nft`, бібліотека підтримує передачу об'єктів у структурованому форматі JSON, що спрощує генерацію конфігурацій з інших мов програмування.

## 2. Реалізація C та C++

У наведених нижче прикладах показано два варіанти створення правилсету:
- Версія мовою C демонструє безпосередню роботу з процедурним API `libnftables` та перевірку кодів повернення.
- Версія мовою C++ реалізує сучасний об'єктно-орієнтований wrapper із використанням RAII-компонента `std::unique_ptr` із власним деструктором, монодичної обробки помилок `std::expected` (C++23) та безпечної роботи з рядковими представленнями без використання C-рядків із плаваючою довжиною.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <nftables/libnftables.h>

int main(void) {
    struct nft_ctx *ctx = nft_ctx_new(NFT_CTX_DEFAULT);
    if (!ctx) {
        fprintf(stderr, "Помилка: не вдалося створити контекст nftables\n");
        return EXIT_FAILURE;
    }

    /* Увімкнення перехоплення стандартного виводу у буфер */
    nft_ctx_buffer_output(ctx);

    /* Команди створення таблиці, ланцюжка та базових правил */
    const char *commands =
        "flush ruleset\n"
        "add table inet filter_demo\n"
        "add chain inet filter_demo input_demo { type filter hook input priority 0; policy drop; }\n"
        "add rule inet filter_demo input_demo ct state invalid drop\n"
        "add rule inet filter_demo input_demo ct state established,related accept\n"
        "add rule inet filter_demo input_demo iifname \"lo\" accept\n"
        "add rule inet filter_demo input_demo tcp dport 22 accept\n";

    printf("=== Завантаження правил nftables ===\n");
    int ret = nft_run_cmd_from_buffer(ctx, commands);
    if (ret != 0) {
        fprintf(stderr, "Помилка застосування правил nftables (код %d)\n", ret);
        nft_ctx_free(ctx);
        return EXIT_FAILURE;
    }
    printf("Правила успішно застосовано.\n\n");

    /* Запит виводу поточного правилсету у текстовому вигляді */
    const char *list_cmd = "list ruleset\n";
    ret = nft_run_cmd_from_buffer(ctx, list_cmd);
    if (ret == 0) {
        const char *output = nft_ctx_get_output_buffer(ctx);
        if (output) {
            printf("=== Поточний Ruleset ядра ===\n%s", output);
        }
    } else {
        fprintf(stderr, "Помилка читання ruleset\n");
    }

    nft_ctx_free(ctx);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <expected>
#include <nftables/libnftables.h>

namespace netfilter {

// Кастомний делетор RAII для безпечного управління контекстом nft_ctx
struct NftCtxDeleter {
    void operator()(struct nft_ctx* ctx) const noexcept {
        if (ctx) {
            nft_ctx_free(ctx);
        }
    }
};

using NftContextPtr = std::unique_ptr<struct nft_ctx, NftCtxDeleter>;

class NftablesManager {
public:
    static std::expected<NftablesManager, std::string> create() {
        struct nft_ctx* raw_ctx = nft_ctx_new(NFT_CTX_DEFAULT);
        if (!raw_ctx) {
            return std::unexpected("Не вдалося створити контекст libnftables");
        }
        
        NftablesManager manager(NftContextPtr(raw_ctx));
        nft_ctx_buffer_output(manager.ctx_.get());
        return manager;
    }

    std::expected<void, std::string> execute(std::string_view commands) {
        // nft_run_cmd_from_buffer очікує null-terminated string
        std::string cmd_str(commands);
        int rc = nft_run_cmd_from_buffer(ctx_.get(), cmd_str.c_str());
        if (rc != 0) {
            return std::unexpected("Помилка виконання команди nftables, код: " + std::to_string(rc));
        }
        return {};
    }

    [[nodiscard]] std::string get_output_buffer() const {
        const char* buf = nft_ctx_get_output_buffer(ctx_.get());
        return buf ? std::string(buf) : std::string();
    }

private:
    explicit NftablesManager(NftContextPtr ctx) : ctx_(std::move(ctx)) {}
    NftContextPtr ctx_;
};

} // namespace netfilter

int main() {
    auto manager_res = netfilter::NftablesManager::create();
    if (!manager_res) {
        std::cerr << "Помилка ініціалізації: " << manager_res.error() << '\n';
        return EXIT_FAILURE;
    }

    auto& manager = manager_res.value();

    constexpr std::string_view rules =
        "flush ruleset\n"
        "add table inet filter_cpp_demo\n"
        "add chain inet filter_cpp_demo input_cpp { type filter hook input priority 0; policy drop; }\n"
        "add rule inet filter_cpp_demo input_cpp ct state invalid drop\n"
        "add rule inet filter_cpp_demo input_cpp ct state established,related accept\n"
        "add rule inet filter_cpp_demo input_cpp iifname \"lo\" accept\n"
        "add rule inet filter_cpp_demo input_cpp tcp dport { 80, 443 } accept\n";

    std::cout << "=== Застосування правил через C++ RAII wrapper ===\n";
    if (auto res = manager.execute(rules); !res) {
        std::cerr << "Не вдалося завантажити правила: " << res.error() << '\n';
        return EXIT_FAILURE;
    }
    std::cout << "Правила успішно завантажено в ядро.\n\n";

    if (auto res = manager.execute("list ruleset\n"); res) {
        std::cout << "=== Поточний Ruleset (C++) ===\n" << manager.get_output_buffer();
    }

    return EXIT_SUCCESS;
}
```
:::

## 3. Детальний аналіз реалізації

### Логіка виконання C-версії

1. `nft_ctx_new(NFT_CTX_DEFAULT)`: створює новий об'єкт контексту `struct nft_ctx`, виділяє ресурси під внутрішні буфери та ініціалізує структура сокета Netlink (`AF_NETLINK`).
2. `nft_ctx_buffer_output(ctx)`: переключає режим виводу. За замовчуванням `libnftables` друкує результати у `stdout` та `stderr`. Після виклику цієї функції весь текстовий вивід накопичується у внутрішньому буфері, доступному через `nft_ctx_get_output_buffer()`.
3. `nft_run_cmd_from_buffer(ctx, commands)`: парсить переданий рядок команд, перетворює його у двійкові інструкції Netlink (`Netlink Messages`) та надсилає їх у ядро підсистемі `nf_tables`.
4. Повернення коду `0`: свідчить про те, що ядро атомарно застосувало всі правила. Якщо повертається від'ємне значення або код помилки, правила не застосовуються (транзакція скасовується).

### Особливості C++ реалізації

C++ версія усуває ключові ризики процедурного API:
- **Автоматичне керування пам'яттю (RAII)**: структура `NftCtxDeleter` гарантує, що виклик `nft_ctx_free(ctx)` буде виконано автоматично при виході об'єкта `NftablesManager` з області видимості, навіть у випадку виникнення винятків.
- **Типобезпечна обробка помилок**: замість повернення числових кодів помилок `-1` або `NULL` виклики повертають об'єкт `std::expected<T, std::string>`. Це примушує розробника явно перевірити успішність виконання перед зверненням до результату.
- **Безпечна робота з рядками**: використання `std::string_view` дозволяє передавати константні рядки правил без зайвого копіювання пам'яті.

## 4. Використання структурованого JSON API

Окрім текстової мови `nft`, утиліта `libnftables` дозволяє формувати команди через формат JSON. Для використання JSON необхідно увімкнути відповідний прапорець контексту за допомогою `nft_ctx_output_set_flags(ctx, NFT_CTX_OUTPUT_JSON)`.

Структура JSON-документа складається з кореневого об'єкта `nftables`, який містить масив дій:

```json
{
  "nftables": [
    {
      "add": {
        "table": {
          "family": "inet",
          "name": "filter_json"
        }
      }
    },
    {
      "add": {
        "chain": {
          "family": "inet",
          "table": "filter_json",
          "name": "input_json",
          "type": "filter",
          "hook": "input",
          "prio": 0,
          "policy": "drop"
        }
      }
    },
    {
      "add": {
        "rule": {
          "family": "inet",
          "table": "filter_json",
          "chain": "input_json",
          "expr": [
            {
              "match": {
                "op": "==",
                "left": { "payload": { "protocol": "tcp", "field": "dport" } },
                "right": 80
              }
            },
            {
              "accept": null
            }
          ]
        }
      }
    }
  ]
}
```

Використання JSON дозволяє уникнути помилок парсингу рядків при динамічному формуванні складних правил із багатьма змінними адресами й портами.

## 5. Динамічне керування мережевими наборами (Sets) у libnftables

Однією з найпотужніших можливостей `libnftables` є створення та динамічна модифікація **наборів (Sets)**. Набори дозволяють додавати або видаляти IP-адреси та порти на льоту без перебудови правил брандмауера.

Приклад команди створення правила з динамічним набором IP-адрес:

```text
add table inet filter_demo
add set inet filter_demo blackhole { type ipv4_addr; flags timeout; }
add chain inet filter_demo input_demo { type filter hook input priority 0; policy accept; }
add rule inet filter_demo input_demo ip saddr @blackhole drop
```

Для додавання блокованої адреси `192.168.1.100` з таймаутом блокування 10 хвилин (600 секунд) через `libnftables` передається команда:

```text
add element inet filter_demo blackhole { 192.168.1.100 timeout 600s }
```

Ця операція виконується за один крок і додає елемент у хеш-таблицю ядра `nft_set_rhash` зі складністю `O(1)`.

## 6. Компіляція, привілеї та крайові випадки

Для успішної збірки програми в системі має бути встановлена бібліотека `libnftables-dev` (Debian/Ubuntu) або `libnftables-devel` (RedHat/Fedora).

### Команди компіляції:

```bash
# Збірка C-версії
gcc -O2 -Wall main.c -lnftables -o nft_manager_c

# Збірка C++23 версії
g++ -std=c++23 -O2 -Wall main.cpp -lnftables -o nft_manager_cpp
```

### Вимоги до привілеїв виконання:

Створення сокетів Netlink підсистеми Netfilter вимагає наявності системного привілею ядра **`CAP_NET_ADMIN`**. Якщо програма запускається від імені звичайного користувача без розширених прав, виклик `nft_run_cmd_from_buffer()` поверне помилку `EPERM` (Operation not permitted).

Запуск із привілеями:

```bash
sudo ./nft_manager_c
sudo ./nft_manager_cpp
```

Або надання привілею бінарному файлу без запуску від `root`:

```bash
sudo setcap cap_net_admin=+ep ./nft_manager_cpp
./nft_manager_cpp
```

### Наслідки та крайові випадки:

1. **Переповнення Netlink-буфера (`ENOBUFS`)**: при одночасному вичитуванні великого правилсету (десятки тисяч правил) буфер сокета Netlink може переповнитися. У такому разі необхідно збільшити розмір буфера через `sysctl net.core.rmem_max`.
2. **Конфлікти паралельних транзакцій**: якщо два сервіси одночасно намагаються модифікувати ruleset, Netfilter блокує мутекс ядра `table lock`. Друга транзакція отримає помилку `EBUSY` і має повторити спробу (retry loop).
3. **Багатопотокова робота**: об'єкт контексту `struct nft_ctx` **не є потокобезпечним (thread-unsafe)**. Якщо кілька потоків програми повинні паралельно надсилати команди у Netfilter, кожен потік зобов'язаний створити власний окремий контекст `nft_ctx_new()`.
