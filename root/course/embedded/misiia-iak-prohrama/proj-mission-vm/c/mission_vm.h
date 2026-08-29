/* mission_vm.h — бортова віртуальна машина виконання місії.
 *
 * Дві межі задано наперед і вони не обговорюються:
 *
 *   · після завантаження місії машина НЕ виділяє пам'яті. Ні malloc, ні пулів
 *     «про запас»: увесь контекст виконання живе в mission_vm_t, а сам байткод
 *     лишається там, де лежав (Flash/ROM) — машина тримає на нього вказівник,
 *     а не копію;
 *
 *   · один виклик mission_vm_step() виконує РІВНО ОДНУ інструкцію або одну
 *     перевірку умови й повертається. Ніякого «доганяємо чергу»: крок ділить
 *     процесор з контуром стабілізації, тож він мусить коштувати передбачувано
 *     мало. Циклів, чия довжина залежить від даних, у машині немає взагалі.
 */
#ifndef MISSION_VM_H
#define MISSION_VM_H

#include <stdbool.h>
#include <stdint.h>

/* Скільки інструкцій дозволено в місії. Межа не про пам'ять (байткод не
 * копіюється), а про те, щоб індекс стрибка гарантовано влазив у int16_t. */
#define VM_MAX_INSTRUCTIONS 256u

/* Скільки різних інструкцій DO_JUMP може містити місія: стільки ж потрібно
 * лічильників повторів у RAM. */
#define VM_MAX_LOOP_SLOTS 16u

/* Глобальний бюджет переходів на всю місію. Перевищення означає, що програма
 * закільцювалася: осмислена місія не робить понад дві з половиною сотні
 * стрибків. */
#define VM_MAX_TOTAL_JUMPS 256u

/* Радіус, у якому точку вважають досягнутою, коли навігатор не сказав інакше. */
#define VM_WAYPOINT_RADIUS_M 2.0f
/* Допуск на курс для COND_YAW. */
#define VM_YAW_TOLERANCE_DEG 5.0f
/* Частка заданої висоти, з якої зліт уважають виконаним. */
#define VM_TAKEOFF_ALT_FRACTION 0.95f
/* Висота, на якій виконується повернення на точку старту. */
#define VM_RTL_ALT_M 30.0f

/* Опкоди. Числа зафіксовані назавжди: за ними компілятор місії на наземній
 * станції складає той самий байткод, що читає борт. Класи розведено по
 * старшому півбайту, щоб дизасемблер і людське око бачили тип операції:
 *   0x0_ — навігація (переміщення, машина чекає на досягнення),
 *   0x1_ — миттєві дії над корисним навантаженням,
 *   0x2_ — керування потоком (стрибки й цикли),
 *   0x3_ — неблокуючі умови очікування.                                     */
typedef enum {
    OP_HALT            = 0x00, /* кінець програми                            */
    OP_NAV_TAKEOFF     = 0x01, /* зліт на alt_m над домашньою точкою          */
    OP_NAV_WAYPOINT    = 0x02, /* політ у точку lat/lon/alt                   */
    OP_NAV_LAND        = 0x03, /* посадка на місці                            */
    OP_NAV_RTL         = 0x04, /* повернення на точку старту                  */
    OP_DO_SET_SERVO    = 0x10, /* param1 — канал, param2 — ширина імпульсу    */
    OP_DO_CHANGE_SPEED = 0x11, /* param2 — цільова швидкість, см/с            */
    OP_DO_JUMP         = 0x20, /* param1 — індекс цілі, param2 — скільки разів*/
    OP_JUMP_IF_BAT_LOW = 0x21, /* param1 — поріг у %, param2 — індекс цілі    */
    OP_COND_DELAY      = 0x30, /* param1 — витримка, секунди                  */
    OP_COND_DISTANCE   = 0x31, /* param1 — лишилося не більше N метрів        */
    OP_COND_YAW        = 0x32  /* param1 — курс у градусах                    */
} vm_opcode_t;

