# ⚙️ Практичне використання PM QoS: керування затримкою та частотою

Ця вставка містить практичні приклади програмного коду для простору користувача (на мовах C та C++) та драйвера ядра Linux, які демонструють встановлення, маніпулювання та динамічну зміну обмежень затримки сну процесора й тактової частоти через підсистему PM QoS.

### 1. Постановка задачі та роль практичної інтеграції

У реальних високопродуктивних системах — таких як торговельні платформи високої частоти (HFT), аудіосервери низької затримки (JACK, PipeWire), бази даних у пам'яті (in-memory databases) або мережеві застосунки на основі DPDK — керування затримками пробудження процесора є критичним елементом проєктування. Навіть поодинокий перехід ядра CPU у глибокий стан сну C6 під час паузи між мережевими пакунками створює затримку обробки у 100–250 мікросекунд, що у сотні разів перевищує час виконання самого обчислювального алгоритму.

Підсистема PM QoS надає розробникам програмного забезпечення простору користувача та розробникам драйверів ядра чіткий інструментарій для гарантування продуктивності. Програма може висунути вимогу мінімальної затримки виключно на час виконання критичної секції, а після її завершення відновити стандартний режим енергозбереження ядра.

---

### 2. Управління затримкою процесора з простору користувача

Простір користувача взаємодіє з підсистемою CPU Latency QoS через спеціальний символьний пристрій `/dev/cpu_dma_latency` (misc-пристрій із динамічним мінорним номером). 

#### Механізм роботи файлового дескриптора
Коли процес відкриває файл `/dev/cpu_dma_latency` за допомогою системного виклику `open()`, підсистема PM QoS виділяє у внутрішній пам'яті ядра новий дескриптор запиту `struct pm_qos_request` і прив'язує його до відкритого файлового дескриптора процесу у таблиці `file->private_data`.

Запис 32-бітного цілого числа у відкритий дескриптор через виклик `write()` встановлює цільове значення затримки у мікросекундах:
* **Запис `0` мкс**: вимагає від ядра абсолютної мінімальної затримки. Це повністю забороняє перехід у будь-які стани сну C1..C10, залишаючи процесор у постійно активному стані C0 (виконання `pause` / `nop` або виконання активного опитування).
* **Запис позитивного числа `N` мкс**: дозволяє ядру використовувати лише ті стани сну `cpuidle`, затримка виходу з яких `exit_latency` не перевищує `N` мікросекунд.
* **Запис дуже великого значення (наприклад, `INT_MAX`)**: практично знімає вимогу цього процесу — жоден реальний стан сну такої межі не перевищує; остаточно ж запит зникає лише із закриттям дескриптора.

Найважливішою властивістю символьного пристрою `/dev/cpu_dma_latency` є **автоматична очистка при закритті**. Коли процес закриває файловий дескриптор через `close()`, або якщо процес завершується аварійно (наприклад, отримує сигнал `SIGKILL`), операційна система автоматично викликає функцію очищення `cpu_latency_qos_miscdev_release()`. Вона негайно видаляє відповідний запит з пріоритетного списку агрегації `plist`, запобігаючи вічним витокам обмежень затримки.

#### Двомовний приклад коду у просторі користувача

Нижче наведено робочий приклад програми у двох ідіоматичних варіантах — мовою C та C++. Варіант на C++ використовує семантику RAII (Resource Acquisition Is Initialization) для автоматичного очищення та скасування вимоги при виході з області видимості.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

#define PM_QOS_DEV "/dev/cpu_dma_latency"

// Відкриває пристрій PM QoS і записує бажане обмеження затримки у мікросекундах
int set_cpu_latency_target(int32_t latency_us) {
    int fd = open(PM_QOS_DEV, O_WRONLY);
    if (fd < 0) {
        perror("Помилка відкриття " PM_QOS_DEV " (перевірте права root)");
        return -1;
    }

    if (write(fd, &latency_us, sizeof(latency_us)) != sizeof(latency_us)) {
        perror("Помилка запису цільового значення у " PM_QOS_DEV);
        close(fd);
        return -1;
    }

    return fd;
}

