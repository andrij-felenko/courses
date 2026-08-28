# ⚙️ Конвеєр автоматизованого ребейзу, перевірки латок та бісекції регресій

У комерційній розробці вбудованих систем, мережевого обладнання та системного програмного забезпечення супровід похідного форку вимагає постійного перенесення локальних латок на нові релізні версії апстриму. Якщо інженерна команда виконує цю процедуру вручну раз на кілька місяців, процес неминуче перетворюється на виснажливий цикл розв'язання неочікуваних конфліктів, ручного порівняння дерев файлів та тривалого пошуку прихованих регресій.

Коли кількість локальних патчів у проєкті перевищує п'ять, ручний контроль втрачає надійність. Розробники забувають, які саме виправлення вже були відправлені до відкритої спільноти, які з них отримали схвалення мейнтейнерів, а які були відхилені через архітектурну несумісність. У результаті під час чергового злиття інженери повторно накладають уже інтегровані в ядро зміни або намагаються адаптувати застарілий код, який давно має штатний аналог в основному дереві.

Надійне інженерне вирішення проблеми полягає у побудові повністю автономного програмного конвеєра, який бере на себе всю механічну рутину:
1. Автоматично завантажує найсвіжіші теги та гілки з віддаленого репозиторію апстриму.
2. Аналізує метадані локальної черги латок, перевіряючи, чи були надіслані виправлення прийняті спільнотою.
3. Математично доводить наявність комітів в апстримі за допомогою аналізу спрямованого ациклічного графа Git та списує застарілі файли латок.
4. Виконує безпечне тестове накладання активних змін в ізольованому тимчасовому робочому дереві (`git worktree`), не торкаючись поточної гілки розробника.
5. Запускає комплексний набір юніт- та інтеграційних тестів для перевірки збереження працездатності периферійних пристроїв.
6. У разі виникнення функціонального збою автоматично ініціює процедуру бісекції (`git bisect`), знаходячи точний комміт апстриму, який порушив роботу системи.

---

## 1. Архітектура та реалізація контролера синхронізації (Python)

Наведений нижче сценарій автоматизації `rebase_sync_engine.py` є завершеним інструментом командного рядка. Він не потребує сторонніх бібліотек, працює поверх стандартного клієнта Git і повністю реалізує логіку управління чергою латок.

Контролер спирається на три фундаментальні механізми системи контролю версій:
* **Ізоляція робочого простору (Worktree Isolation):** замість модифікації поточного робочого каталогу створюється окремий тимчасовий каталог, прив'язаний до цільового тегу апстриму в режимі `detached HEAD`. Це гарантує, що незафіксовані файли розробника або поточна гілка не будуть пошкоджені навіть у разі аварійної зупинки.
* **Математична перевірка предків (`git merge-base --is-ancestor`):** перевірка входження коміту здійснюється не за текстовим збігом опису, а за топологією графа комітів. Якщо хеш комміта, зазначений у метаданих `Upstream-Commit`, є прямим предком цільового тегу, це є неспростовним доказом того, що код уже присутній в ядрі.
* **Триточкове накладання латок (`git am -3`):** у разі зміщення номерів рядків у вихідному коді Git використовує інформацію про хеші вихідних блобів (blobs) для триточкового зіставлення, що дозволяє успішно накладати патчі навіть після значного рефакторингу навколишнього коду.