/* Прапорці інструкції (поле flags). */
/* Уставку видано — і одразу наступна інструкція, не чекаючи досягнення. Саме
 * так між двома точками вставляють умову «за 30 метрів до точки». */
#define VM_FLAG_AUTO_CONTINUE 0x01u
/* alt_m задано над рівнем моря, а не над домашньою точкою. */
#define VM_FLAG_ALT_ABSOLUTE 0x02u

/* Одна інструкція місії. Рівно 20 байтів із ПРИРОДНИМ вирівнюванням: кожне
 * поле стоїть на своїй межі саме, без __attribute__((packed)). Упакована
 * структура коштувала б невирівняних читань на кожному кроці, а виграшу в
 * пам'яті не дала б — байткод і так лежить у Flash. */
typedef struct {
    uint8_t opcode;  /* значення з vm_opcode_t, збережене одним байтом        */
    uint8_t flags;   /* VM_FLAG_*                                             */
    int16_t param1;  /* час (с), канал, кут (град), поріг батареї (%), індекс */
    int16_t param2;  /* повтори, ширина імпульсу (мкс), швидкість (см/с)      */
    int32_t lat_1e7; /* широта × 10⁷ — дискретність близько 1 см             */
    int32_t lon_1e7; /* довгота × 10⁷                                        */
    float   alt_m;   /* цільова висота, метри                                 */
} vm_instruction_t;

_Static_assert(sizeof(vm_instruction_t) == 20,
               "інструкція мусить лишатися 20-байтовою: за цим числом наземна "
               "станція нарізає байткод");

typedef enum {
    VM_STATUS_IDLE,                /* місії не завантажено                   */
    VM_STATUS_RUNNING,             /* виконується, чекати нема на що          */
    VM_STATUS_WAITING_NAV,         /* уставку видано, летимо до точки         */
    VM_STATUS_WAITING_COND,        /* чекаємо на час, відстань або курс       */
    VM_STATUS_COMPLETED,           /* програма дійшла до кінця                */
    VM_STATUS_ERROR_INFINITE_LOOP, /* вичерпано бюджет переходів              */
    VM_STATUS_ERROR_OUT_OF_BOUNDS, /* стрибок на неіснуючий індекс            */
    VM_STATUS_ERROR_INVALID_OPCODE /* байт не належить переліку опкодів       */
} vm_status_t;

/* Чому місію не взято до виконання. Відхилити програму ДО зльоту дешевше, ніж
 * упертися в її ваду посеред польоту. */
typedef enum {
    VM_LOAD_OK,
    VM_LOAD_EMPTY,          /* нуль інструкцій                               */
    VM_LOAD_TOO_LONG,       /* довша за VM_MAX_INSTRUCTIONS                   */
    VM_LOAD_NO_HOME,        /* домашню точку не задано                        */
    VM_LOAD_BAD_OPCODE,     /* невідомий опкод                                */
    VM_LOAD_BAD_PARAM,      /* аргумент поза допустимим діапазоном            */
    VM_LOAD_BAD_JUMP,       /* ціль стрибка поза програмою                    */
    VM_LOAD_TOO_MANY_LOOPS, /* DO_JUMP-ів більше, ніж слотів лічильників      */
    VM_LOAD_NO_TERMINATOR   /* остання інструкція не завершує програму        */
} vm_load_result_t;

/* Знімок стану апарата, який машина читає й ніколи не змінює. Готує його
 * навігаційний контур (100 Гц), машина бачить його вже цілим. */
typedef struct {
    int32_t lat_1e7;
    int32_t lon_1e7;
    float   alt_m;          /* висота над домашньою точкою                    */
    float   yaw_deg;        /* курс, градуси                                  */
    float   dist_to_wp_m;   /* до активної уставки; NaN — позиції немає       */
    float   battery_soc_pct;
    bool    wp_reached;     /* навігатор сам сказав «на місці»                */
    bool    gcs_link_ok;    /* машина сюди НЕ дивиться: втрата зв'язку з
                             * наземною станцією не спиняє автономну програму */
} vm_telemetry_t;