int main(void) {
    int32_t target_latency = 0; // 0 мкс: повна заборона станів сну C1..C10

    printf("[C] Запитуємо обмеження затримки CPU у %d мкс...\n", target_latency);
    int qos_fd = set_cpu_latency_target(target_latency);
    if (qos_fd < 0) {
        return EXIT_FAILURE;
    }

    printf("[C] Обмеження PM QoS активовано. Виконуємо критичну секцію обчислень...\n");
    
    // Імітація інтенсивної обробки даних
    usleep(500000); // 500 мс

    printf("[C] Критичну секцію завершено. Закриваємо дескриптор для зняття обмеження.\n");
    close(qos_fd); // Ядро автоматично вилучає запит зі списку агрегації

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <system_error>
#include <string_view>
#include <cstdint>
#include <cstdlib>
#include <cerrno>
#include <unistd.h>
#include <fcntl.h>

namespace pm_qos {

// RAII обгортка для безпечного керування дескриптором CPU Latency QoS
class CpuLatencyLock {
public:
    explicit CpuLatencyLock(std::int32_t target_latency_us) {
        fd_ = ::open(device_path_.data(), O_WRONLY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(),
                                    "Failed to open " + std::string(device_path_));
        }

        if (::write(fd_, &target_latency_us, sizeof(target_latency_us)) != sizeof(target_latency_us)) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(),
                                    "Failed to write target latency to " + std::string(device_path_));
        }
    }

    ~CpuLatencyLock() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    // Заборона копіювання для запобігання подвійному закриттю дескриптора
    CpuLatencyLock(const CpuLatencyLock&) = delete;
    CpuLatencyLock& operator=(const CpuLatencyLock&) = delete;

    // Дозвіл переміщення ресурсу
    CpuLatencyLock(CpuLatencyLock&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    CpuLatencyLock& operator=(CpuLatencyLock&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

private:
    static constexpr std::string_view device_path_ = "/dev/cpu_dma_latency";
    int fd_{-1};
};

} // namespace pm_qos

