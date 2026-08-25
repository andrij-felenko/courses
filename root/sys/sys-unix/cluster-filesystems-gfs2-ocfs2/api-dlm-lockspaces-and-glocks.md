# 📋 Інтерфейси Distributed Lock Manager (DLM) та керування glocks у sysfs/debugfs

Цей довідник містить системні інтерфейси програмування та діагностичні вузли ядра Linux, що забезпечують роботу розподіленого менеджера блокувань (*Distributed Lock Manager*, DLM), механізму `glock` у файловій системі GFS2 та віртуальної файлової системи `dlmfs` у OCFS2. Довідник охоплює C та C++ API бібліотеки `libdlm`, структури блокувань ядра, бітові маски статусів, формат діагностичних файлів у `debugfs` та утиліти командного рядка для діагностики кластерного стану.

## 1. Системний інтерфейс libdlm (User-Space API)

Бібліотека `libdlm` надає інтерфейс користувацького простору для взаємодії з ядерним модулем `dlm.ko` через символьний пристрій `/dev/dlm-control` та сокети подій. Вона дозволяє створювати простори блокувань (*lockspaces*), ініціювати асинхронні запити на захоплення та конверсію режимів, а також обробляти зворотні виклики AST.

### Режими блокувань (Lock Modes)

Константи режимів визначають рівень монополії вузла над абстрактним ресурсом:

| Константа | Числове значення | Назва режиму | Сумісні режими запиту | Призначення у файлових системах |
| :--- | :--- | :--- | :--- | :--- |
| `DLM_LOCK_NL` | `0` | Null | Усі (`NL`, `CR`, `CW`, `PR`, `PW`, `EX`) | Утримання ресурсу без прав доступу (для кешування дескриптора) |
| `DLM_LOCK_CR` | `1` | Concurrent Read | `NL`, `CR`, `CW`, `PR`, `PW` | Неблоковане читання невпорядкованих даних |
| `DLM_LOCK_CW` | `2` | Concurrent Write | `NL`, `CR`, `CW` | Паралельний неблокований запис у різні частини структури |
| `DLM_LOCK_PR` | `3` | Protected Read (Shared) | `NL`, `CR`, `PR` | Захищене спільне читання (блокує будь-який запис) |
| `DLM_LOCK_PW` | `4` | Protected Write | `NL`, `CR` | Запис із дозволом іншим вузлам паралельно читати в режимі `CR` |
| `DLM_LOCK_EX` | `5` | Exclusive | `NL` | Повна монополія: читання і запис метаданих / екстентів |

### Структура блоку стану блокування (dlm_lksb)

Блок стану блокування (*Lock Status Block*, LKSB) є ключовою структурою передачі контексту між процесом та ядром. Він зберігає числовий ідентифікатор блокування в ядрі, результат завершення операції та покажчик на буфер значення блокування (*Lock Value Block*, LVB).

У мові C структура оголошується напряму з системного заголовка, тоді як в ідіоматичному C++ навколо неї створюється RAII-обгортка, яка автоматично контролює життєвий цикл блокування та виділення буфера LVB:

:::tabs
```c
#include <libdlm.h>
#include <stdint.h>

/* Системна структура LKSB з бібліотеки libdlm */
struct dlm_lksb {
    int      sb_status;  /* Результат операції (0 — успіх, або стандартний errno) */
    uint32_t sb_lkid;    /* Унікальний числовий ідентифікатор блокування (Lock ID) */
    char     sb_flags;   /* Прапорці зворотного зв'язку від ядра */
    char    *sb_lvbptr;  /* Покажчик на 32-байтовий або 64-байтовий буфер LVB */
};
```
```cpp
#include <libdlm.h>
#include <cstdint>
#include <vector>
#include <span>
#include <string_view>

/* Ідіоматична C++ обгортка над структурою dlm_lksb */
class DlmLockStatusBlock {
public:
    explicit DlmLockStatusBlock(size_t lvb_size = 64) 
        : lvb_buffer_(lvb_size, 0) {
        lksb_.sb_status = 0;
        lksb_.sb_lkid = 0;
        lksb_.sb_flags = 0;
        lksb_.sb_lvbptr = lvb_buffer_.empty() ? nullptr : lvb_buffer_.data();
    }

    [[nodiscard]] int status() const noexcept { return lksb_.sb_status; }
    [[nodiscard]] uint32_t lock_id() const noexcept { return lksb_.sb_lkid; }
    [[nodiscard]] dlm_lksb* raw_lksb() noexcept { return &lksb_; }
    [[nodiscard]] std::span<char> lvb() noexcept { return lvb_buffer_; }

private:
    dlm_lksb lksb_{};
    std::vector<char> lvb_buffer_;
};
```
:::