/* Усе, що машина віддає назовні за такт. Виконавчий потік читає структуру й
 * перетворює її на уставки регуляторів. */
typedef struct {
    bool     nav_valid;        /* просторова уставка чинна                    */
    int32_t  target_lat_1e7;
    int32_t  target_lon_1e7;
    float    target_alt_m;     /* завжди над домашньою точкою                 */
    float    target_speed_mps; /* 0 — швидкості не задавали                   */
    uint8_t  servo_channel;
    uint16_t servo_pwm_us;
    bool     rtl_triggered;
    bool     land_triggered;
    bool     failsafe_request; /* машина спинилася аварійно — вирішуй сам     */
} vm_actuators_t;

typedef struct {
    int32_t lat_1e7;
    int32_t lon_1e7;
    float   alt_m; /* висота домашньої точки над рівнем моря                  */
} vm_home_t;

/* Лічильник повторів одного DO_JUMP. Слот прив'язано до АДРЕСИ САМОГО
 * СТРИБКА, а не до його цілі: інакше два різні DO_JUMP на ту саму мітку
 * ділили б один лічильник і вкладені цикли рахувалися б неправильно. */
typedef struct {
    uint16_t jump_pc;
    uint16_t remaining;
    bool     active;
} vm_loop_slot_t;

typedef struct {
    /* Байткод НЕ копіюється в RAM — вказівник дивиться просто у Flash. */
    const vm_instruction_t *program;
    uint16_t                program_len;

    uint16_t    pc;
    vm_status_t status;
    bool        home_set;
    vm_home_t   home;

    /* Стан ПОТОЧНОЇ інструкції: чи ми вже зробили для неї одноразову дію —
     * видали уставку, засікли час. Скидається на кожному переході. */
    bool     entered;
    uint32_t instr_entry_ms;

    uint32_t total_jumps;    /* сторож нескінченних циклів                    */
    uint32_t steps_executed; /* для журналу й тестів                          */

    vm_loop_slot_t loops[VM_MAX_LOOP_SLOTS];
} mission_vm_t;

/* Привести машину у вихідний стан. Місії ще немає, домашньої точки теж. */
void mission_vm_init(mission_vm_t *vm);

/* Задати домашню точку. Мусить бути викликано ДО mission_vm_load(): від неї
 * рахується відносна висота й до неї повертає RTL. */
void mission_vm_set_home(mission_vm_t *vm, int32_t lat_1e7, int32_t lon_1e7, float alt_m);

/* Перевірити програму й узяти її до виконання. Указівник code мусить лишатися
 * дійсним увесь політ — машина зберігає його, а не вміст. */
vm_load_result_t mission_vm_load(mission_vm_t *vm, const vm_instruction_t *code, uint16_t len);

/* Один такт. Викликається періодично (20–50 Гц) із задачі місії й ніколи не
 * блокує: якщо чекати ще рано, повертає WAITING_* і віддає процесор. */
vm_status_t mission_vm_step(mission_vm_t *vm,
                            const vm_telemetry_t *telem,
                            vm_actuators_t       *act,
                            uint32_t              now_ms);

bool mission_vm_is_error(vm_status_t status);
bool mission_vm_is_active(vm_status_t status);

/* Скільки машина сидить на поточній інструкції. Саме за цим числом ЗОВНІШНІЙ
 * супервізор вирішує, що очікування затяглося (наприклад, GNSS не
 * повертається): сама машина таймаутів не має й чекати може вічно. */
uint32_t mission_vm_wait_elapsed_ms(const mission_vm_t *vm, uint32_t now_ms);

const char *vm_status_name(vm_status_t status);
const char *vm_load_result_name(vm_load_result_t result);

#endif /* MISSION_VM_H */