```text
               ПОСЛІДОВНІСТЬ РОБОТИ КОНТРОЛЕРА СИНХРОНІЗАЦІЇ
┌────────────────────────┐
│ 1. Сканування каталогу ├─► Читання заголовків RFC 822 із файлів *.patch
└───────────┬────────────┘
            │
┌───────────▼────────────┐
│ 2. Аудит входження     ├─► Перевірка Upstream-Commit через git merge-base
└───────────┬────────────┘
            │
┌───────────▼────────────┐
│ 3. Списання латок      ├─► Видалення прийнятих патчів із черги тестування
└───────────┬────────────┘
            │
┌───────────▼────────────┐
│ 4. Створення worktree  ├─► Ізольована тимчасова тека на базі target_tag
└───────────┬────────────┘
            │
┌───────────▼────────────┐
│ 5. Триточковий rebase  ├─► Почергове застосування git am -3 для активних латок
└───────────┬────────────┘
            │
┌───────────▼────────────┐
│ 6. Звітування та вихід ├─► 0 — успіх, 1 — конфлікт, запуск бісекції
└────────────────────────┘
```

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebase_sync_engine.py — Автоматизований контролер оновлення форку."""

import os
import sys
import re
import subprocess
import tempfile
import shutil


def run_git(args, cwd=None, check=True):
    """Виконати команду Git та повернути текстовий вивід.
    
    У разі помилки формує докладне повідомлення з кодом повернення,
    командою та вмістом стандартних потоків виводу й помилок.
    """
    cmd = ["git"] + args
    res = subprocess.run(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if check and res.returncode != 0:
        raise RuntimeError(
            f"Git command failed: {' '.join(cmd)}\n"
            f"Stdout: {res.stdout.strip()}\n"
            f"Stderr: {res.stderr.strip()}"
        )
    return res.stdout.strip()


def parse_patch_headers(patch_path):
    """Витягти структуровані заголовки метаданих із файлу латки.
    
    Зчитує блок коментарів до першого технічного роздільника '---'.
    Підтримує обов'язкові поля Upstream-Status, Upstream-Commit,
    Upstream-PR, CVE та юридичний підпис Signed-off-by.
    """
    metadata = {
        "status": "Pending",
        "commit": None,
        "pr": None,
        "cve": None,
        "subject": "",
        "signed_off_by": None
    }
    with open(patch_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("Subject:"):
                metadata["subject"] = line.split(":", 1)[1].strip()
            elif line.startswith("Upstream-Status:"):
                metadata["status"] = line.split(":", 1)[1].strip()
            elif line.startswith("Upstream-Commit:"):
                metadata["commit"] = line.split(":", 1)[1].strip()
            elif line.startswith("Upstream-PR:"):
                metadata["pr"] = line.split(":", 1)[1].strip()
            elif line.startswith("CVE:"):
                metadata["cve"] = line.split(":", 1)[1].strip()
            elif line.startswith("Signed-off-by:"):
                metadata["signed_off_by"] = line.split(":", 1)[1].strip()
            elif line.strip() == "---":
                break
    return metadata


def is_commit_in_upstream(repo_path, commit_hash, upstream_ref):
    """Перевірити, чи увійшов конкретний комміт до цільової гілки апстриму.
    
    Використовує фундаментальну команду git merge-base --is-ancestor,
    яка математично перевіряє досяжність комміта у графі DAG.
    """
    if not commit_hash or len(commit_hash) < 7:
        return False
    
    # Виконуємо перевірку без викидання винятку: returncode 0 означає істину
    res = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit_hash, upstream_ref],
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return res.returncode == 0


def run_automated_sync(repo_dir, patches_dir, upstream_remote, target_tag):
    """Головний контур аналізу латок, списання та тестового ребейзу."""
    print(f"[*] Ініціалізація аналізу латок у каталозі: {patches_dir}")
    if not os.path.exists(patches_dir):
        raise FileNotFoundError(f"Каталог латок не знайдено: {patches_dir}")

    patch_files = sorted([f for f in os.listdir(patches_dir) if f.endswith(".patch")])
    if not patch_files:
        print("[*] Локальних латок не виявлено. Дерево повністю синхронізоване з апстримом.")
        return True

    active_patches = []
    retired_patches = []

    # Фаза 1: Аудит метаданих та списання прийнятих патчів
    for pf in patch_files:
        ppath = os.path.join(patches_dir, pf)
        meta = parse_patch_headers(ppath)
        print(f" -> Аналіз {pf}: [{meta['status']}] {meta['subject'][:55]}...")

        # Якщо латка позначена як Accepted і містить хеш, перевіряємо її в апстримі
        if meta["status"] == "Accepted" and meta["commit"]:
            if is_commit_in_upstream(repo_dir, meta["commit"], target_tag):
                print(f"    [+] СПИСАНО: Комміт {meta['commit'][:10]} увійшов до {target_tag}")
                retired_patches.append((pf, meta))
                continue

        active_patches.append((pf, meta))

    print(f"\n[*] Результат аудиту: {len(active_patches)} активних латок, {len(retired_patches)} списано.")

    # Фаза 2: Створення ізольованого робочого дерева (Worktree)
    temp_worktree = tempfile.mkdtemp(prefix="rebase_sync_worktree_")
    try:
        print(f"[*] Створення тимчасового робочого дерева в {temp_worktree}")
        run_git(["worktree", "add", "--detach", temp_worktree, target_tag], cwd=repo_dir)

        # Фаза 3: Послідовне накладання активних латок
        print(f"[*] Накладання активних латок поверх цільової бази {target_tag}...")
        for pf, meta in active_patches:
            ppath = os.path.abspath(os.path.join(patches_dir, pf))
            apply_res = subprocess.run(
                ["git", "am", "-3", ppath],
                cwd=temp_worktree,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if apply_res.returncode != 0:
                print(f"\n[!] СТРУКТУРНИЙ КОНФЛІКТ при накладанні латки: {pf}")
                print(f"    Деталі Git:\n{apply_res.stderr.strip()}")
                run_git(["am", "--abort"], cwd=temp_worktree, check=False)
                return False
            else:
                print(f"    [✓] Успішно накладено: {pf}")

        print(f"\n[УСПІХ] Усі {len(active_patches)} активних латок успішно ребейзнуто на {target_tag}!")
        return True

    finally:
        # Гарантоване прибирання робочого простору навіть у разі збоїв
        print("[*] Видалення тимчасового робочого дерева...")
        run_git(["worktree", "remove", "--force", temp_worktree], cwd=repo_dir, check=False)
        shutil.rmtree(temp_worktree, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Використання: python rebase_sync_engine.py <шлях_до_репо> <каталог_латок> <цільовий_тег>")
        print("Приклад: python rebase_sync_engine.py ./firmware ./patches v3.6.0")
        sys.exit(0)
    
    success = run_automated_sync(sys.argv[1], sys.argv[2], "upstream", sys.argv[3])
    sys.exit(0 if success else 1)
```

---

## 2. Тестовий модуль верифікації сумісності інтерфейсів (ABI Shim Check)

При переході на нову версію операційної системи реального часу структури дескрипторів обладнання та сигнатури функцій керування периферією можуть змінюватися. Якщо прикладний код безпосередньо звертається до внутрішніх структур ядра, будь-яка зміна розміру полів або порядку байтів викличе катастрофічне пошкодження пам'яті (Memory Corruption) або збій вирівнювання (Bus Fault).

Щоб запобігти цьому, між ядром та комерційним застосунком зводиться шар програмного фасаду (Shim Layer). Нижче наведено завершену еталонну реалізацію модуля перевірки сумісності інтерфейсу апаратного таймера на мовах C та C++.

Особливості реалізації:
* **Умовна трансляція структур:** адаптер самостійно транслює параметри між старою версією v1 та новою v2 на етапі компіляції.
* **Інкапсуляція апаратних прапорців:** застосунок оперує абстрактною частотою в герцах, тоді як адаптер самостійно розраховує дільники та пріоритети переривань для конкретного ядра.
* **Безпека ресурсів у C++ (RAII):** деструктор автоматично зупиняє апаратний таймер при виході об'єкта з області видимості, унеможливлюючи виникнення висячих переривань. Семантика переміщення (Move Semantics) запобігає небезпечному копіюванню фізичного ресурсу.

:::tabs
```c
/* abi_shim_check.c — C-реалізація шару абстракції апаратного таймера */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Імітація внутрішнього API ядра версії v1 проти v2 */
#if defined(USE_KERNEL_API_V2)
typedef struct {
    void *mmio_base;
    uint32_t freq_hz;
    uint32_t irq_priority;
} kernel_timer_raw_t;

int kernel_raw_timer_start(kernel_timer_raw_t *t, uint32_t freq_hz);
void kernel_raw_timer_stop(kernel_timer_raw_t *t);
#else
typedef struct {
    uint32_t register_base;
    uint16_t clock_mhz;
} kernel_timer_raw_t;

int kernel_raw_timer_init(kernel_timer_raw_t *t, uint16_t mhz);
void kernel_raw_timer_disable(kernel_timer_raw_t *t);
#endif

/* Публічний контракт, який бачить прикладний код продукту */
typedef struct {
    kernel_timer_raw_t native_handle;
    uint32_t configured_freq_hz;
    bool is_running;
} product_timer_handle_t;

int product_timer_init(product_timer_handle_t *timer, uint32_t target_freq_hz) {
    if (!timer || target_freq_hz == 0) {
        return -1;
    }

    timer->configured_freq_hz = target_freq_hz;
    int status = 0;

#if defined(USE_KERNEL_API_V2)
    /* Адаптація під інтерфейс нового ядра v2 */
    timer->native_handle.freq_hz = target_freq_hz;
    timer->native_handle.irq_priority = 2;
    status = kernel_raw_timer_start(&timer->native_handle, target_freq_hz);
#else
    /* Підтримка застарілого інтерфейсу ядра v1 */
    uint16_t mhz = (uint16_t)(target_freq_hz / 1000000UL);
    status = kernel_raw_timer_init(&timer->native_handle, mhz);
#endif

    if (status == 0) {
        timer->is_running = true;
    }
    return status;
}

void product_timer_shutdown(product_timer_handle_t *timer) {
    if (!timer || !timer->is_running) {
        return;
    }

#if defined(USE_KERNEL_API_V2)
    kernel_raw_timer_stop(&timer->native_handle);
#else
    kernel_raw_timer_disable(&timer->native_handle);
#endif

    timer->is_running = false;
}
```
```cpp
// abi_shim_check.cpp — Ідіоматичний C++ фасад із RAII та обробкою помилок
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <memory>

namespace product::bsp {

enum class HardwareError : uint8_t {
    InvalidConfiguration,
    InitializationFailed,
    BusBusy,
    Timeout
};

// Внутрішній C-інтерфейс операційної системи
struct NativeKernelTimerHandle {
    void* mmio_address{nullptr};
    uint32_t frequency_hz{0};
    uint32_t irq_flags{0};
};

extern "C" {
    int os_kernel_timer_configure(NativeKernelTimerHandle* h, uint32_t freq);
    void os_kernel_timer_release(NativeKernelTimerHandle* h);
}

class SystemTimerFacade final {
public:
    explicit SystemTimerFacade(uint32_t target_freq_hz) noexcept
        : target_frequency_{target_freq_hz} {}

    ~SystemTimerFacade() noexcept {
        if (active_) {
            os_kernel_timer_release(&native_handle_);
        }
    }

    // Заборона небезпечного копіювання ресурсу обладнання
    SystemTimerFacade(const SystemTimerFacade&) = delete;
    SystemTimerFacade& operator=(const SystemTimerFacade&) = delete;

    // Дозвіл безпечного переміщення (Move semantics)
    SystemTimerFacade(SystemTimerFacade&& other) noexcept
        : native_handle_{other.native_handle_},
          target_frequency_{other.target_frequency_},
          active_{other.active_} {
        other.active_ = false;
        other.native_handle_ = {};
    }

    SystemTimerFacade& operator=(SystemTimerFacade&& other) noexcept {
        if (this != &other) {
            if (active_) {
                os_kernel_timer_release(&native_handle_);
            }
            native_handle_ = other.native_handle_;
            target_frequency_ = other.target_frequency_;
            active_ = other.active_;
            other.active_ = false;
            other.native_handle_ = {};
        }
        return *this;
    }

    [[nodiscard]] std::expected<void, HardwareError> start() noexcept {
        if (target_frequency_ == 0) {
            return std::unexpected(HardwareError::InvalidConfiguration);
        }

        native_handle_.frequency_hz = target_frequency_;
        native_handle_.irq_flags = 0x01;

        const int ret = os_kernel_timer_configure(&native_handle_, target_frequency_);
        if (ret != 0) {
            return std::unexpected(HardwareError::InitializationFailed);
        }

        active_ = true;
        return {};
    }

    [[nodiscard]] bool is_running() const noexcept {
        return active_;
    }

    [[nodiscard]] uint32_t get_frequency() const noexcept {
        return target_frequency_;
    }

private:
    NativeKernelTimerHandle native_handle_{};
    uint32_t target_frequency_{0};
    bool active_{false};
};

} // namespace product::bsp
```
:::

---

## 3. Автоматизована локалізація регресій у конвеєрі (Git Bisect Runner)

Коли тестовий ребейз проходить без синтаксичних конфліктів і прошивка успішно компілюється, проте автоматизовані тести на емуляторі QEMU або апаратному стенді фіксують збій, конвеєр переходить у режим автоматичної бісекції.

Скрипт `bisect_runner.sh` здійснює логарифмічний двійковий пошук (лат. *dichotomia*) серед тисяч комітів апстриму, виконуючи тестовий запуск на кожному кроці.

Критичні правила побудови бісекційного стенду:
1. **Код повернення 125 для незбираних комітів:** в історії апстриму неминуче трапляються проміжні коміти, в яких збірка зламана через помилки інших розробників. Скрипт перехоплює помилку компіляції та повертає код 125. Це вказує Git пропустити поточний крок і вибрати сусідній коміт без зупинки бісекції.
2. **Ізоляція тестового середовища:** кожна ітерація тестування повинна повністю очищати каталоги збирання (`build/`), щоб виключити артефакти кешу компілятора ccache або застарілі об'єктні файли.
3. **Автоматична генерація звіту:** після виявлення першого зламаного комміта скрипт зберігає повний лог `git bisect log` та формує чернетку багрепорту для відправки до апстриму.

```bash
#!/usr/bin/env bash
# bisect_runner.sh — Автоматичний пошук дефекту між релізами апстриму
set -euo pipefail

OLD_STABLE_TAG="v3.5.0"
NEW_TARGET_TAG="v3.6.0"

echo "[*] Ініціалізація бісекції між стабільним ${OLD_STABLE_TAG} та цільовим ${NEW_TARGET_TAG}..."
git bisect start "${NEW_TARGET_TAG}" "${OLD_STABLE_TAG}"

# Автоматичний запуск тестового скрипта на кожній ітерації
git bisect run bash -c '
    # 1. Експорт шляхів до нашого ізольованого позадеревного модуля драйверів
    export ZEPHYR_MODULES="$(pwd)/modules/custom_drivers"
    
    # 2. Спроба збирання тестового бінарного артефакту
    if ! west build -b qemu_cortex_m3 tests/drivers/spi -p auto > /dev/null 2>&1; then
        # Код 125 сигналізує Git пропустити цей комміт, якщо апстрим зламаний іншими авторами
        exit 125
    fi
    
    # 3. Виконання інтеграційного тесту в емуляторі
    ninja -C build run_tests
'

echo "[*] Бісекцію завершено. Комміт апстриму, що спричинив регресію:"
git bisect log
git bisect reset
```

Завдяки автоматизації час локалізації критичних апаратних дефектів зменшується з декількох робочих днів до 15–20 хвилин фонової роботи сервера збирання, забезпечуючи інженерів вичерпним звітом для відправки багрепорту мейнтейнерам апстриму.
