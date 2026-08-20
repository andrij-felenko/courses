# ⚙️ Рушій журналу випереджувального запису (WAL) та відновлення стану

Надійний клієнтський документ мусить витримувати непередбачувані аварійні зупинки процесу без втрати незбережених змін та без ризику пошкодження дискових файлів. Повне перезаписування документа на кожну дію користувача виснажує накопичувач і блокує інтерфейс, тоді як відкладене автозбереження залишає велике вікно вразливості, у якому втрачаються останні хвилини роботи.

Нижче наведено робочу реалізацію рушія стійкості, що об'єднує двійковий журнал випереджувального запису (WAL) із перевіркою контрольних сум CRC32, атомарну фіксацію контрольних точок (Checkpointing) та автоматичне відновлення стану при холодному старті.

## Завдання та структура бінарного формату

Рушій керує трьома пов'язаними файлами в робочому каталозі документа:
1. `document.snap` — базовий стан документа (повний знімок на момент останньої контрольної точки);
2. `document.wal` — послідовний журнал операцій (дописується лише в кінець, append-only);
3. `document.lock` — файл координації ексклюзивного доступу (запобігає одночасному відкриттю кількома процесами).

Кожен окремий запис у файлі журналу `document.wal` має суворо фіксовану бінарну структуру (обрамлення запису):

```
+---------------+---------------+-------------------+-------------------+-------------------+---------------+
| Magic (4B)    | SeqNum (8B)   | Timestamp (8B)    | PayloadLen (4B)   | Payload (N bytes) | CRC32 (4B)    |
| 0x57414C31    | uint64_t      | int64_t (Unix ms) | uint32_t          | utf-8 / binary    | IEEE 802.3    |
+---------------+---------------+-------------------+-------------------+-------------------+---------------+
```

Заголовок має довжину 24 байти. Поле `Magic` містить сигнатуру `0x57414C31` (ASCII-рядок `WAL1`). Поле `SeqNum` забезпечує монотонну нумерацію операцій, що гарантує строгий порядок виконання під час повтору. Поле `PayloadLen` визначає кількість байтів у тілі мутації.

Контрольна сума CRC32 обчислюється від корисного навантаження (або всього запису) за поліномом IEEE 802.3 (`0xEDB88320`). Вибір некриптографічного алгоритму CRC32 замість важких SHA-256 чи MD5 зумовлений швидкістю: обчислення CRC32 на сучасних процесорах виконується зі швидкістю понад 3 ГБ/с на ядро (а з використанням інструкцій SSE4.2 / ARM CRC32 — до 15 ГБ/с), що повністю усуває затримки при швидкому введенні тексту.

Якщо процес завершився аварійно прямо під час запису операції (розірваний запис), алгоритм відновлення виявляє невідповідність CRC32 на хвості файлу, відкидає пошкоджений фрагмент і відновлює всі попередні коректні транзакції.

![Життєвий цикл WAL і відновлення стану: від базового знімка до перегравання послідовності валідних операцій](/book/programming/client-architecture/client-crash-recovery/img/wal-and-snapshot-lifecycle.svg)
*При завантаженні застосунок спочатку читає базовий знімок, після чого послідовно застосовує всі валідні записи з журналу WAL.*

## Реалізація рушія

:::tabs
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <chrono>
#include <numeric>
#include <stdexcept>
#include <span>

#if defined(_WIN32)
#include <windows.h>
#else
#include <unistd.h>
#include <fcntl.h>
#include <sys/file.h>
#endif

namespace fs = std::filesystem;

// ── Алгоритм CRC32 (IEEE 802.3) ─────────────────────────────────────────────
class Crc32 {
public:
    static uint32_t calculate(std::span<const uint8_t> data) {
        uint32_t crc = 0xFFFFFFFFu;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (int k = 0; k < 8; ++k) {
                crc = (crc >> 1) ^ (0xEDB88320u & -(crc & 1));
            }
        }
        return ~crc;
    }
};

// ── Заголовок запису в журналі WAL ──────────────────────────────────────────
#pragma pack(push, 1)
struct WalHeader {
    uint32_t magic;       // 0x57414C31 ("WAL1")
    uint64_t seq_num;     // Монотонний номер операції
    int64_t  timestamp;   // Час створення в мілісекундах
    uint32_t payload_len; // Довжина тіла операції в байтах
};
#pragma pack(pop)

