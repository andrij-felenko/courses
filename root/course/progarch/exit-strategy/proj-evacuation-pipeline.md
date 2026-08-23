# ⚙️ Побудова портативного шару зберігання та евакуаційного пайплайну

Цей проектний практичний модуль містить повноцінну реалізацію абстрактного інтерфейсу зберігання об'єктів мовами C та C++, а також розгортання високонавантаженого пайплайну беззупиночної евакуації даних (Change Data Capture) для ізоляції доменної логіки від SDK хмарних вендорів.

Головна мета портативного дизайну — створити жорстку архітектурну межу між бізнес-правилами системи та зовнішньою інфраструктурою зберігання. Зміна хмарного провайдера (наприклад, міграція з хмарного AWS S3 / DynamoDB на локальне MinIO чи PostgreSQL) за правильно побудованого ізоляційного шару вимагає лише створення одного нового адаптера, залишаючи весь доменний код, алгоритми обробки та модульні тести повністю недоторканими.

---

## 1. Архітектурне проектування портативного адаптера сховища (Storage Adapter)

Абстракція сховища побудована за патерном «Порти й адаптери» (Hexagonal Architecture). Порт визначає суто доменний контракт взаємодії з об'єктами: збереження блоку даних за унікальним ключем, читання за ключем та видалення. Доменний шар працює виключно з вказівником або посиланням на цей контракт, не підозрюючи про мережеві протоколи (HTTP/REST, gRPC), специфічні заголовки автентифікації чи формат зберігання даних.

### Проблематика прямого виклику SDK вендора

Коли розробник викликає хмарне SDK безпосередньо в бізнес-коді, виникає серія прихованих архітектурних зв'язувань, які згодом блокують будь-яку спробу евакуації системи:

1. **Жорстка залежність від типів даних:** Хмарні SDK повертають власні специфічні типи даних (наприклад, `Aws::S3::Model::GetObjectResult` або `DynamoDB::AttributeValue`). Вони проникають у сигнатури методів доменних сервісів, унеможливлюючи тестування без складних mock-об'єктів.
2. **Управління ресурсами та винятками:** Специфічні мережеві помилки (наприклад, `AWS SQS OverLimit`, `HTTP 403 Forbidden`, `ThrottlingException`) мусять оброблятися всередині бізнес-логіки. Це призводит до розмиття відповідальності: доменний код починає вирішувати завдання ретраїв, експоненційного відступу (Exponential Backoff) та повторного підключення.
3. **Неможливість локального тестування:** Модульні тести вимагають підключення до реальної хмари або запуску важких емуляторів (наприклад, LocalStack), що уповільнює конвеєр CI/CD в десятки разів.

### Проектування C-інтерфейсу через таблицю функціональних вказівників (VTable)

У мові C відсутні класи та віртуальні функції, тому для побудови поліморфного адаптера застосовується паттерн VTable (Virtual Method Table). Створюється структура `storage_adapter_ops`, яка містить вказівники на функції запису, читання, видалення та знищення об'єкта. 

Головна структура `storage_adapter_t` тримає вказівник на цю таблицю методів та непрозорий вказівник `void *ctx`, у якому конкретний драйвер зберігає власні ресурси — дескриптори файлів, мережеві сокети або токени автентифікації. Завдяки такому підходу доменний код C маніпулює виключно вказівником на `storage_adapter_t`, виклики методів відбуваються через непрямий виклик `self->ops->write_object(...)`, а внутрішній стан драйвера залишається повністю прихованим.

### Проектування C++20-інтерфейсу на базі новітніх стандартів

У C++20 реалізація адаптера спирається на сучасні семантичні вирази мови:

- **Використання `std::string_view` та `std::span<const std::byte>`:** Уникає зайвого копіювання пам'яті під час передачі ключів та бінарних даних. Доменний шар передає зріз пам'яті без виділення динамічних буферів на купі.
- **Беземисійна обробка помилок через `std::expected`:** Замість викидання винятків або використання застарілих вихідних `out`-параметрів, кожна функція повертає об'єкт `std::expected<T, StorageError>`. Це гарантує явну перевірку результату виклику на етапі компіляції та виключає неочікувані аварійні зупинки потоку.
- **Гарантії RAII (Resource Acquisition Is Initialization):** Деструктори конкретних адаптерів гарантують автоматичне закриття файлів, скидання системних буферів та звільнення мережевих з'єднань при виході об'єкта з області видимості.

### Інтерфейс та реалізація мовами C та C++

Нижче наведено робочий код портативного адаптера сховища об'єктів. Контракт підтримки розроблено у двох варіантах: ідіоматичний C з використанням структури функціональних вказівників та ідіоматичний C++20 із застосуванням RAII, беземисійних помилок, неволодіючих зрізів пам'яті та рядкових представлень.

:::tabs
```c
/* storage_adapter.h — Портативний C-інтерфейс сховища об'єктів */
#ifndef STORAGE_ADAPTER_H
#define STORAGE_ADAPTER_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct storage_adapter storage_adapter_t;

/* Коди помилок адаптера сховища */
typedef enum {
    STORAGE_OK = 0,
    STORAGE_ERR_NOT_FOUND = -1,
    STORAGE_ERR_ACCESS_DENIED = -2,
    STORAGE_ERR_NETWORK = -3,
    STORAGE_ERR_IO = -4,
    STORAGE_ERR_INVALID_PARAM = -5
} storage_err_t;

/* Таблиця віртуальних методів (VTable) для C-адаптера */
struct storage_adapter_ops {
    storage_err_t (*write_object)(storage_adapter_t *self, const char *key, const void *buf, size_t len);
    storage_err_t (*read_object)(storage_adapter_t *self, const char *key, void *buf, size_t max_len, size_t *out_len);
    storage_err_t (*delete_object)(storage_adapter_t *self, const char *key);
    void (*destroy)(storage_adapter_t *self);
};

struct storage_adapter {
    const struct storage_adapter_ops *ops;
    void *ctx; /* Приватний контекст реалізації (креденціали, fd, сокети) */
};

/* Фабричні функції для створення конкретних адаптерів */
storage_adapter_t *storage_adapter_create_posix(const char *base_dir);
storage_adapter_t *storage_adapter_create_cloud(const char *endpoint, const char *bucket, const char *access_key);

#ifdef __cplusplus
}
#endif

#endif /* STORAGE_ADAPTER_H */
```

```cpp
// storage_adapter.hpp — Ідіоматичний C++20 портативний інтерфейс сховища
#pragma once

#include <memory>
#include <string_view>
#include <span>
#include <vector>
#include <expected>
#include <system_error>
#include <filesystem>
#include <fstream>
#include <iostream>

enum class StorageError {
    NotFound,
    AccessDenied,
    NetworkFailure,
    IoError,
    InvalidArgument
};

// Абстрактний інтерфейс сховища об'єктів (Порт)
class StorageAdapter {
public:
    virtual ~StorageAdapter() = default;

    [[nodiscard]] virtual std::expected<void, StorageError> 
    write_object(std::string_view key, std::span<const std::byte> data) noexcept = 0;

    [[nodiscard]] virtual std::expected<std::vector<std::byte>, StorageError> 
    read_object(std::string_view key) noexcept = 0;

    [[nodiscard]] virtual std::expected<void, StorageError> 
    delete_object(std::string_view key) noexcept = 0;
};

// Адаптер для локальної POSIX файлової системи (Fallback / Local Dev)
class PosixStorageAdapter final : public StorageAdapter {
public:
    explicit PosixStorageAdapter(std::filesystem::path base_path)
        : base_path_(std::move(base_path)) {}

    std::expected<void, StorageError> 
    write_object(std::string_view key, std::span<const std::byte> data) noexcept override {
        try {
            auto full_path = base_path_ / key;
            std::filesystem::create_directories(full_path.parent_path());

            std::ofstream file(full_path, std::ios::binary | std::ios::trunc);
            if (!file) return std::unexpected(StorageError::IoError);

            file.write(reinterpret_cast<const char*>(data.data()), static_cast<std::streamsize>(data.size()));
            file.flush();
            return {};
        } catch (...) {
            return std::unexpected(StorageError::IoError);
        }
    }

    std::expected<std::vector<std::byte>, StorageError> 
    read_object(std::string_view key) noexcept override {
        try {
            auto full_path = base_path_ / key;
            if (!std::filesystem::exists(full_path)) {
                return std::unexpected(StorageError::NotFound);
            }

            std::ifstream file(full_path, std::ios::binary | std::ios::ate);
            if (!file) return std::unexpected(StorageError::IoError);

            auto size = file.tellg();
            file.seekg(0, std::ios::beg);

            std::vector<std::byte> buffer(static_cast<size_t>(size));
            file.read(reinterpret_cast<char*>(buffer.data()), size);
            return buffer;
        } catch (...) {
            return std::unexpected(StorageError::IoError);
        }
    }

    std::expected<void, StorageError> 
    delete_object(std::string_view key) noexcept override {
        try {
            auto full_path = base_path_ / key;
            if (std::filesystem::remove(full_path)) return {};
            return std::unexpected(StorageError::NotFound);
        } catch (...) {
            return std::unexpected(StorageError::IoError);
        }
    }

private:
    std::filesystem::path base_path_;
};
```
:::

