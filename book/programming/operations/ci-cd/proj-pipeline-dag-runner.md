# ⚙️ Конвеєрний рушій виконання DAG задач із паралельним плануванням

Сучасні системи неперервної інтеграції виконують пайплайни не як лінійний список послідовних кроків, а як спрямований ациклічний граф (англ. *Directed Acyclic Graph*, DAG). Це дозволяє запускати незалежні задачі (наприклад, збірку фронтенду, юніт-тести бекенду та статичний аналіз) паралельно на пулі воркерів, скорочуючи загальний час виконання пайплайну до довжини критичного шляху.

Нижче наведено повнофункціональну реалізацію багатопотокового DAG-планувальника задач. Рушій будує граф залежностей, обчислює вхідні півстепені вершин (`in-degree`), динамічно переміщує розблоковані задачі до черги виконання, розподіляє їх між потоками пулу та каскадно маркує залежні задачі як `SKIPPED` у разі аварійного завершення попередника.

## Архітектура та математична модель DAG-планувальника

Граф задач конвеєра формально визначається як пара G = (V, E), де:
* Множина вершин V = {j_1, j_2, ..., j_n} представляє окремі ізольовані задачі (наприклад, компіляцію, лінтування, тестування, пакування).
* Множина спрямованих ребер E ⊆ V × V визначає відношення передування. Ребро (u, v) ∈ E означає, що задача v не може розпочати виконання доти, доки задача u не завершиться зі статусом `SUCCESS`.

### Обчислення вхідного півстепеня (In-Degree) та алгоритм Кана
Для кожної вершини v ∈ V визначається вхідний півстепінь deg^-(v) = |{u ∈ V : (u, v) ∈ E}|, що дорівнює кількості незавершених батьківських задач, від яких залежить v.