constexpr uint32_t WAL_MAGIC = 0x57414C31;

// ── Документ у пам'яті (проста модель текстових рядків) ─────────────────────
class DocumentModel {
public:
    void apply_operation(std::string_view op) {
        // Формат операції: "INSERT:<рядок>" або "CLEAR"
        if (op.starts_with("INSERT:")) {
            lines_.emplace_back(op.substr(7));
        } else if (op == "CLEAR") {
            lines_.clear();
        }
    }

    [[nodiscard]] std::string serialize() const {
        std::string out;
        for (const auto& line : lines_) {
            out += line;
            out += '\n';
        }
        return out;
    }

    void deserialize(std::string_view content) {
        lines_.clear();
        size_t start = 0;
        while (start < content.size()) {
            size_t end = content.find('\n', start);
            if (end == std::string_view::npos) end = content.size();
            if (end > start) {
                lines_.emplace_back(content.substr(start, end - start));
            }
            start = end + 1;
        }
    }

    const std::vector<std::string>& get_lines() const { return lines_; }

private:
    std::vector<std::string> lines_;
};

// ── Менеджер стійкості до крахів ────────────────────────────────────────────
class CrashResilientStore {
public:
    CrashResilientStore(fs::path base_path)
        : base_path_(std::move(base_path)),
          snap_path_(base_path_.string() + ".snap"),
          wal_path_(base_path_.string() + ".wal"),
          lock_path_(base_path_.string() + ".lock") {}

    ~CrashResilientStore() {
        release_lock();
    }

