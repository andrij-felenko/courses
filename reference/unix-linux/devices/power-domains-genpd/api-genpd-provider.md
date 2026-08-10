# 📋 genpd: інтерфейс постачальника й споживача

Це контракт двох сторін: коду, який **володіє** вимикачем регіону живлення (постачальника домену), і коду, який лише **живе** всередині регіону — драйвера пристрою, шини, вузла в дереві пристроїв. Нижче зібрано поля структур, прапорці поведінки, сигнатури, властивості дерева пристроїв і файли, які видно назовні.

Звірено з деревом mainline: `include/linux/pm_domain.h`, `drivers/pmdomain/core.c`, `drivers/pmdomain/governor.c`, `drivers/base/power/common.c`, `drivers/base/power/sysfs.c`. Врахуйте переїзд: genpd жив у `drivers/base/power/domain.c` і `domain_governor.c`, а тепер це `drivers/pmdomain/core.c` і `drivers/pmdomain/governor.c` — старіші статті й закладки ведуть у порожнечу.

---

## 1. `struct generic_pm_domain`: що заповнює постачальник

| Поле | Тип | Що це |
| --- | --- | --- |
| `name` | `const char *` | ім'я домену; під ним домен видно в debugfs і в зведенні |
| `power_on` | `int (*)(struct generic_pm_domain *)` | закрити вимикач: подати напругу, дочекатися готовності, зняти скидання. `0` — успіх |
| `power_off` | те саме | відкрити вимикач. Обидва можуть спати — крім домену з `GENPD_FLAG_IRQ_SAFE` |
| `states` · `state_count` | `struct genpd_power_state *` · `unsigned int` | масив станів вимкнення, від найдрібнішого до найглибшого |
| `state_idx` | `unsigned int` | індекс стану, у який домен вимикають зараз; вибрав губернатор, читає `power_off` |
| `gov` | `struct dev_power_governor *` | політика: чи варто вимикати й у який стан. `NULL` — вимикати завжди і лише в `states[0]` |
| `flags` | `unsigned int` | набір `GENPD_FLAG_*` (§3) |
| `set_performance_state` | `int (*)(struct generic_pm_domain *, unsigned int)` | перевести регіон на новий рівень продуктивності |
| `attach_dev` · `detach_dev` | `int (*)(…, struct device *)` · `void (*)(…)` | гачки на мить приєднання пристрою до домену й від'єднання від нього |

Решту веде ядро — постачальник ці поля читає, а не пише:

| Поле | Що показує |
| --- | --- |
| `device_count` | скільки пристроїв **приєднано** до домену (не скільки з них активні) |
| `sd_count` | `atomic_t`: скільки піддоменів зараз увімкнено |
| `suspended_count` · `prepared_count` | лічильники системного сну: скільки пристроїв приспано й підготовлено |
| `status` | `GENPD_STATE_ON` або `GENPD_STATE_OFF`; початкове значення задає `is_off` при ініціалізації |

Лічильника активних пристроїв у структурі немає взагалі. Перед кожним вимкненням genpd проходить свій список і питає в кожного пристрою `pm_runtime_suspended()` — джерело правди про потрібність лишається в [runtime PM](book:unix-linux/runtime-power-management), який рахує заявників на пристрій, а домен щоразу перечитує його наново.

---

## 2. `struct genpd_power_state`: один стан вимкнення

| Поле | Хто пише | Що це |
| --- | --- | --- |
| `name` | постачальник | ім'я стану; під ним він з'являється у файлі `idle_states` |
| `power_off_latency_ns` | постачальник | скільки триває саме вимикання |
| `power_on_latency_ns` | постачальник | скільки триває повернення живлення |
| `residency_ns` | постачальник | найменше лежання, за яке перехід окупається |
| `usage` | ядро | скільки разів у цей стан входили |
| `rejected` | ядро | скільки разів губернатор відмовив саме на цьому стані |
| `above` · `below` | ядро | скільки разів стан виявився надто глибоким і надто дрібним |
| `idle_time` | ядро | сумарний час, пролежаний у стані |