---

## 2. Реалізація драйвера локального зберігання (POSIX Driver)

Для забезпечення повної працездатності C-модуля наведемо реалізацію адаптера локального диска, який використовує стандартні POSIX системні виклики файлової системи.

### Деталі внутрішньої механіки POSIX-драйвера

1. **Динамічне виділення приватного контексту:** При виклику `storage_adapter_create_posix` виділяється структура `posix_ctx_t`, яка зберігає базовий каталог зберігання. Ця структура зв'язується з полями `adapter->ctx`.
2. **Атомарний запис та скидання буферів:** Функція `posix_write` виконує запис бінарного буфера у файл і обов'язково викликає `fflush(f)` для гарантії того, що дані потрапили в операційну систему до повернення успішного статусу.
3. **Обробка та валідація розмірів пам'яті:** Під час читання у `posix_read` виконується позиціонування `fseek(f, 0, SEEK_END)` для визначення точного розміру файла на диску. Якщо переданий буфер `max_len` є меншим за фактичний розмір файла, повертається код помилки `STORAGE_ERR_IO`, запобігаючи переповненню буфера в пам'яті.
4. **Очищення ресурсів:** Виклик `posix_destroy` послідовно звільняє контекст драйвера та головну структуру адаптера, виключаючи витоки пам'яті.