### Основні функції dlm_lock() та dlm_unlock()

Функція `dlm_ls_lock()` є головною точкою входу для створення або конверсії блокування. Вона приймає покажчики на дві функції зворотного виклику: `astaddr` (викликається, коли операція блокування завершена) та `bastaddr` (викликається, коли інший вузол вимагає несумісного режиму і власнику потрібно понизити свій рівень доступу).

:::tabs
```c
#include <libdlm.h>
#include <stdio.h>
#include <string.h>

/* Базовий приклад підключення до простору блокувань та виклику dlm_ls_lock у C */
int acquire_cluster_lock(dlm_lshandle_t ls, const char *res_name, uint32_t mode,
                         struct dlm_lksb *lksb, void (*ast)(void *), void (*bast)(void *, int)) {
    int status = dlm_ls_lock(ls,
                             mode,
                             lksb,
                             DLM_LKF_NOQUEUE,
                             res_name,
                             strlen(res_name),
                             0,            /* parent lock id */
                             ast,
                             lksb,         /* ast argument */
                             bast,
                             lksb);        /* bast argument */
    return status;
}
```
```cpp
#include <libdlm.h>
#include <string_view>
#include <functional>
#include <stdexcept>
#include <system_error>

/* C++ клас керування простором блокувань та RAII-блокуваннями */
class DlmLockspace {
public:
    explicit DlmLockspace(std::string_view name) {
        handle_ = dlm_open_lockspace(name.data());
        if (!handle_) {
            handle_ = dlm_create_lockspace(name.data(), 0660);
        }
        if (!handle_) {
            throw std::system_error(errno, std::generic_category(), "Failed to open or create DLM lockspace");
        }
    }

    ~DlmLockspace() {
        if (handle_) {
            dlm_release_lockspace(handle_);
        }
    }

    DlmLockspace(const DlmLockspace&) = delete;
    DlmLockspace& operator=(const DlmLockspace&) = delete;

    [[nodiscard]] dlm_lshandle_t native_handle() const noexcept { return handle_; }

private:
    dlm_lshandle_t handle_{nullptr};
};
```
:::

#### Прапорці виклику (Lock Flags)

* `DLM_LKF_NOQUEUE` (`0x00000001`) — не ставати в чергу очікування: якщо ресурс захоплено несумісним режимом, негайно повернути `-EAGAIN`;
* `DLM_LKF_CONVERT` (`0x00000004`) — конвертувати наявне блокування (ідентифіковане `lksb->sb_lkid`) у новий режим `mode`;
* `DLM_LKF_VALBLK` (`0x00000008`) — оновити або прочитати значення Lock Value Block (LVB) під час виконання операції;
* `DLM_LKF_QUECVT` (`0x00000010`) — якщо конверсія неможлива негайно, поставити запит у чергу конверсій замість відхилення;
* `DLM_LKF_EXPEDITE` (`0x00000020`) — надати найвищий пріоритет запиту в черзі сумісних блокувань;
* `DLM_LKF_PERSISTENT` (`0x00000040`) — зберегти блокування навіть після закриття процесу, що його відкрив.

#### Коди помилок системного виклику

* `-EAGAIN` — ресурс зайнятий несумісним режимом при використанні прапорця `DLM_LKF_NOQUEUE`;
* `-EDEADLK` — виявлено потенційне взаємне блокування (*deadlock*) між вузлами кластера;
* `-EINVAL` — некоректний дескриптор простору блокувань або неправильна комбінація прапорців;
* `-ENOMEM` — вичерпано пам'ять ядра для створення структури `struct dlm_rsb` (*Resource State Block*).