int main() {
    try {
        std::cout << "[C++] Створюємо RAII-замок затримки (0 мкс)...\n";
        pm_qos::CpuLatencyLock latency_lock(0);

        std::cout << "[C++] PM QoS замок активний. Виконуємо обчислення без затримок пробудження...\n";
        ::usleep(500000); // 500 мс

        std::cout << "[C++] Завершено. Вихід із області видимості знищить замок RAII.\n";
    } catch (const std::exception& ex) {
        std::cerr << "[C++] Помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

### 3. Керування затримкою та частотою у драйвері ядра Linux

Усередині простору ядра драйвери периферійних пристроїв не використовують файлові дескриптори. Натомість вони оперують безпосередньо об'єктами `struct pm_qos_request` та `struct freq_qos_request`.

#### Використання CPU Latency QoS у драйвері
Під час реєстрації драйвера (наприклад, у виклику `probe()` або `module_init()`) виділяється структура `struct pm_qos_request`, після чого викликається `cpu_latency_qos_add_request()`. У момент появи високого навантаження (DMA-обмін, старт передачі кадрів) драйвер викликає `cpu_latency_qos_update_request()`, знижуючи допустиму затримку до `0` мкс. Після завершення обміну затримка повертається до стандартного значення, а при зупинці драйвера вимагається виклик `cpu_latency_qos_remove_request()`.

Нижче наведено приклад коду ядра Linux (мовою C):

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/pm_qos.h>
#include <linux/slab.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("PM QoS Example Author");
MODULE_DESCRIPTION("Приклад драйвера з підключенням CPU Latency QoS");

static struct pm_qos_request my_driver_qos_req;

static int __init my_driver_init(void) {
    pr_info("my_driver: Реєстрація вимоги CPU Latency QoS (20 мкс)\n");

    // Додаємо запит на максимальну затримку пробудження CPU у 20 мкс
    cpu_latency_qos_add_request(&my_driver_qos_req, 20);

    return 0;
}

// Викликається при старті інтенсивного DMA-обміну даними
void my_driver_start_heavy_io(void) {
    pr_info("my_driver: Знижуємо межу затримки до 0 мкс (заборона сну)\n");
    // Робимо вимогу найжорсткішою: допустима затримка пробудження — нуль
    cpu_latency_qos_update_request(&my_driver_qos_req, 0);
}

// Викликається після завершення інтенсивного DMA-обміну даними
void my_driver_stop_heavy_io(void) {
    pr_info("my_driver: Повернення затримки до 20 мкс\n");
    // Повертаємо початкову вимогу
    cpu_latency_qos_update_request(&my_driver_qos_req, 20);
}

static void __exit my_driver_exit(void) {
    pr_info("my_driver: Видалення вимоги CPU Latency QoS\n");

    // Видаляємо запит з глобального списку агрегації
    cpu_latency_qos_remove_request(&my_driver_qos_req);
}

module_init(my_driver_init);
module_exit(my_driver_exit);
```

#### Використання Frequency QoS у драйвері
Якщо драйверу необхідно форсувати підвищення мінімальної частоти процесора (наприклад, для прискорення обробки пакетного сплеску), він використовує фреймворк `Frequency QoS`:

```c
#include <linux/cpufreq.h>
#include <linux/pm_qos.h>

static struct freq_qos_request my_freq_req;

void my_driver_boost_frequency(struct cpufreq_policy *policy, u32 min_freq_khz) {
    // Додаємо вимогу мінімальної частоти у кГц для політики cpufreq
    freq_qos_add_request(&policy->constraints, &my_freq_req, FREQ_QOS_MIN, min_freq_khz);
}

void my_driver_unboost_frequency(void) {
    // Видаляємо вимогу мінімальної частоти
    freq_qos_remove_request(&my_freq_req);
}
```

---

### 4. Діагностика та трасування трасувальниками ядра (`ftrace`)

З ядра Linux 5.7 застарілий інтерфейс `debugfs` для перегляду списку PM QoS було повністю видалено. Сучасне спостереження за діяльністю підсистеми здійснюється через трасувальник **ftrace** та точки трасування `events/power/`.

#### Активація трасування PM QoS
Щоб увімкнути та переглянути події додавання, зміни й видалення вимог PM QoS у реальному часі, виконуються такі команди від імені користувача root:

```bash
# 1. Перехід у каталог трасувальника ftrace
cd /sys/kernel/tracing

# 2. Активація подій трасування підсистеми PM QoS
echo 1 > events/power/pm_qos_add_request/enable
echo 1 > events/power/pm_qos_update_request/enable
echo 1 > events/power/pm_qos_remove_request/enable

# 3. Перегляд потокового виводу подій трасування
cat trace_pipe
```

Приклад виводу трасування у консолі під час роботи програми простору користувача:

```text
  app_process-4102  [002] .... 14201.512034: pm_qos_add_request: value=0
  app_process-4102  [002] .... 14202.012411: pm_qos_update_request: value=50
```

#### Моніторинг статистики станів сну `cpuidle`
Щоб переконатися у практичній ефективності встановленого обмеження затримки, можна порівняти лічильники перебування у станах сну у файловій системі sysfs до та після висунення вимоги PM QoS:

```bash
# Перегляд статистики перебування CPU0 у глибокому стані сну
# (який саме стан ховається за state3 на цій машині — покаже сусідній файл name)
cat /sys/devices/system/cpu/cpu0/cpuidle/state3/name
cat /sys/devices/system/cpu/cpu0/cpuidle/state3/time
cat /sys/devices/system/cpu/cpu0/cpuidle/state3/usage
```

Якщо вимога затримки встановлена у `0` мкс, лічильники `usage` та `time` для глибоких станів сну повністю припиняють зростати, підтверджуючи, що регулятор `cpuidle` відсікає ці стани від виконання.

---

### 5. Типові помилки та підводні камені використання

Під час роботи з підсистемою PM QoS розробники найчастіше припускаються таких помилок:

1. **Часте оновлення у гарячих шляхах (Hot Paths):**
   Викликати `cpu_latency_qos_update_request()` на кожному отриманому мережевому пакунку чи перериванні заборонено. Оновлення вимоги захоплює спін-лок і викликає ланцюжок сповіщувачів, що на кожному виклику додає кілька мікросекунд, і ця плата накопичується просто в гарячому шляху. Вимогу висувають один раз на сесію, а не на пакунок.

2. **Забуті відкриті дескриптори `/dev/cpu_dma_latency`:**
   Якщо фонова служба відкриває символьний пристрій і забуває закрити його після завершення обчислень, ядро продовжує утримувати обмеження `0` мкс. Це призводить до підвищеного енергоспоживання процесора та випалювання акумулятора мобільного пристрою.

3. **Виклики модифікуючих функцій з атомарного контексту:**
   Спроба викликати `cpu_latency_qos_add_request()` чи `cpu_latency_qos_update_request()` з обробника переривань (ISR) призводить до краху ядра (kernel panic чи BUG: scheduling while atomic), оскільки ланцюжок сповіщень `blocking_notifier_call_chain` вимагає контексту з можливістю сну.