    // Захоплення ексклюзивного блокування (Lease)
    bool acquire_lock() {
#if defined(_WIN32)
        lock_handle_ = CreateFileW(lock_path_.c_str(), GENERIC_READ | GENERIC_WRITE,
                                   0, nullptr, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
        return lock_handle_ != INVALID_HANDLE_VALUE;
#else
        lock_fd_ = ::open(lock_path_.c_str(), O_RDWR | O_CREAT, 0666);
        if (lock_fd_ < 0) return false;
        return ::flock(lock_fd_, LOCK_EX | LOCK_NB) == 0;
#endif
    }

    // Завантаження та відновлення стану після краху
    void recover(DocumentModel& model) {
        // Крок 1: Читання базового знімка (якщо існує)
        if (fs::exists(snap_path_)) {
            std::ifstream snap_file(snap_path_, std::ios::binary);
            std::string content((std::istreambuf_iterator<char>(snap_file)),
                                 std::istreambuf_iterator<char>());
            model.deserialize(content);
        }

        // Крок 2: Програвання операцій із журналу WAL
        if (!fs::exists(wal_path_)) return;

        std::ifstream wal_file(wal_path_, std::ios::binary);
        std::vector<uint8_t> wal_data((std::istreambuf_iterator<char>(wal_file)),
                                       std::istreambuf_iterator<char>());

        size_t offset = 0;
        size_t valid_operations = 0;

        while (offset + sizeof(WalHeader) + sizeof(uint32_t) <= wal_data.size()) {
            WalHeader header;
            std::memcpy(&header, wal_data.data() + offset, sizeof(WalHeader));

            if (header.magic != WAL_MAGIC) break;

            size_t total_record_size = sizeof(WalHeader) + header.payload_len + sizeof(uint32_t);
            if (offset + total_record_size > wal_data.size()) {
                // Розірваний запис на хвості файлу — відкидаємо
                break;
            }

            // Перевірка контрольної суми CRC32
            uint32_t stored_crc;
            std::memcpy(&stored_crc, wal_data.data() + offset + sizeof(WalHeader) + header.payload_len, sizeof(uint32_t));

            std::span<const uint8_t> payload_span(wal_data.data() + offset + sizeof(WalHeader), header.payload_len);
            uint32_t computed_crc = Crc32::calculate(payload_span);

            if (computed_crc != stored_crc) {
                // Пошкодження даних — зупиняємо повтор на останньому валідному записі
                break;
            }

            std::string op(reinterpret_cast<const char*>(payload_span.data()), payload_span.size());
            model.apply_operation(op);

            seq_num_ = std::max(seq_num_, header.seq_num);
            offset += total_record_size;
            valid_operations++;
        }

        // Крок 3: Якщо було відновлено операції, закріплюємо їх свіжим знімком
        if (valid_operations > 0) {
            checkpoint(model);
        }
    }

    // Запис нової операції в журнал WAL
    void append_operation(std::string_view op) {
        std::vector<uint8_t> buffer;
        WalHeader header;
        header.magic = WAL_MAGIC;
        header.seq_num = ++seq_num_;
        header.timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
        header.payload_len = static_cast<uint32_t>(op.size());

        auto header_bytes = reinterpret_cast<const uint8_t*>(&header);
        buffer.insert(buffer.end(), header_bytes, header_bytes + sizeof(WalHeader));

        auto op_bytes = reinterpret_cast<const uint8_t*>(op.data());
        buffer.insert(buffer.end(), op_bytes, op_bytes + op.size());

        std::span<const uint8_t> payload_span(op_bytes, op.size());
        uint32_t crc = Crc32::calculate(payload_span);
        auto crc_bytes = reinterpret_cast<const uint8_t*>(&crc);
        buffer.insert(buffer.end(), crc_bytes, crc_bytes + sizeof(uint32_t));

        // Дописування у файл
        std::ofstream wal_out(wal_path_, std::ios::binary | std::ios::app);
        wal_out.write(reinterpret_cast<const char*>(buffer.data()), buffer.size());
        wal_out.flush();
    }

    // Створення контрольної точки (Checkpoint): атомарний знімок + очищення WAL
    void checkpoint(const DocumentModel& model) {
        fs::path tmp_snap = snap_path_.string() + ".tmp";
        std::string serialized = model.serialize();

        // 1. Запис у тимчасовий файл
        {
            std::ofstream out(tmp_snap, std::ios::binary | std::ios::trunc);
            out.write(serialized.data(), serialized.size());
            out.flush();
        }

        // 2. Атомарна підміна файлу
        fs::rename(tmp_snap, snap_path_);

        // 3. Обрізання журналу WAL
        std::ofstream wal_truncate(wal_path_, std::ios::binary | std::ios::trunc);
        wal_truncate.close();
    }

private:
    void release_lock() {
#if defined(_WIN32)
        if (lock_handle_ != INVALID_HANDLE_VALUE) {
            CloseHandle(lock_handle_);
            lock_handle_ = INVALID_HANDLE_VALUE;
        }
#else
        if (lock_fd_ >= 0) {
            ::flock(lock_fd_, LOCK_UN);
            ::close(lock_fd_);
            lock_fd_ = -1;
        }
#endif
    }

    fs::path base_path_;
    fs::path snap_path_;
    fs::path wal_path_;
    fs::path lock_path_;
    uint64_t seq_num_{0};

#if defined(_WIN32)
    HANDLE lock_handle_{INVALID_HANDLE_VALUE};
#else
    int lock_fd_{-1};
#endif
};
```
```ts
import * as fs from "fs";
import * as path from "path";

// ── Табличний розрахунок CRC32 (IEEE 802.3) ──────────────────────────────────
class Crc32 {
  private static table: Uint32Array = (() => {
    const tbl = new Uint32Array(256);
    for (let i = 0; i < 256; i++) {
      let c = i;
      for (let k = 0; k < 8; k++) {
        c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      }
      tbl[i] = c >>> 0;
    }
    return tbl;
  })();

  static calculate(buf: Buffer): number {
    let crc = 0xffffffff;
    for (let i = 0; i < buf.length; i++) {
      crc = (crc >>> 8) ^ Crc32.table[(crc ^ buf[i]) & 0xff];
    }
    return (crc ^ 0xffffffff) >>> 0;
  }
}

const WAL_MAGIC = 0x57414c31; // "WAL1"
const HEADER_SIZE = 24; // Magic(4) + Seq(8) + Timestamp(8) + Len(4)

// ── Документ у пам'яті ──────────────────────────────────────────────────────
export class DocumentModel {
  private lines: string[] = [];