---

## 2. Діагностичний інтерфейс glocks у GFS2 (/sys/kernel/debug/gfs2)

GFS2 транслює кожен об'єкт файлової системи у відповідний ядерний об'єкт `struct gfs2_glock`. Їхній поточний стан експортується через віртуальний файл:

```text
/sys/kernel/debug/gfs2/<cluster_name>:<fs_name>/glocks
```

Цей інтерфейс відображає внутрішній стан кожного зареєстрованого в пам'яті glock, черги процесів, що очікують на блокування всередині поточного ядра, та статус взаємодії з DLM.

### Формат рядка діагностики glock

Кожен запис у файлі `glocks` починається префіксом `G:` і має таку структуру:

```text
G:  s:EX n:2/1a4f0 f:lIdt t:EX d:EX/0 l:0 a:0 r:3
```

Розшифровка полів запису:

| Поле | Приклад | Опис і значення |
| :--- | :--- | :--- |
| `s:<state>` | `s:EX` | Поточний активний стан glock на цьому вузлі (`UN` — Unlocked, `DF` — Deferred, `SH` — Shared, `EX` — Exclusive). |
| `n:<type>/<num>` | `n:2/1a4f0` | Тип ресурсу та його шістнадцятковий номер (номер inode, адреса Resource Group тощо). |
| `f:<flags>` | `f:lIdt` | Набір однолітерних прапорців стану glock у ядрі. |
| `t:<target>` | `t:EX` | Цільовий стан (*target state*), якого намагається досягти автомат станів glock. |
| `d:<demote>` | `d:EX/0` | Стан запиту на добровільне пониження режиму (*demote*) та лічильник спроб. |
| `l:<locks>` | `l:0` | Кількість локальних утримувачів блокування (*holders*) у процесах цього ядра. |
| `a:<flags>` | `a:0` | Асинхронні прапорці glock. |
| `r:<refcount>` | `r:3` | Лічильник посилань на структуру `struct gfs2_glock` у пам'яті ядра. |

Якщо під рядком `G:` присутні рядки з префіксом `H:` (*Holder*), вони позначають конкретні процеси ядра або простору користувача, які захопили це блокування:

```text
 H: s:EX f:e p:28192 [kworker/u16:2]
```
де `p:28192` — ідентифікатор потоку (PID), а `[kworker/...]` — назва задачі.

### Таблиця типів ресурсів n:<type>/...

| Числове значення | Назва типу | Префікс утиліт | Призначення ресурсу |
| :--- | :--- | :--- | :--- |
| `1` | `trans` | `t:` | Транзакційне блокування (заморожування файлової системи) |
| `2` | `inode` | `n:` | Метадані та кеш сторінок конкретного файлу або каталогу |
| `3` | `rgrp` | `r:` | Група ресурсів (*Resource Group*): бітові карти виділення блоків |
| `4` | `meta` | `m:` | Системні метадані файлової системи |
| `5` | `iopen` | `i:` | Спеціальне блокування відкритих файлів для координації `unlink` |
| `6` | `flock` | `f:` | Блокування діапазонів байтів файлів через `fcntl()` / `flock()` |
| `7` | `quota` | `q:` | Ліміти дискових квот користувачів і груп |
| `8` | `journal` | `j:` | Ексклюзивне блокування журналу транзакцій конкретного вузла |

### Таблиця прапорців стану f:<flags>

Прапорці стану відображають фазу автомата станів, у якій перебуває конкретний glock:

* `l` (`GLF_LOCK`) — об'єкт glock заблокований для зміни внутрішнього стану іншими потоками ядра;
* `d` (`GLF_DEMOTE`) — отримано BAST: потрібне пониження режиму для задоволення чужого запиту;
* `D` (`GLF_DEMOTE_IN_PROGRESS`) — триває процес скидання сторінок на диск та переходу в нижчий режим;
* `i` (`GLF_INVALIDATE_IN_PROGRESS`) — виконується очищення (`invalidate`) сторінок локального `page cache`;
* `p` (`GLF_DIRTY`) — кеш сторінок або метадані містять незбережені зміни, що вимагають запису на диск;
* `I` (`GLF_INITIAL`) — glock щойно створений у пам'яті і ще не синхронізований із DLM;
* `q` (`GLF_QUEUED`) — запит стоїть у черзі очікування повідомлень від DLM;
* `o` (`GLF_OBJECT`) — до glock прив'язано активний об'єкт VFS (структура `inode` або `rgroup`).

