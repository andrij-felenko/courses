# Аналіз модуля «proshyvka» — «Прошивка й відлагодження»

Курс: guide/embedded («Вбудована електроніка й автономні системи»), секція 9 з 14.
Поточний стан: 19 тем пласким списком (1 ref + 18 own), без розділів.

## 1. Діагноз модуля

Модуль — «шухляда для всього, що не влізло деінде»: у ньому впереміш живуть **чотири різні модулі**:
приладовий стенд (осцилограф, шунт, споживання), калібрування вимірювального тракту,
інженерія коду прошивки (SOLID, помилки, пам'ять, конкурентність), тестування/надійність
та випуск/безпека (git, TPM). Нитки між сусідніми темами нема: після «Тестування прошивки»
йде «Коди помилок», після «FMEA» — «addr2line», після «TPM» — «SOLID». Половина назви —
«відлагодження» — насправді живе в секції mk (jtag-swd-tools, openocd-gdb, core-dump,
debug-io-comparison), а тут лишився тільки хвіст (addr2line-workflow).

Системна причина більшості прогалин: **курс не використовує книгу programming жодного разу**
(грепом по маніфесту: 0 кроків `ref: "programming/…"`), хоча в ній є готовий (basic: done)
embedded-блок: компіляція/лінкування/образ прошивки, bootloader, таймери, watchdog, RTOS
(tasks/scheduler/freertos/task-ipc/atomicity-races), OTA, secure boot, файлові системи Flash.
Модуль «Прошивка» — головний споживач саме цих статей.

## 2. Порушення порядку (конкретно)

Нумерація — поточні позиції в секції (1–19).

1. **sine-on-scope (2) користується осцилографом, якого курс ніде не вводив кроком.**
   Стаття сама рятується попап-лінком на `topic:electronics/oscilloscope`, але для новачка
   це перший «прилад» у курсі — а мультиметра, лабораторного БЖ і самого осцилографа
   як кроків немає взагалі. Статті в книзі є (metrology, basic done).
2. **frequency-measurement-methods (19) відірвано від вимірювального блоку (1–4)** — стоїть
   останнім після git і TPM. Гірше: стаття лінкує **вперед** на `root:embedded/signal-acquisition`
   (секція keruvannia, 12-та — читач її ще не бачив) і спирається на таймер-лічильник МК
   та input capture, яких у курсі немає взагалі (у книзі programming є: timer-counter,
   capture-compare — done). Також лінкує `topic:electronics/counters` — лічильники теж не були кроком.
3. **firmware-testing (5) стоїть перед усім блоком про якість коду** — error-codes-vs-exceptions (6),
   solid-principles (14), error-propagation-patterns (16), memory-safety (17). Юніт-тести
   й «шов» між логікою та залізом спираються на структуру коду й обробку помилок; порядок
   інвертований. (При цьому fatfs-integration (7) явно посилається назад на firmware-testing —
   отже firmware-testing мусить лишитися ПЕРЕД fatfs, це обмеження нового порядку.)
4. **error-codes-vs-exceptions (6) і error-propagation-patterns (16) розірвані** десятьма
   чужими темами, хоча друга — пряме продовження першої.
5. **calibration-procedure (10) «Процедура калібрування давача» стоїть на секцію раніше за давачі**
   (davachi — наступна, 10-та секція курсу): читач калібрує давач, не знаючи жодного давача.
6. **tpm-trustzone (13) відкривається словами «Ми вже навчилися підписувати прошивку й перевіряти
   підпис — [secure boot]»** — але кроку `programming/secure-boot` у курсі немає взагалі
   (стаття в книзі є, basic done, з math-hash-signature).
7. **spinlock-mutex (18) вимагає задач, планувальника і поняття гонок** — RTOS-блоку в курсі
   немає ніде (mk/super-loop-limits лише підводить до нього). Спінлок проти м'ютекса без
   поняття «задача блокується» — стіна незнаного.
8. **gitflow-branching (15) — стратегії гілкування без жодного кроку про сам git**/контроль версій
   (у книзі programming є слот version-control, basic поки pending).
9. **addr2line-workflow (12) вимагає ELF/символів/тулчейна** — курс ніде не пояснює ланцюг
   компіляція→лінкування→образ. До того ж його пререквізит core-dump живе в mk (секція 7),
   а продовження — тут (9): пару розірвано між секціями.
10. **fatfs-integration (7) — файлова система до того, як курс згадав SD-картку чи поняття
    файлової системи** (electronics/sd-card і programming/flash-filesystems існують, done).
11. **Дублювання з mk:** current-profiler-tools і power-logger (mk, секція 7) стоять РАНІШЕ
    за базове measure-consumption (тут, 4); `proj-coulomb-counter.md` фізично існує двічі —
    у mk/power-logger і в proshyvka/measure-consumption; comp-current-profiler (тут) ≈
    comp-power-profiler-instruments (mk). Базове вимірювання мусить іти перед спеціалізованими
    профайлерами, а дублікат вставок — злити.
12. **kelvin-shunt (1) як перший крок** — прийнятний по пререквізитах (опір/потужність були),
    але логічніше після загального знайомства з приладами й перед measure-consumption.

## 3. Пропоновані розділи (усі 19 поточних тем збережені: 18 тут + 1 у move_out)

### Р1. Прилади на столі: побачити сигнал (9 кроків)
Мотив: перший вимірювальний стенд; без нього ні залізо, ні прошивку не відладиш.
1. ref:electronics/multimeter — ДОДАТИ: перший прилад новачка, у курсі приладів нема взагалі
2. ref:electronics/oscilloscope — ДОДАТИ: sine-on-scope лінкує його попапом, кроку нема
3. own:sine-on-scope
4. ref:electronics/measurement-errors — ДОДАТИ: як читати покази і не вірити їм сліпо
5. own:noise-hunting
6. ref:electronics/logic-analyzer — ДОДАТИ: цифрові шини з peryferiia (SPI/I2C) дебажити нічим
7. ref:electronics/kelvin-shunt (наявний крок)
8. own:measure-consumption
9. own:current-profiler-tools (move_in із mk — спеціалізовані профайлери після базового вимірювання)

### Р2. МК вимірює сам: лічильники, таймери, частота (4)
1. ref:electronics/counters — ДОДАТИ: стаття frequency-measurement лінкує їх, кроку не було
2. ref:programming/timer-counter — ДОДАТИ: таймер МК — базовий інструмент усього подальшого
3. ref:programming/capture-compare — ДОДАТИ: input capture, на якому стоїть вимірювання періоду
4. own:frequency-measurement-methods (перенесено з кінця секції до вимірювального блоку)

### Р3. Точність тракту: опора, похибки, калібрування (5)
1. ref:electronics/adc — ДОДАТИ: базове знайомство з АЦП; mk/dma-adc уже його мовчки вимагав
2. ref:electronics/adc-errors — ДОДАТИ: зміщення/підсилення/нелінійність — мова калібрування
3. ref:electronics/voltage-reference — ДОДАТИ: без поняття опорної напруги калібрування опорою не прочитати
4. own:adc-reference-calibration
5. ref:electronics/calibration — ДОДАТИ: загальна процедура; місток до calibration-procedure у davachi

### Р4. Від коду до чипа: тулчейн і прошивання (6)
1. ref:programming/compilation — ДОДАТИ: курс ніде не пояснює, як текст стає машинним кодом
2. ref:programming/linking — ДОДАТИ: без лінкера не зрозуміти ані ELF, ані addr2line, ані map-файл
3. ref:programming/firmware-image — ДОДАТИ: що саме заливається у Flash (образ, секції, версія)
4. ref:programming/bootloader — ДОДАТИ: esptool говорить із ROM-завантажувачем; без цього — магія
5. own:esptool-workflow (move_in із mk — «прошивання» буквально тема цього модуля)
6. own:jtag-swd-tools (move_in із mk — проби: місток від заливання до відлагодження)

### Р5. Відлагодження: наживо й посмертно (4)
1. own:debug-io-comparison (move_in із mk — найдоступніший канал: лог)
2. own:openocd-gdb (move_in із mk — кроковий дебаг)
3. own:core-dump (move_in із mk — посмертний аналіз; його продовження і так тут)
4. own:addr2line-workflow (тепер одразу після свого пререквізиту)

### Р6. Код, який можна супроводжувати (6)
1. own:solid-principles (структура — перед помилками й тестами)
2. own:error-codes-vs-exceptions
3. own:error-propagation-patterns (одразу після свого початку, а не через 10 тем)
4. ref:programming/assert-panic — ДОДАТИ: третій стовп обробки помилок; згадується скрізь далі
5. ref:programming/addresses-pointers — ДОДАТИ: без покажчиків memory-safety — стіна
6. own:memory-safety

### Р7. Багатозадачність і спільний стан (6)
1. ref:programming/tasks — ДОДАТИ: mk/super-loop-limits підвів — тут відповідь
2. ref:programming/scheduler — ДОДАТИ
3. ref:programming/freertos — ДОДАТИ: конкретика, на якій стоять усі приклади ESP32
4. ref:programming/atomicity-races — ДОДАТИ: без поняття гонки м'ютекс не мотивований
5. ref:programming/task-ipc — ДОДАТИ: черги й семафори — те, з чим порівнюється спінлок
6. own:spinlock-mutex

### Р8. Тестування й надійність (5)
1. own:firmware-testing (після коду, перед fatfs — обидва обмеження виконано)
2. ref:programming/static-analysis — ДОДАТИ: баги без запуску; природне продовження тестів
3. own:fault-injection-testing (move_in із mk — навмисно ламаємо, щоб перевірити стійкість)
4. ref:programming/watchdog — ДОДАТИ: головний примітив живучості прошивки; у курсі його нема
5. own:fmea-embedded (системний рівень — вінчає розділ)

### Р9. Прикладні підсистеми: файли й індикація (4)
1. ref:electronics/sd-card — ДОДАТИ: носій, на який пише FatFs
2. ref:programming/flash-filesystems — ДОДАТИ: що таке файлова система і чому FAT
3. own:fatfs-integration (спирається на firmware-testing ✓ Р8 і м'ютекси ✓ Р7)
4. own:led-animation-patterns (прикладний модуль-патерн; PWM ✓ zhyvlennia, неблокуючий код ✓ mk)

### Р10. Випуск, оновлення й довіра (6)
1. ref:programming/version-control — ДОДАТИ: git із нуля перед стратегіями гілкування
   (у книзі basic поки pending — єдиний не-done ref у плані)
2. own:gitflow-branching
3. ref:programming/ota-update — ДОДАТИ: клієнтський бік OTA; без нього ota-server висить у повітрі
4. own:ota-server (move_in із mk)
5. ref:programming/secure-boot — ДОДАТИ: tpm-trustzone ПРЯМО каже «ми вже навчилися підписувати»
6. own:tpm-trustzone (фінал: апаратний корінь довіри)

Разом: 55 кроків, 10 розділів по 4–9. Баланс ref/own: 26 ref (усі, крім version-control, — done)
проти 29 own-кроків (з урахуванням move_in).

## 4. move_out / move_in

**move_out (1):**
- own:calibration-procedure → davachi: «Процедура калібрування давача» до того, як курс подав
  давачі, — читати нема на чому. У davachi стане поруч із error-budget-ranging після конкретних
  давачів; ref:electronics/calibration у Р3 лишає тут загальний місток.

**move_in (8, усі з mk):**
- own:esptool-workflow — «прошивання й читання Flash» — буквально ім'я цього модуля; у mk губився
  серед архітектури процесора.
- own:jtag-swd-tools — дебаг-проби: ядро «відлагодження», якого модуль-тезка не мав.
- own:openocd-gdb — тс.
- own:core-dump — його продовження addr2line-workflow уже тут; пару розірвано між секціями.
- own:debug-io-comparison — порівняння каналів налагоджувального виводу.
- own:fault-injection-testing — тестування відмовостійкості: до розділу тестування, поруч із FMEA.
- own:current-profiler-tools — профайлери струму після базового measure-consumption
  (у mk стояв РАНІШЕ за базу; і дублює тутешні вставки).
- own:ota-server — серверний бік оновлень: до розділу випуску, після клієнтського OTA.

Примітка: mk/power-logger лишаю в mk (це «побудувати пристрій-логер»), але він на межі
й дублює proj-coulomb-counter.md із measure-consumption — злити вставки.

## 5. Прогалини (усі перевірені по маніфестах книг; усі закриваються готовими статтями)

Новачкові (тип а): multimeter, oscilloscope, measurement-errors, logic-analyzer (electronics/metrology);
counters (electronics), timer-counter, capture-compare (programming) — під frequency-measurement;
adc, adc-errors, voltage-reference, calibration (electronics) — під калібрування;
compilation, linking, firmware-image, bootloader (programming) — під esptool/addr2line;
addresses-pointers, assert-panic (programming) — під memory-safety/помилки;
tasks, scheduler, freertos, atomicity-races, task-ipc (programming) — під spinlock-mutex;
version-control (programming, basic pending) — під gitflow; sd-card (electronics),
flash-filesystems (programming) — під FatFs; secure-boot (programming) — під tpm-trustzone.

Повне покриття теми модуля (тип б): static-analysis, watchdog, ota-update (programming).
Не вставляв, але вартує згадки: CI для embedded (статті в книгах нема — кандидат new:ci-for-embedded),
semihosting/RTT/trace-itm-swo (є done-статті в programming — хай лишаться попап-лінками
з debug-io-comparison, кроки не обов'язкові).

## 6. Органічність ref/own

- Власні статті модуля якісні й уплетені (sine-on-scope, fatfs, frequency-measurement активно
  лінкують book:/guide: у прозі). Це добрий зразок.
- Але модуль (і весь курс) має **нуль ref:programming** — усе програмне курс або винаходить
  own-статтями в mk, або просто пропускає. Тулчейн/RTOS/OTA/secure-boot закриваються готовими
  ref-ами — власні статті тут не потрібні.
- Ризик «стіни ref-ів»: Р7 (5 ref поспіль + 1 own). Якщо це неприйнятно за стилем курсу —
  альтернатива: перенести RTOS-блок у mk одразу після super-loop-limits (там його природне
  місце в розповіді), а тут лишити atomicity-races → spinlock-mutex; або написати одну власну
  статтю-зшивку «RTOS для нашого курсу». Р4 (4 ref + 2 own) — на межі, але ланцюг
  «компіляція→лінк→образ→bootloader» сам собою є ниткою.

## 7. Модуль як ціле

- Назва «Прошивка й відлагодження» покриває Р4–Р10; Р1–Р3 — це «стенд і вимірювання».
  Чесніше або розбити на ДВА модулі: «Стенд: прилади й вимірювання» (Р1–Р3, ~18 кроків)
  і «Прошивка: від коду до випуску» (Р4–Р10, ~37 кроків), або перейменувати на
  «Стенд, прошивка й відлагодження». 55 кроків для одного модуля — забагато, розбиття краще.
- Місце в курсі: після mk і peryferiia — правильне для програмної частини (Р4+).
  Приладова частина (Р1) обґрунтовано могла б стояти НАБАГАТО раніше — одразу після kola,
  бо мультиметр і осцилограф потрібні вже під час перших схем; якщо колись буде глобальна
  перестановка — Р1 кандидат на переїзд у район секцій 2–3.
- Дублікати вставок між mk і proshyvka (proj-coulomb-counter.md ×2, comp-current-profiler ≈
  comp-power-profiler-instruments) — злити при переносі current-profiler-tools.
- Взаємодія з давачами: калібрування розрізано свідомо — загальне (Р3) тут,
  процедура калібрування давача — у davachi (move_out).