Динамічний цикл планування працює за модифікованим алгоритмом Кана (Kahn's Algorithm) для паралельного багатопотокового середовища:
1. **Ініціалізація**: для всіх вершин v ∈ V підраховується початковий півстепінь deg^-(v). Усі вершини з deg^-(v) = 0 (кореневі задачі без залежностей) переміщуються до потокобезпечної черги готових задач (`ready_queue`).
2. **Паралельне виконання**: вільні робочі потоки (воркери) вилучають задачі з `ready_queue` та виконують їх паралельно.
3. **Розблокування нащадків**: після успішного завершення задачі u воркер зменшує лічильник deg^-(v) для кожного прямого нащадка v ∈ children(u) під захистом м'ютекса. Якщо лічильник нащадка досягає нуля (deg^-(v) = 0), задача v стає готовою і надсилається до `ready_queue`, пробуджуючи наступний вільний потік через умовну змінну (`condition_variable`).
4. **Каскадне відсікання помилок (Cascade Skip)**: якщо задача u завершується аварійно зі статусом `FAILED`, планувальник рекурсивно обходить підграф нащадків Descendants(u) та маркує їх статусом `SKIPPED`, запобігаючи марній витраті процесорного часу на завідомо приречені етапи.

---

## Повнофункціональна реалізація багатопотокового рушія

:::tabs
== C
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

#define MAX_JOBS 32
#define MAX_NAME_LEN 64
#define MAX_DEPS 8
#define NUM_WORKERS 4

typedef enum {
    STATUS_PENDING,
    STATUS_READY,
    STATUS_RUNNING,
    STATUS_SUCCESS,
    STATUS_FAILED,
    STATUS_SKIPPED
} job_status_t;

typedef struct {
    char name[MAX_NAME_LEN];
    int duration_ms;
    bool should_fail;
    job_status_t status;
    int in_degree;
    int dep_count;
    int dep_indices[MAX_DEPS];
} job_t;

typedef struct {
    job_t jobs[MAX_JOBS];
    int job_count;
    int ready_queue[MAX_JOBS];
    int ready_head;
    int ready_tail;
    int ready_count;
    int completed_count;
    pthread_mutex_t lock;
    pthread_cond_t cv_ready;
    pthread_cond_t cv_done;
    bool shutdown;
} dag_runner_t;

void runner_init(dag_runner_t *runner) {
    memset(runner, 0, sizeof(*runner));
    pthread_mutex_init(&runner->lock, NULL);
    pthread_cond_init(&runner->cv_ready, NULL);
    pthread_cond_init(&runner->cv_done, NULL);
}

int runner_add_job(dag_runner_t *runner, const char *name, int duration_ms, bool should_fail) {
    if (runner->job_count >= MAX_JOBS) return -1;
    int idx = runner->job_count++;
    strncpy(runner->jobs[idx].name, name, MAX_NAME_LEN - 1);
    runner->jobs[idx].duration_ms = duration_ms;
    runner->jobs[idx].should_fail = should_fail;
    runner->jobs[idx].status = STATUS_PENDING;
    runner->jobs[idx].in_degree = 0;
    runner->jobs[idx].dep_count = 0;
    return idx;
}

void runner_add_dependency(dag_runner_t *runner, int parent_idx, int child_idx) {
    if (parent_idx < 0 || parent_idx >= runner->job_count ||
        child_idx < 0 || child_idx >= runner->job_count) return;
    job_t *child = &runner->jobs[child_idx];
    if (child->dep_count < MAX_DEPS) {
        child->dep_indices[child->dep_count++] = parent_idx;
        child->in_degree++;
    }
}

static void runner_enqueue_ready(dag_runner_t *runner, int job_idx) {
    runner->ready_queue[runner->ready_tail] = job_idx;
    runner->ready_tail = (runner->ready_tail + 1) % MAX_JOBS;
    runner->ready_count++;
    runner->jobs[job_idx].status = STATUS_READY;
    pthread_cond_signal(&runner->cv_ready);
}

static int runner_dequeue_ready(dag_runner_t *runner) {
    if (runner->ready_count == 0) return -1;
    int job_idx = runner->ready_queue[runner->ready_head];
    runner->ready_head = (runner->ready_head + 1) % MAX_JOBS;
    runner->ready_count--;
    return job_idx;
}

static void cascade_skip(dag_runner_t *runner, int failed_idx) {
    for (int i = 0; i < runner->job_count; ++i) {
        job_t *job = &runner->jobs[i];
        if (job->status == STATUS_PENDING || job->status == STATUS_READY) {
            for (int d = 0; d < job->dep_count; ++d) {
                if (job->dep_indices[d] == failed_idx) {
                    job->status = STATUS_SKIPPED;
                    runner->completed_count++;
                    printf("[RUNNER] Job '%s' SKIPPED (upstream '%s' failed)\n",
                           job->name, runner->jobs[failed_idx].name);
                    cascade_skip(runner, i);
                    break;
                }
            }
        }
    }
}

void* worker_thread(void *arg) {
    dag_runner_t *runner = (dag_runner_t*)arg;

    while (1) {
        pthread_mutex_lock(&runner->lock);

        while (runner->ready_count == 0 && !runner->shutdown &&
               runner->completed_count < runner->job_count) {
            pthread_cond_wait(&runner->cv_ready, &runner->lock);
        }

        if (runner->shutdown || runner->completed_count >= runner->job_count) {
            pthread_mutex_unlock(&runner->lock);
            break;
        }

        int job_idx = runner_dequeue_ready(runner);
        if (job_idx < 0) {
            pthread_mutex_unlock(&runner->lock);
            continue;
        }

        job_t *job = &runner->jobs[job_idx];
        job->status = STATUS_RUNNING;
        printf("[RUNNER] Starting job '%s' (duration: %d ms)...\n", job->name, job->duration_ms);
        pthread_mutex_unlock(&runner->lock);

        /* Імітація виконання корисної роботи */
        usleep(job->duration_ms * 1000);
        bool success = !job->should_fail;

        pthread_mutex_lock(&runner->lock);
        runner->completed_count++;

        if (success) {
            job->status = STATUS_SUCCESS;
            printf("[RUNNER] Job '%s' COMPLETED SUCCESS\n", job->name);

            /* Розблокування нащадків */
            for (int i = 0; i < runner->job_count; ++i) {
                job_t *child = &runner->jobs[i];
                if (child->status == STATUS_PENDING) {
                    for (int d = 0; d < child->dep_count; ++d) {
                        if (child->dep_indices[d] == job_idx) {
                            child->in_degree--;
                            if (child->in_degree == 0) {
                                runner_enqueue_ready(runner, i);
                            }
                            break;
                        }
                    }
                }
            }
        } else {
            job->status = STATUS_FAILED;
            printf("[RUNNER] Job '%s' FAILED!\n", job->name);
            cascade_skip(runner, job_idx);
        }

        if (runner->completed_count >= runner->job_count) {
            pthread_cond_broadcast(&runner->cv_ready);
            pthread_cond_signal(&runner->cv_done);
        }

        pthread_mutex_unlock(&runner->lock);
    }
    return NULL;
}

void runner_run(dag_runner_t *runner) {
    pthread_t threads[NUM_WORKERS];

    pthread_mutex_lock(&runner->lock);
    /* Знаходимо початкові задачі з нульовим in-degree */
    for (int i = 0; i < runner->job_count; ++i) {
        if (runner->jobs[i].in_degree == 0) {
            runner_enqueue_ready(runner, i);
        }
    }
    pthread_mutex_unlock(&runner->lock);

    for (int i = 0; i < NUM_WORKERS; ++i) {
        pthread_create(&threads[i], NULL, worker_thread, runner);
    }

    pthread_mutex_lock(&runner->lock);
    while (runner->completed_count < runner->job_count) {
        pthread_cond_wait(&runner->cv_done, &runner->lock);
    }
    runner->shutdown = true;
    pthread_cond_broadcast(&runner->cv_ready);
    pthread_mutex_unlock(&runner->lock);

    for (int i = 0; i < NUM_WORKERS; ++i) {
        pthread_join(threads[i], NULL);
    }

    pthread_mutex_destroy(&runner->lock);
    pthread_cond_destroy(&runner->cv_ready);
    pthread_cond_destroy(&runner->cv_done);
}

int main(void) {
    dag_runner_t runner;
    runner_init(&runner);

    int j_lint    = runner_add_job(&runner, "lint-and-format", 50, false);
    int j_build   = runner_add_job(&runner, "compile-binary", 100, false);
    int j_unit    = runner_add_job(&runner, "unit-tests", 80, false);
    int j_sec     = runner_add_job(&runner, "security-sast", 60, false);
    int j_e2e     = runner_add_job(&runner, "e2e-integration", 120, false);
    int j_package = runner_add_job(&runner, "build-oci-image", 90, false);

    /* Граф залежностей:
     * lint & build -> unit-tests & security-sast -> e2e-integration -> build-oci-image */
    runner_add_dependency(&runner, j_lint, j_unit);
    runner_add_dependency(&runner, j_build, j_unit);
    runner_add_dependency(&runner, j_build, j_sec);
    runner_add_dependency(&runner, j_unit, j_e2e);
    runner_add_dependency(&runner, j_sec, j_e2e);
    runner_add_dependency(&runner, j_e2e, j_package);

    printf("=== Starting DAG Pipeline Runner ===\n");
    runner_run(&runner);
    printf("=== Pipeline Completed ===\n");
    return 0;
}
```
== C++
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <memory>
#include <span>

enum class JobStatus {
    Pending,
    Ready,
    Running,
    Success,
    Failed,
    Skipped
};

struct Job {
    std::string name;
    std::chrono::milliseconds duration;
    bool should_fail{false};
    JobStatus status{JobStatus::Pending};
    int in_degree{0};
    std::vector<std::string> dependencies;
    std::vector<std::string> dependents;
};

class DagRunner {
public:
    explicit DagRunner(std::size_t worker_count = 4)
        : worker_count_(worker_count) {}

    void add_job(std::string name, std::chrono::milliseconds duration, bool should_fail = false) {
        jobs_.emplace(name, Job{
            .name = std::move(name),
            .duration = duration,
            .should_fail = should_fail
        });
    }

    void add_dependency(std::string_view parent_name, std::string_view child_name) {
        auto p_it = jobs_.find(std::string(parent_name));
        auto c_it = jobs_.find(std::string(child_name));
        if (p_it != jobs_.end() && c_it != jobs_.end()) {
            c_it->second.dependencies.push_back(p_it->first);
            c_it->second.in_degree++;
            p_it->second.dependents.push_back(c_it->first);
        }
    }

    void run() {
        {
            std::lock_guard lock(mutex_);
            for (auto& [name, job] : jobs_) {
                if (job.in_degree == 0) {
                    job.status = JobStatus::Ready;
                    ready_queue_.push(name);
                }
            }
        }

        std::vector<std::jthread> workers;
        workers.reserve(worker_count_);
        for (std::size_t i = 0; i < worker_count_; ++i) {
            workers.emplace_back([this](std::stop_token st) {
                worker_loop(st);
            });
        }

        {
            std::unique_lock lock(mutex_);
            cv_done_.wait(lock, [this] {
                return completed_count_ >= jobs_.size();
            });
            shutdown_ = true;
        }
        cv_ready_.notify_all();
    }

private:
    void cascade_skip(const std::string& failed_name) {
        for (auto& [name, job] : jobs_) {
            if (job.status == JobStatus::Pending || job.status == JobStatus::Ready) {
                for (const auto& dep : job.dependencies) {
                    if (dep == failed_name) {
                        job.status = JobStatus::Skipped;
                        completed_count_++;
                        std::cout << "[RUNNER C++] Job '" << job.name 
                                  << "' SKIPPED (upstream '" << failed_name << "' failed)\n";
                        cascade_skip(job.name);
                        break;
                    }
                }
            }
        }
    }

    void worker_loop(std::stop_token st) {
        while (!st.stop_requested()) {
            std::string current_job_name;

            {
                std::unique_lock lock(mutex_);
                cv_ready_.wait(lock, [this, &st] {
                    return !ready_queue_.empty() || shutdown_ || st.stop_requested();
                });

                if (shutdown_ || st.stop_requested() || completed_count_ >= jobs_.size()) {
                    break;
                }

                if (ready_queue_.empty()) continue;

                current_job_name = ready_queue_.front();
                ready_queue_.pop();
                jobs_[current_job_name].status = JobStatus::Running;
            }

            auto& job = jobs_[current_job_name];
            std::cout << "[RUNNER C++] Starting job '" << job.name 
                      << "' (" << job.duration.count() << " ms)...\n";

            std::this_thread::sleep_for(job.duration);
            bool success = !job.should_fail;

            {
                std::lock_guard lock(mutex_);
                completed_count_++;

                if (success) {
                    job.status = JobStatus::Success;
                    std::cout << "[RUNNER C++] Job '" << job.name << "' COMPLETED SUCCESS\n";

                    for (const auto& dep_name : job.dependents) {
                        auto& child = jobs_[dep_name];
                        if (child.status == JobStatus::Pending) {
                            child.in_degree--;
                            if (child.in_degree == 0) {
                                child.status = JobStatus::Ready;
                                ready_queue_.push(child.name);
                                cv_ready_.notify_one();
                            }
                        }
                    }
                } else {
                    job.status = JobStatus::Failed;
                    std::cout << "[RUNNER C++] Job '" << job.name << "' FAILED!\n";
                    cascade_skip(job.name);
                }

                if (completed_count_ >= jobs_.size()) {
                    cv_done_.notify_all();
                    cv_ready_.notify_all();
                }
            }
        }
    }

    std::size_t worker_count_;
    std::unordered_map<std::string, Job> jobs_;
    std::queue<std::string> ready_queue_;
    std::size_t completed_count_{0};
    bool shutdown_{false};
    std::mutex mutex_;
    std::condition_variable cv_ready_;
    std::condition_variable cv_done_;
};

int main() {
    DagRunner runner(4);

    runner.add_job("lint-and-format", std::chrono::milliseconds(50));
    runner.add_job("compile-binary", std::chrono::milliseconds(100));
    runner.add_job("unit-tests", std::chrono::milliseconds(80));
    runner.add_job("security-sast", std::chrono::milliseconds(60));
    runner.add_job("e2e-integration", std::chrono::milliseconds(120));
    runner.add_job("build-oci-image", std::chrono::milliseconds(90));

    runner.add_dependency("lint-and-format", "unit-tests");
    runner.add_dependency("compile-binary", "unit-tests");
    runner.add_dependency("compile-binary", "security-sast");
    runner.add_dependency("unit-tests", "e2e-integration");
    runner.add_dependency("security-sast", "e2e-integration");
    runner.add_dependency("e2e-integration", "build-oci-image");

    std::cout << "=== Starting C++20 DAG Pipeline Runner ===\n";
    runner.run();
    std::cout << "=== Pipeline Execution Finished ===\n";
    return 0;
}
```
:::

---

## Покроковий розбір механізмів синхронізації та управління пам'яттю

Реалізація рушія демонструє ключові відмінності між низькорівневим імперативним підходом мови C та сучасними ідіомами безпеки стандартів C++20.

### 1. Організація структур даних та виділення пам'яті
* **У версії мовою C**: стан конвеєра описується монолітною структурою `dag_runner_t`, яка розміщується на стеку або в статичній пам'яті. Усі масиви задач та черга мають фіксовані розміри (`MAX_JOBS`). Черга реалізована як класичний кільцевий буфер (англ. *circular ring buffer*) з двома показчиками `ready_head` та `ready_tail`. Це гарантує нульову фрагментацію пам'яті та відсутність викликів `malloc`/`free`, що є критичним для систем реального часу та вбудованих агентів збірки.
* **У версії мовою C++20**: використовується динамічний хеш-масив `std::unordered_map<std::string, Job>`, що забезпечує пошук задач за іменем за O(1) у середньому. Імена передаються за допомогою `std::string_view`, уникаючи зайвого копіювання рядків під час конструювання графу залежностей. Конструктори спираються на семантику переміщення (`std::move`) та безпечне володіння ресурсами без сирих вказівників.

### 2. Патерн багатопотокового пулу (Worker Pool) та умовні змінні
Обидві реалізації використовують патерн монітора (англ. *Monitor Pattern*) для координації потоків:
* Потоки воркерів блокуються на умовній змінній `cv_ready`, поки черга `ready_queue` порожня.
* Для запобігання проблемі втраченого пробудження (англ. *lost wakeup*) та фальшивих спрацьовувань (англ. *spurious wakeups*) виклик очікування завжди обгортається у цикл перевірки предикату. У C++20 це реалізовано через лямбда-предикат у методі `cv_ready_.wait(lock, [&] { return ...; })`.
* Головний потік очікує завершення всіх задач через окрему умовну змінну `cv_done`, засинаючи до моменту, коли `completed_count == jobs.size()`.

### 3. Автоматичне управління життєвим циклом потоків (RAII у C++20)
У версії C керування потоками вимагає явного створення через `pthread_create` та ручного очікування `pthread_join`. У разі виникнення винятку або передчасного виходу з функції ресурси можуть бути заблоковані або втрачені.

У версії C++20 застосовується клас `std::jthread` (введений у C++20), який автоматично викликає `request_stop()` та `join()` у своєму деструкторі за принципом RAII. Механізм `std::stop_token` забезпечує кооперативне переривання потоків під час аварійного зупинення конвеєра, дозволяючи коректно звільнити дескриптори файлів та мережеві з'єднання.

---

## Валідація графу та детекція циклічних залежностей

Перед тим як передати граф на виконання багатопотоковому пулу, рушій зобов'язаний виконати статичну верифікацію коректності структури DAG. Якщо конфігурація містить взаємні циклічні залежності (наприклад, задача A вимагає виконання B, а задача B вимагає A), запуск наївного планувальника призведе до вічного взаємного блокування (англ. *deadlock*), коли жодна з задач ніколи не зможе досягти нульового півстепеня заходу.

### Алгоритм розфарбовування вершин (DFS Cycle Detection)
Для виявлення циклів застосовується алгоритм пошуку в глибину з триколірним маркуванням вершин:
1. **Білий (WHITE)**: вершина ще не була відвідана під час обходу.
2. **Сірий (GREY)**: вершина наразі обробляється і знаходиться в поточному стеку викликів DFS.
3. **Чорний (BLACK)**: вершина та всі її нащадки повністю досліджені та не містять циклів.

Якщо під час рекурсивного обходу із сірої вершини u знайдено спрямоване ребро (u, v) у вершину v, яка вже має сірий колір, це однозначно доводить наявність зворотного ребра (англ. *back-edge*) і, відповідно, циклу в графі. У такому разі синтаксичний валідатор конвеєра повертає помилку `ERR_AST_CYCLE_DETECTED` із точним переліком вершин, що утворюють замкнений контур, зупиняючи запуск до початку виділення ресурсів агентів.

---

## Обробка системних сигналів та ізоляція процесів задач

У реальних виробничих системах задачі конвеєра є зовнішніми системними процесами (компіляторами, тестерами, контейнерами), які взаємодіють з операційною системою через системні виклики POSIX `fork()`, `execve()` та `waitpid()`.

### Управління групами процесів (Process Groups)
Якщо крок конвеєра породжує дочірні фонові процеси (наприклад, тестовий скрипт піднімає локальний тестовий екземпляр Redis та веб-сервер), звичайне надсилання сигналу `kill(pid, SIGTERM)` завершить лише батьківський процес оболонки, залишаючи дочірні демони працювати у фоні (утворюючи процеси-сироти).

Для гарантованого очищення ресурсів планувальник виконує ізоляцію кожної задачі у власну групу процесів:
1. Одразу після виклику `fork()` дочірній процес викликає `setpgid(0, 0)`, створюючи нову групу процесів з ідентифікатором, рівним власному PID.
2. У разі перевищення таймауту або отримання сигналу зупинки рушій надсилає сигнал усій групі процесів за допомогою від'ємного значення PID: `kill(-pgid, SIGKILL)`.
3. Це гарантує стовідсоткове знищення всіх породжених процесів, звільнення мережевих портів та запобігання витоку системної пам'яті на хості агента.

---

## Продуктивність та оптимізація планування на масштабі

### Закон Амдала та межа паралелізму
Згідно із законом Амдала, максимальне теоретичне прискорення конвеєра S(P) при використанні P паралельних воркерів обмежене часткою суворо послідовних задач s:

```text
S(P) = 1 / (s + (1 - s) / P)
```

Якщо збірка вимагає обов'язкової послідовної міграції бази даних або підписання фінального релізу криптографічним ключем, які займають 20% загального часу (s = 0.20), то навіть на кластері зі 100 воркерів максимальне прискорення не перевищить 1 / 0.20 = 5 разів. Тому архітектура високопродуктивних конвеєрів прагне до мінімізації критичного шляху через асинхронні перевірки.

### Безблокувальне планування (Work-Stealing Deques)
У високонавантажених CI-системах із сотнями воркерів централізована черга з єдиним м'ютексом стає вузьким місцем через ефект відскоку кеш-ліній (англ. *cache line bouncing*). 

Сучасні планувальники використовують алгоритм захоплення роботи (англ. *Work-Stealing*): кожен потік володіє власною локальною чергою (двосторонньою чергою Чейза-Лева, Chase-Lev deque). Власник додає та вилучає задачі зі своєї вершини за принципом LIFO без синхронізації, а вільні потоки «крадуть» готові задачі з протилежного кінця черги зайнятих потоків за принципом FIFO за допомогою атомарних інструкцій `compare_and_swap`, забезпечуючи максимальну локальність даних у кеші CPU L1/L2.