П'ять останніх полів — це і є вміст `idle_states` у debugfs. Коли постачальник лишив `state_count` нулем, `pm_genpd_init()` заводить один нульовий стан: без затримок і без витримки, тобто вимикати можна завжди.

---

## 3. Прапорці `flags`

| Прапорець | Біт | Сенс |
| --- | --- | --- |
| `GENPD_FLAG_PM_CLK` | 0 | домен сам знімає й повертає такти своїх пристроїв через [каркас тактування](book:unix-linux/clock-framework), який рахує споживачів кожного такту |
| `GENPD_FLAG_IRQ_SAFE` | 1 | `power_on`/`power_off` не сплять — домен можна вмикати з атомарного контексту |
| `GENPD_FLAG_ALWAYS_ON` | 2 | не вимикати ніколи: ні на ходу, ні в системному сні |
| `GENPD_FLAG_ACTIVE_WAKEUP` | 3 | тримати ввімкненим, поки котрийсь із пристроїв бере участь у пробудженні |
| `GENPD_FLAG_CPU_DOMAIN` | 4 | у домені або в його піддоменах є процесорні ядра |
| `GENPD_FLAG_RPM_ALWAYS_ON` | 5 | не вимикати на ходу, але в системному сні — можна |
| `GENPD_FLAG_MIN_RESIDENCY` | 6 | губернаторові дозволено враховувати оголошене найближче пробудження |
| `GENPD_FLAG_OPP_TABLE_FW` | 7 | рівні продуктивності є, але таблиць OPP у дереві пристроїв немає — їх знає прошивка |
| `GENPD_FLAG_DEV_NAME_FW` | 8 | генерувати унікальні імена пристроїв домену через `ida` |
| `GENPD_FLAG_NO_SYNC_STATE` | 9 | постачальник сам вирішує, коли для нього настав `sync_state` |
| `GENPD_FLAG_NO_STAY_ON` | 10 | не тримати ввімкненим домен лише тому, що він був увімкнений на момент реєстрації |

Обидва «завжди ввімкнено» перевіряє сам `genpd_power_off()`, а не губернатор. Це важливо, бо `pm_domain_always_on_gov` у чинному ядрі має тільки `->suspend_ok`: колишній `always_on_power_down_ok()`, що просто вертав «не можна», прибрано, і тримати домен живим тепер належить прапорцю, а не губернаторові.

---

## 4. Постачальник: реєстрація

```c
int  pm_genpd_init(struct generic_pm_domain *genpd,
                   struct dev_power_governor *gov, bool is_off);
int  pm_genpd_remove(struct generic_pm_domain *genpd);

int  pm_genpd_add_subdomain(struct generic_pm_domain *genpd,
                            struct generic_pm_domain *subdomain);
int  pm_genpd_remove_subdomain(struct generic_pm_domain *genpd,
                               struct generic_pm_domain *subdomain);

int  of_genpd_add_provider_simple(struct device_node *np,
                                  struct generic_pm_domain *genpd);
int  of_genpd_add_provider_onecell(struct device_node *np,
                                   struct genpd_onecell_data *data);
void of_genpd_del_provider(struct device_node *np);

int  of_genpd_parse_idle_states(struct device_node *dn,
                                struct genpd_power_state **states, int *n);

int  pm_genpd_add_device(struct generic_pm_domain *genpd, struct device *dev);
int  pm_genpd_remove_device(struct device *dev);
```

Порядок жорсткий: спершу `pm_genpd_init()` на кожен домен, потім `pm_genpd_add_subdomain()` на кожне ребро вкладеності, і аж тоді реєстрація постачальником — інакше споживач може прийти по домен, який ще не має піддоменів. `pm_genpd_remove()` вертає `-EBUSY`, доки в домені лишається хоч один пристрій, піддомен чи батько.

Вибір між двома `of_genpd_add_provider_*` диктує вузол у дереві: `simple` — один домен на вузол і `#power-domain-cells = <0>`, `onecell` — масив доменів і `<1>`, де число в посиланні є індексом у `genpd_onecell_data.domains`. Пари `pm_genpd_add_device()`/`pm_genpd_remove_device()` — це прив'язка руками, для пристроїв, яких у дереві немає.