:::tabs
```c
/* storage_adapter_posix.c — POSIX-реалізація портативного адаптера мовою C */
#include "storage_adapter.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char base_dir[256];
} posix_ctx_t;

static storage_err_t posix_write(storage_adapter_t *self, const char *key, const void *buf, size_t len) {
    if (!self || !self->ctx || !key || !buf) return STORAGE_ERR_INVALID_PARAM;
    posix_ctx_t *ctx = (posix_ctx_t *)self->ctx;

    char path[512];
    snprintf(path, sizeof(path), "%s/%s", ctx->base_dir, key);

    FILE *f = fopen(path, "wb");
    if (!f) return STORAGE_ERR_IO;

    size_t written = fwrite(buf, 1, len, f);
    fflush(f);
    fclose(f);

    return (written == len) ? STORAGE_OK : STORAGE_ERR_IO;
}

static storage_err_t posix_read(storage_adapter_t *self, const char *key, void *buf, size_t max_len, size_t *out_len) {
    if (!self || !self->ctx || !key || !buf || !out_len) return STORAGE_ERR_INVALID_PARAM;
    posix_ctx_t *ctx = (posix_ctx_t *)self->ctx;

    char path[512];
    snprintf(path, sizeof(path), "%s/%s", ctx->base_dir, key);

    FILE *f = fopen(path, "rb");
    if (!f) return STORAGE_ERR_NOT_FOUND;

    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);

    if ((size_t)size > max_len) {
        fclose(f);
        return STORAGE_ERR_IO;
    }

    size_t read_bytes = fread(buf, 1, size, f);
    fclose(f);
    *out_len = read_bytes;

    return STORAGE_OK;
}

static storage_err_t posix_delete(storage_adapter_t *self, const char *key) {
    if (!self || !self->ctx || !key) return STORAGE_ERR_INVALID_PARAM;
    posix_ctx_t *ctx = (posix_ctx_t *)self->ctx;

    char path[512];
    snprintf(path, sizeof(path), "%s/%s", ctx->base_dir, key);

    if (remove(path) == 0) return STORAGE_OK;
    return STORAGE_ERR_NOT_FOUND;
}

static void posix_destroy(storage_adapter_t *self) {
    if (self) {
        if (self->ctx) free(self->ctx);
        free(self);
    }
}

static const struct storage_adapter_ops posix_ops = {
    .write_object = posix_write,
    .read_object = posix_read,
    .delete_object = posix_delete,
    .destroy = posix_destroy
};

storage_adapter_t *storage_adapter_create_posix(const char *base_dir) {
    storage_adapter_t *adapter = (storage_adapter_t *)malloc(sizeof(storage_adapter_t));
    if (!adapter) return NULL;

    posix_ctx_t *ctx = (posix_ctx_t *)malloc(sizeof(posix_ctx_t));
    if (!ctx) {
        free(adapter);
        return NULL;
    }

    strncpy(ctx->base_dir, base_dir, sizeof(ctx->base_dir) - 1);
    ctx->base_dir[sizeof(ctx->base_dir) - 1] = '\0';

    adapter->ops = &posix_ops;
    adapter->ctx = ctx;

    return adapter;
}
```

```cpp
// storage_adapter_cloud.hpp — Хмарний адаптер C++ (Абстрагований REST Client)
#pragma once
#include "storage_adapter.hpp"
#include <iostream>

class CloudStorageAdapter final : public StorageAdapter {
public:
    CloudStorageAdapter(std::string endpoint, std::string bucket, std::string access_key)
        : endpoint_(std::move(endpoint)), bucket_(std::move(bucket)), access_key_(std::move(access_key)) {}

    std::expected<void, StorageError> 
    write_object(std::string_view key, std::span<const std::byte> data) noexcept override {
        // У продакшені тут використовується стандартизований HTTP/gRPC REST API
        // Без імпорту proprietary SDK провайдера у публічні заголовки
        std::cout << "[CloudStorage] PUT " << endpoint_ << "/" << bucket_ << "/" << key 
                  << " (" << data.size() << " bytes) [AUTH: OK]\n";
        return {};
    }

    std::expected<std::vector<std::byte>, StorageError> 
    read_object(std::string_view key) noexcept override {
        std::cout << "[CloudStorage] GET " << endpoint_ << "/" << bucket_ << "/" << key << "\n";
        return std::vector<std::byte>{};
    }

    std::expected<void, StorageError> 
    delete_object(std::string_view key) noexcept override {
        std::cout << "[CloudStorage] DELETE " << endpoint_ << "/" << bucket_ << "/" << key << "\n";
        return {};
    }

private:
    std::string endpoint_;
    std::string bucket_;
    std::string access_key_;
};
```
:::

---

## 3. Скрипт потокової евакуації даних (CDC Streaming Evacuation Pipeline)

Коли виникає потреба евакуювати живий продакшн-сервіс із хмари без зупинки системи (Zero Downtime), розробники розгортають конвеєр Change Data Capture (CDC). Цей модуль читає журнал змін хмарної бази даних у реальному часі, конвертує proprietary-типи вендора у відкритий нейтральний формат (наприклад, JSON Lines або Apache Parquet) та записує їх у нове нейтральне сховище.

### Послідовність дій під час евакуаційного транзиту

Процес потокової евакуації складається з чотирьох послідовних кроків:

1. **Зчитування журналу змін (Log Consumer):** Конвеєр підключається до потоку подій хмарної бази даних (наприклад, DynamoDB Streams, AWS Kinesis або Debezium CDC) і зчитує нові пачки записів.
2. **Нейтралізація схем даних (Schema Normalization):** Спеціальний транслятор `NeutralSchemaConverter` знімає proprietary-обгортки вендора (наприклад, DynamoDB-структури `{"S": "value"}` або `{"N": "42"}`) і приводить записи до звичайного словника з базовими типами (String, Float, Int, Bool).
3. **Обчислення контрольних сум (Checksum Verification):** Для кожного нейтралізованого запису обчислюється криптографічний хеш SHA-256 від його канонічної JSON-представлення. Цей хеш зберігається поруч із записом для подальшої валідації цілісності.
4. **Запис у цільове відкрите сховище (Target Writer):** Оброблені записи передаються адаптеру цільової бази даних (наприклад, PostgreSQL або MinIO) з підтримкою подвійного запису або відкладеної дедуплікації.

Нижче наведено розширений вихідний код Python-модуля для проведення потокової евакуації телеметрії з повним журналюванням та обробкою помилок.

```python
#!/usr/bin/env python3
"""
evacuation_pipeline.py — Потоковий пайплайн евакуаційного транслятора даних
"""
import hashlib
import json
import logging
import time
import typing
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

@dataclass
class EvacuationRecord:
    record_id: str
    timestamp: float
    payload: dict
    checksum: str

class NeutralSchemaConverter:
    """Нормалізує proprietary-типи вендора (DynamoDB/CosmosDB) у відкритий канонічний формат"""

    @staticmethod
    def convert_dynamodb_record(vendor_record: dict) -> EvacuationRecord:
        raw_payload = vendor_record.get("Item", {})
        clean_payload = {}

        # Рекурсивне зняття proprietary-тегів типу {"S": "val"}, {"N": "42"}
        for key, val in raw_payload.items():
            if isinstance(val, dict):
                if "S" in val:
                    clean_payload[key] = str(val["S"])
                elif "N" in val:
                    clean_payload[key] = float(val["N"]) if "." in str(val["N"]) else int(val["N"])
                elif "BOOL" in val:
                    clean_payload[key] = bool(val["BOOL"])
                elif "M" in val:
                    clean_payload[key] = val["M"]
                else:
                    clean_payload[key] = str(val)
            else:
                clean_payload[key] = val

        rec_id = str(clean_payload.get("id", "unknown_id"))
        ts = float(vendor_record.get("CreatedAt", time.time()))

        # Обчислення канонічного SHA-256 хешу для перевірки цілісності
        serialized = json.dumps(clean_payload, sort_keys=True)
        chksum = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        return EvacuationRecord(record_id=rec_id, timestamp=ts, payload=clean_payload, checksum=chksum)

class EvacuationStreamPipeline:
    def __init__(self, target_writer: typing.Callable[[EvacuationRecord], bool], batch_size: int = 100):
        self.writer = target_writer
        self.batch_size = batch_size
        self.evacuated_count = 0
        self.failed_count = 0

    def process_stream_batch(self, vendor_batch: typing.List[dict]) -> dict:
        start_time = time.time()
        logging.info(f"Starting batch evacuation of {len(vendor_batch)} items...")

        for raw_item in vendor_batch:
            try:
                record = NeutralSchemaConverter.convert_dynamodb_record(raw_item)
                success = self.writer(record)
                if success:
                    self.evacuated_count += 1
                else:
                    self.failed_count += 1
                    logging.warning(f"Target writer rejected record {record.record_id}")
            except Exception as err:
                self.failed_count += 1
                logging.error(f"Critical error converting record: {err}")

        duration = time.time() - start_time
        logging.info(f"Batch completed in {duration:.3f}s. Evacuated: {self.evacuated_count}, Failed: {self.failed_count}")
        return {"evacuated": self.evacuated_count, "failed": self.failed_count, "duration": duration}

def open_postgres_target_writer(record: EvacuationRecord) -> bool:
    """Імітація зчитування нейтрального запису та збереження у відкритий PostgreSQL/MinIO-кластер"""
    # У продакшені тут викликається SQL `INSERT INTO telemetry VALUES (...) ON CONFLICT DO UPDATE`
    if not record.checksum:
        return False
    return True

if __name__ == "__main__":
    # Тестовий потік даних у proprietary-форматі DynamoDB Streams
    sample_vendor_stream = [
        {
            "Item": {
                "id": {"S": "sensor_living_room_01"},
                "temp": {"N": "22.4"},
                "humidity": {"N": "45.0"},
                "active": {"BOOL": True}
            },
            "CreatedAt": 1690000000
        },
        {
            "Item": {
                "id": {"S": "sensor_kitchen_02"},
                "temp": {"N": "26.1"},
                "humidity": {"N": "58.2"},
                "active": {"BOOL": True}
            },
            "CreatedAt": 1690000100
        }
    ]

    pipeline = EvacuationStreamPipeline(target_writer=open_postgres_target_writer)
    stats = pipeline.process_stream_batch(sample_vendor_stream)
    print(f"\nFinal Summary: {stats['evacuated']} records successfully migrated.")
```