  applyOperation(op: string): void {
    if (op.startsWith("INSERT:")) {
      this.lines.push(op.slice(7));
    } else if (op === "CLEAR") {
      this.lines = [];
    }
  }

  serialize(): string {
    return this.lines.join("\n") + "\n";
  }

  deserialize(content: string): void {
    this.lines = content.split("\n").filter((l) => l.length > 0);
  }

  getLines(): string[] {
    return [...this.lines];
  }
}

// ── Менеджер аварійної стійкості (Write-Ahead Log + Snapshotting) ────────────
export class CrashResilientStore {
  private snapPath: string;
  private walPath: string;
  private lockPath: string;
  private seqNum = 0n;
  private lockFd: number | null = null;

  constructor(basePath: string) {
    this.snapPath = `${basePath}.snap`;
    this.walPath = `${basePath}.wal`;
    this.lockPath = `${basePath}.lock`;
  }

  // Ексклюзивне блокування через відкриття з прапорцем O_EXCL
  acquireLock(): boolean {
    try {
      this.lockFd = fs.openSync(this.lockPath, fs.constants.O_CREAT | fs.constants.O_EXCL | fs.constants.O_RDWR);
      return true;
    } catch {
      return false; // Файл уже заблоковано іншим процесом
    }
  }

  releaseLock(): void {
    if (this.lockFd !== null) {
      fs.closeSync(this.lockFd);
      try { fs.unlinkSync(this.lockPath); } catch {}
      this.lockFd = null;
    }
  }

  // Відновлення після аварії
  recover(model: DocumentModel): void {
    // 1. Читання базового знімка
    if (fs.existsSync(this.snapPath)) {
      const snapContent = fs.readFileSync(this.snapPath, "utf-8");
      model.deserialize(snapContent);
    }

    // 2. Читання та валідація журналу WAL
    if (!fs.existsSync(this.walPath)) return;

    const walBuffer = fs.readFileSync(this.walPath);
    let offset = 0;
    let validOps = 0;

    while (offset + HEADER_SIZE + 4 <= walBuffer.length) {
      const magic = walBuffer.readUInt32LE(offset);
      if (magic !== WAL_MAGIC) break;

      const seq = walBuffer.readBigUInt64LE(offset + 4);
      const payloadLen = walBuffer.readUInt32LE(offset + 20);

      const totalSize = HEADER_SIZE + payloadLen + 4;
      if (offset + totalSize > walBuffer.length) {
        // Розірваний запис на хвості файлу — крах перервав запис
        break;
      }

      const payloadBuf = walBuffer.subarray(offset + HEADER_SIZE, offset + HEADER_SIZE + payloadLen);
      const storedCrc = walBuffer.readUInt32LE(offset + HEADER_SIZE + payloadLen);

      // Перевірка цілісності корисного навантаження
      if (Crc32.calculate(payloadBuf) !== storedCrc) {
        // Спотворені байти — зупинка відновлення
        break;
      }

      const op = payloadBuf.toString("utf-8");
      model.applyOperation(op);

      if (seq > this.seqNum) this.seqNum = seq;
      offset += totalSize;
      validOps++;
    }

    // 3. Автоматичний знімок після відновлення для очищення обробленого WAL
    if (validOps > 0) {
      this.checkpoint(model);
    }
  }

  // Дописування операції в кінець WAL
  appendOperation(op: string): void {
    this.seqNum++;
    const payloadBuf = Buffer.from(op, "utf-8");
    const crc = Crc32.calculate(payloadBuf);

    const record = Buffer.alloc(HEADER_SIZE + payloadBuf.length + 4);
    record.writeUInt32LE(WAL_MAGIC, 0);
    record.writeBigUInt64LE(this.seqNum, 4);
    record.writeBigInt64LE(BigInt(Date.now()), 12);
    record.writeUInt32LE(payloadBuf.length, 20);

    payloadBuf.copy(record, HEADER_SIZE);
    record.writeUInt32LE(crc, HEADER_SIZE + payloadBuf.length);

    fs.appendFileSync(this.walPath, record);
  }