---

## 5. Споживач: прив'язка пристрою

```c
int  dev_pm_domain_attach(struct device *dev, u32 flags);
struct device *dev_pm_domain_attach_by_id(struct device *dev, unsigned int index);
struct device *dev_pm_domain_attach_by_name(struct device *dev, const char *name);
int  dev_pm_domain_attach_list(struct device *dev,
                               const struct dev_pm_domain_attach_data *data,
                               struct dev_pm_domain_list **list);
void dev_pm_domain_detach(struct device *dev, bool power_off);
void dev_pm_domain_detach_list(struct dev_pm_domain_list *list);
```

Перша функція — та, яку викликає шина до `probe`, і в неї вже не `bool power_on`, а набір прапорців; за одним доменом на пристрій драйвер сам не ходить. Дві наступні дістають домен за номером чи за іменем із `power-domain-names` і **вертають новостворений віртуальний пристрій** (`ERR_PTR` при невдачі) — саме його драйвер прив'язує до свого справжнього. `dev_pm_domain_attach_list()` робить це гуртом. Спільний для всіх код помилки — `-EPROBE_DEFER`: постачальник домену ще не завантажився.

| Прапорець | Що змінює |
| --- | --- |
| `PD_FLAG_NO_DEV_LINK` | не заводити [зв'язок між пристроями](book:unix-linux/device-links) — явне ребро «постачальник → споживач», яким ядро впорядковує сон і пробудження |
| `PD_FLAG_DEV_LINK_ON` | створюючи зв'язок, одразу ввімкнути постачальника й домен |
| `PD_FLAG_REQUIRED_OPP` | зіставити домени з `required-opps` за індексом |
| `PD_FLAG_ATTACH_POWER_ON` | увімкнути домен на час прив'язки |
| `PD_FLAG_DETACH_POWER_OFF` | вимкнути домен при від'єднанні |

Ті самі прапорці кладуть у `dev_pm_domain_attach_data.pd_flags` разом зі списком імен `pd_names`.

---

## 6. Драйвер під час роботи

```c
int     dev_pm_genpd_set_performance_state(struct device *dev, unsigned int state);
void    dev_pm_genpd_set_next_wakeup(struct device *dev, ktime_t next);
ktime_t dev_pm_genpd_get_next_hrtimer(struct device *dev);
void    dev_pm_genpd_synced_poweroff(struct device *dev);
int     dev_pm_genpd_add_notifier(struct device *dev, struct notifier_block *nb);
int     dev_pm_genpd_remove_notifier(struct device *dev);
```

`set_performance_state()` оголошує вимогу **цього** пристрою; genpd бере по домену максимум із усіх оголошень і піддоменів. Аргумент `0` знімає вимогу; `-ENODEV` означає, що пристрій узагалі не в домені. `set_next_wakeup()` має вагу лише тоді, коли домен заявив `GENPD_FLAG_MIN_RESIDENCY`, — без прапорця губернатор ці числа не читає.

---

## 7. Губернатори і що саме перевіряє `power_down_ok()`

| Губернатор | `->suspend_ok` | `->power_down_ok` | `->system_power_down_ok` |
| --- | --- | --- | --- |
| `simple_qos_governor` | `default_suspend_ok` | `default_power_down_ok` | — |
| `pm_domain_always_on_gov` | `default_suspend_ok` | **немає** | — |
| `pm_domain_cpu_gov` | `default_suspend_ok` | `cpu_power_down_ok` | `cpu_system_power_down_ok` |
| `NULL` | — | — | — |

Губернатора питають **останнім**. До нього `genpd_power_off()` сам відмовляє, коли домен уже вимкнено, коли стоїть `GENPD_FLAG_ALWAYS_ON` чи `GENPD_FLAG_RPM_ALWAYS_ON`, коли `sd_count > 0`, коли триває підготовка до системного сну (`prepared_count > 0`), коли хтось із пристроїв не `pm_runtime_suspended()`, коли на пристрої висить `PM_QOS_FLAG_NO_POWER_OFF` або коли IRQ-безпечний пристрій сидить у домені, що спить.

Аж тоді `default_power_down_ok()` рахує бюджет. Для кожного пристрою бере його межу затримки пробудження — [обмеження PM QoS](book:unix-linux/pm-qos-constraints), найжорсткіше з оголошених пристроєм і його дітьми, — і віднімає власні затримки пристрою на засинання й пробудження:

```
бюджет пристрою = межа PM QoS − (suspend_latency_ns + resume_latency_ns)

стан i дозволено ⟺ бюджет > power_off_latency_ns[i] + power_on_latency_ns[i]
                    для КОЖНОГО пристрою й піддомену

межа PM_QOS_RESUME_LATENCY_NO_CONSTRAINT_NS — пристрій із розрахунку випадає
```

Береться найглибший стан, що проходить у всіх; не пройшов жоден — вимикати не можна. З `GENPD_FLAG_MIN_RESIDENCY` додається друга умова: очікуване лежання до найближчого пробудження мусить перекрити `power_off_latency_ns + residency_ns` — та сама точка окупності, що й у [сну ядра процесора](book:unix-linux/cpuidle-and-cstates), тільки з іншим джерелом оцінки часу.

---

## 8. Дерево пристроїв

| Властивість | Де | Що означає |
| --- | --- | --- |
| `#power-domain-cells` | постачальник | скільки чисел треба, щоб назвати домен: `<0>` — один домен на вузол, `<1>` — індекс у масиві |
| `power-domains` | споживач | посилання на домен (або кілька) |
| `power-domain-names` | споживач | імена для `dev_pm_domain_attach_by_name()`; порядок збігається з `power-domains` |
| `domain-idle-states` | вузол домену | посилання на вузли станів вимкнення |
| `operating-points-v2` | споживач | [таблиця робочих точок](book:unix-linux/opp-tables), що зв'язує частоту з напругою й рівнем домену |
| `required-opps` | робоча точка | який рівень домену потрібен цій частоті пристрою |

```dts
domain_ret: domain-retention {
        compatible = "domain-idle-state";
        entry-latency-us = <120>;    /* → power_off_latency_ns */
        exit-latency-us  = <300>;    /* → power_on_latency_ns  */
        min-residency-us = <1000>;   /* → residency_ns         */
};

pd_video: power-domain {
        #power-domain-cells = <0>;
        domain-idle-states = <&domain_ret>;
};

codec_opps: opp-table {
        compatible = "operating-points-v2";
        opp-600000000 {
                opp-hz = /bits/ 64 <600000000>;
                required-opps = <&pd_video_high>;
        };
};
```

Ці три числа `of_genpd_parse_idle_states()` перекладає в поля `struct genpd_power_state` — мікросекунди з опису стають наносекундами в структурі.

---

## 9. Що видно назовні

У `/sys/kernel/debug/pm_genpd/` лежить підкаталог на кожен домен, а поруч — зведення `pm_genpd_summary` на всі одразу.

| Файл | Що показує |
| --- | --- |
| `current_state` | `on` або `off-N`, де `N` — індекс стану вимкнення |
| `devices` | приєднані пристрої та їхній стан у runtime PM |
| `sub_domains` | піддомени й чи ввімкнені вони |
| `idle_states` | рядок на стан: `usage`, `rejected`, `above`, `below`, накопичений `idle_time` |
| `active_time` · `total_idle_time` | скільки домен пробув увімкненим і вимкненим |
| `perf_state` | поточний рівень продуктивності — лише в домену, що його підтримує |

З боку кожного пристрою є `power/pm_qos_resume_latency_us` у sysfs — саме те число, з якого губернатор рахує бюджет.

> 🔧 **Навіщо це.** Читається цей файл не так, як здається. `0` означає **немає обмеження**: домен вільний вимикатися як завгодно глибоко. А `n/a` означає протилежне — прийнятна затримка нульова, тобто вимикати не можна взагалі. Запис дзеркальний: `echo 0` знімає обмеження, `echo n/a` ставить найжорсткіше. Тому «у файлі нуль, а домен не спить» і «там написано n/a, значить обмежень немає» — два найчастіші хибні висновки при розборі, чому регіон лишається під напругою.