---

## 4. Конфігурування та обробка крайових випадків (Edge Cases)

При розгортанні евакуаційного конвеєра в реальних продакшн-умовах інженери зіштовхуються з серією крайових випадків, які мають бути передбачені в інфраструктурній конфігурації:

### 1. Дрейф схем даних (Schema Drift)

Під час тривалого процесу евакуації команда продукту продовжує розробку та додає нові поля у хмарну базу даних. Якщо конвертер схеми не розрахований на нові атрибути, виникає ризик прихованої втрати даних. 

Для запобігання цьому `NeutralSchemaConverter` підтримує відкритий динамічний атрибут `payload`, у який зберігаються всі нерозпізнані поля у вигляді універсального документа JSONB. Це дозволяє розпакувати нові дані вже після завершення перенесення основного масиву.

### 2. Мережеві збої та збереження контрольних точок (Checkpointing)

Під час потокової міграції мільйонів записів мережеве з'єднання між хмарами може перерватися. Якщо конвеєр фіксує прочитаний зсув (Offset Commit) до того, як записи гарантовано збережені у цільовому відкритому сховищі, виникає втрата подій. 

Правильна інженерна практика вимагає двофазної фіксації: зсув у хмарному CDC-потоці оновлюється виключно після того, як цільова СУБД повернула успішний статус підтвердження транзакції (`ACK`) та виконала скидання дискового буфера (`fsync`).

### 3. Дедуплікація під час повторних спроб (At-Least-Once Delivery & Idempotency)

Мережеві ретраї та аварійне перезавантаження воркерів евакуації неминуче призводять до повторної доставки одних і тих самих записів. 

Для забезпечення ідемпотентності цільова СУБД повинна використовувати операцію вибіркового оновлення за унікальним ключем: `INSERT INTO target_table VALUES (...) ON CONFLICT (record_id) DO UPDATE SET payload = EXCLUDED.payload`. Це гарантує, що повторне проходження одного й того самого пакета даних не призведе до дублювання рядків або спотворення аналітичних звітів.

### 4. Обробка зворотного тиску (Backpressure Management)

Якщо швидкість генерації нових подій у старій хмарній базі даних перевищує throughput-спроможність нової цільової бази даних, конвеєр евакуації починає накопичувати незаписані об'єкти в оперативній пам'яті. 

Для захисту від аварійного вичерпання пам'яті (Out-Of-Memory Panic) конвеєр реалізує алгоритм обмеження швидкості читання (Rate Limiting / Token Bucket). Якщо розмір внутрішньої черги воркера перевищує порогове значення (наприклад, 5 000 об'єктів), зчитування нових пакетів із CDC-потоку тимчасово призупиняється до повного скидання накопиченого буфера у цільове сховище.