  // Контрольна точка: атомарний знімок + truncate WAL
  checkpoint(model: DocumentModel): void {
    const tmpSnap = `${this.snapPath}.tmp`;
    fs.writeFileSync(tmpSnap, model.serialize(), "utf-8");

    // Атомарна підміна
    fs.renameSync(tmpSnap, this.snapPath);

    // Очищення файлу журналу
    fs.writeFileSync(this.walPath, Buffer.alloc(0));
  }
}
```
:::

## Покроковий розбір алгоритму та підводні камені

Коректна робота алгоритму стійкості до відмов спирається на суворе дотримання послідовності операцій та обробку граничних станів.

### 1. Сканування та відсікання пошкодженого хвоста (Torn Tail)

Під час аварійного вимкнення живлення остання операція може бути записана на диск лише частково. Якщо файл `document.wal` обірвався посеред заголовка або корисного навантаження, цикл відновлення виявляє одну з трьох типових ситуацій:
- Кількість залишкових байтів у буфері файлу менша за розмір мінімального заголовка (24 байти);
- Поле `Magic` містить нулі або некоректне значення замість сигнатури `0x57414C31`;
- Обчислена контрольна сума `Crc32::calculate(payload)` не збігається зі значенням `stored_crc` у кінці запису.

У кожному з цих випадків цикл парсингу негайно виконує команду `break`. Це принциповий момент: **помилка валідації на хвості журналу не є фатальною катастрофою**. Вона свідчить про те, що аварія перервала останню незавершену транзакцію вводу-виводу. Усі попередні операції, які успішно пройшли перевірку CRC32, гарантовано цілісні й послідовно застосовуються до моделі.

Проте якщо помилка CRC32 виявляється **посередині файлу**, а за нею йдуть інші валідні заголовки, це свідчить про фізичне спотворення накопичувача (Bit Flip або збій сектора). У такій ситуації рушій зобов'язаний зупинити відновлення та попередити користувача, оскільки застосування наступних правок на дефектному стані призведе до розбіжності моделі.

### 2. Атомарність знімка через створення файлу-двійника

Функція `checkpoint` ніколи не записує серіалізований стан безпосередньо у файл `document.snap`. Замість цього створюється тимчасовий файл `document.snap.tmp`. Лише після того, як буфери повністю записані на диск, викликається системна функція `rename` (у Node.js — `renameSync`).

Якщо живлення зникне під час виконання `checkpoint`:
- Базовий файл `document.snap` залишиться старим, але повністю валідним;
- Усі операції, які ще не закріпилися новим знімком, зберігаються у файлі `document.wal`;
- При наступному запуску застосунок коректно відтворить стан зі старого знімка та повного журналу.

### 3. Ексклюзивне блокування та запобігання гонитві процесів

Якщо користувач помилково відкриє той самий документ у двох вікнах програми одночасно, виникає ризик перехресного запису в один файл `document.wal`. Обидва процеси намагатимуться дописувати байти за різними зміщеннями, що призведе до незворотного спотворення бінарних рамок.

Метод `acquire_lock` використовує атомарне блокування на рівні ядра ОС:
- У POSIX-системах виклик `flock(lock_fd, LOCK_EX | LOCK_NB)` повертає помилку, якщо інший процес уже утримує дескриптор;
- У середовищі Windows виклик `CreateFileW` із нульовим прапорцем спільного доступу (`dwShareMode = 0`) забороняє паралельне відкриття файлу іншими процесами;
- У Node.js створення файлу з прапорцем `O_EXCL` гарантує атомарну перевірку створення.

Якщо блокування не вдалося захопити, застосунок повинен повідомити користувача про небезпеку та перейти в безпечний режим перегляду без права запису змін.

### 4. Робота з нульовими копіями пам'яті (Zero-Copy Spans)

У реалізації C++ для парсингу корисної інформації використовується тип `std::span<const uint8_t>`. Він дозволяє обчислювати CRC32 та декодувати текст без виділення додаткової пам'яті в купі (heap allocation) на кожен запис. Увесь файл `document.wal` зчитується в один неперервний вектор, після чого парсер переміщує ковзне вікно по байтах, що гарантує максимальну пропускну здатність під час холодного старту.