---

## 3. Інтерфейс dlmfs у OCFS2

Файлова система `dlmfs` монтується в простір користувача для прямого створення іменованих блокувань у кластері без необхідності писати низькорівневі C-програми з викликами сокетів:

```bash
mount -t dlmfs none /dlm
```

### Структура простору імен /dlm

Кожен каталог першого рівня всередині `/dlm` відповідає простору блокувань (*domain/lockspace*). Створення файлу всередині каталогу створює відповідний ресурс блокування:

```text
/dlm/
  └── my_cluster_domain/
        ├── lock_resource_1   (Файл блокування)
        └── database_mutex    (Файл блокування)
```

### Семантика системних викликів над файлами dlmfs

Робота з псевдофайлами у `/dlm` транслюється драйвером ядра безпосередньо в команди DLM:

* `open(path, O_RDWR)` — створення або підключення до ресурсу блокування;
* `read(fd, buf, count)` — зчитування поточного значення Lock Value Block (LVB);
* `write(fd, buf, count)` — оновлення значення Lock Value Block (LVB) (до 64 байтів);
* `flock(fd, LOCK_SH)` — захоплення спільного блокування (`DLM_LOCK_PR`);
* `flock(fd, LOCK_EX)` — захоплення монопольного блокування (`DLM_LOCK_EX`);
* `flock(fd, LOCK_UN)` — зняття блокування (`DLM_LOCK_NL`);
* `close(fd)` — автоматичне звільнення блокувань процесу при його завершенні або аварійному виході.

---

## 4. Точки трасування ядра (Tracepoints) для DLM та GFS2

Для детального аналізу затримок між'ядерної комунікації в підсистемі ftrace передбачено спеціалізовані статичні точки трасування:

```bash
# Увімкнення трасування переходів станів glock у GFS2
echo 1 > /sys/kernel/tracing/events/gfs2/gfs2_glock_state_change/enable

# Увімкнення трасування асинхронних пасток DLM
echo 1 > /sys/kernel/tracing/events/dlm/dlm_ast/enable
echo 1 > /sys/kernel/tracing/events/dlm/dlm_bast/enable

# Читання поточного логу подій
cat /sys/kernel/tracing/trace_pipe
```

Формат події `gfs2_glock_state_change` фіксує номер glock, попередній та новий стан, а також прапорці черг, що дозволяє виявити затримки примусового скидання кешу (*cache flush latency*).

---

## 5. Консольні утиліти моніторингу та керування

### Діагностика DLM (dlm_tool)

Утиліта `dlm_tool` дозволяє контролювати стан демона координації `dlm_controld` та черги повідомлень між вузлами:

```bash
# Перелік активних просторів блокувань та їхніх учасників
dlm_tool ls

# Повне вивантаження черг блокувань простору gfs2_fs
dlm_tool lockdump gfs2_fs

# Перевірка з'єднань між вузлами кластера та конфігурації
dlm_tool dump_config
```

### Керування GFS2 (gfs2_tool)

```bash
# Перевірка активних параметрів змонтованої ФС
gfs2_tool getargs /mnt/cluster_storage

# Примусове заморожування ФС для зняття консистентного snapshot на рівні SAN
gfs2_tool freeze /mnt/cluster_storage
gfs2_tool unfreeze /mnt/cluster_storage

# Додавання журналів для нових вузлів кластера
gfs2_jadd -j 2 /mnt/cluster_storage
```

### Діагностика OCFS2 (debugfs.ocfs2 та o2info)

```bash
# Інформація про розмітку екстентів та локальні алокатори
o2info --volinfo /dev/sdb1

# Інтерактивна консоль аналізу метаданих та стану блокувань OCFS2
debugfs.ocfs2 -n /dev/sdb1
```
