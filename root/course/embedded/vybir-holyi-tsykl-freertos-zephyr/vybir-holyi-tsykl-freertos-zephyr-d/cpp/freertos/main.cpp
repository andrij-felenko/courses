// Складання приладу: об'єкти задач, їхні стеки й бюджет RAM в одному місці.
#include "board.hpp"
#include "message_queue.hpp"
#include "static_task.hpp"
#include "workers.hpp"

namespace {

constexpr std::size_t kSensorStackWords = 192;
constexpr std::size_t kDisplayStackWords = 384;
constexpr std::size_t kSupervisorStackWords = 128;

using SensorTask = rtos::StaticTask<kSensorStackWords>;
using DisplayTask = rtos::StaticTask<kDisplayStackWords>;
using SupervisorTask = rtos::StaticTask<kSupervisorStackWords>;

// Стеки службових задач ядра теж їдять ту саму пам'ять.
constexpr std::size_t kSystemStackBytes =
    (configMINIMAL_STACK_SIZE + configTIMER_TASK_STACK_DEPTH) * sizeof(StackType_t);

constexpr std::size_t kTotalStackBytes = SensorTask::stack_bytes() + DisplayTask::stack_bytes() +
                                         SupervisorTask::stack_bytes() + kSystemStackBytes;

// На чипі 8 КБ RAM. Перевищив бюджет — падає збірка, а не прилад у полі.
static_assert(kTotalStackBytes <= 4096, "стеки задач не влазять у бюджет RAM");
static_assert(app::SampleQueue::bytes() < 256, "черга роздулася — перевір розмір елемента");

app::SampleQueue g_queue;

// Супервізор питає запас стеків через ці дві функції: самі об'єкти задач
// оголошені нижче, а знати про них супервізорові й не треба.
std::size_t sensor_free_bytes();
std::size_t display_free_bytes();

// Задачі створюються в порядку залежностей: спершу супервізор, бо робочі
// задачі мають кому звітувати вже з першого свого оберту.
app::Supervisor g_supervisor_worker{&sensor_free_bytes, &display_free_bytes};

SupervisorTask g_supervisor{g_supervisor_worker, "supervisor", tskIDLE_PRIORITY + 3};

app::SensorWorker g_sensor_worker{g_queue, g_supervisor.handle()};
app::DisplayWorker g_display_worker{g_queue, g_supervisor.handle()};

SensorTask g_sensor{g_sensor_worker, "sensor", tskIDLE_PRIORITY + 2};
DisplayTask g_display{g_display_worker, "display", tskIDLE_PRIORITY + 1};

std::size_t sensor_free_bytes() { return g_sensor.untouched_bytes(); }
std::size_t display_free_bytes() { return g_display.untouched_bytes(); }

} // namespace

// Хуки ядра. Зі статичним розподілом пам'яті дві перші обов'язкові:
// без них FreeRTOS ніде взяти пам'ять під власні задачі, і збірка не злінкується.
extern "C" {

static StaticTask_t s_idle_tcb;
static StackType_t s_idle_stack[configMINIMAL_STACK_SIZE];
static StaticTask_t s_timer_tcb;
static StackType_t s_timer_stack[configTIMER_TASK_STACK_DEPTH];

void vApplicationGetIdleTaskMemory(StaticTask_t **tcb, StackType_t **stack, uint32_t *size)
{
    *tcb = &s_idle_tcb;
    *stack = s_idle_stack;
    *size = configMINIMAL_STACK_SIZE;
}

void vApplicationGetTimerTaskMemory(StaticTask_t **tcb, StackType_t **stack, uint32_t *size)
{
    *tcb = &s_timer_tcb;
    *stack = s_timer_stack;
    *size = configTIMER_TASK_STACK_DEPTH;
}

// Потребує configCHECK_FOR_STACK_OVERFLOW = 2. Продовжувати після переповнення
// не можна: пам'ять сусідньої задачі вже затерта, тож зупиняємось і чекаємо
// на watchdog, лишивши слід для налагоджувача.
void vApplicationStackOverflowHook(TaskHandle_t task, char *name)
{
    static volatile TaskHandle_t s_failed_task;
    static volatile const char *s_failed_name;

    s_failed_task = task;
    s_failed_name = name;

    taskDISABLE_INTERRUPTS();
    for (;;) { }
}

} // extern "C"

int main()
{
    board::init_pins();
    board::start_watchdog();

    vTaskStartScheduler();

    // Планувальник не повертається. Якщо повернувся — ядру бракує пам'яті;
    // нічого розумного вже не зробиш, лишається дати спрацювати watchdog.
    for (;;) { }
}
