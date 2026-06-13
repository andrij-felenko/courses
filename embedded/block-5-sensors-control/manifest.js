/* embedded/block-5-sensors-control/manifest.js — per-module маніфест Модуля 5. Складає scripts/bookbuild.js
   (histories[]/extras[] ВИВОДЯТЬСЯ з topics[]). Нумерація — М.Р.Т. */
(window.__MODREG__ = window.__MODREG__ || []).push({
  n: 5, slug: "block-5-sensors-control", title: "Давачі, сигнали й керування",
  chapters: [
    { n: 1, title: "Фізика давачів", dir: "block-5-sensors-control/sensor-physics", main: "sensor-physics.md", status: "done",
      scope: "Перетворювач фізичної величини в електричний сигнал; класи перетворювачів; чутливість, лінійність, дрейф, гістерезис, калібрування; вимірювання струму й напруги.",
      topics: [
        { mrt: "5.1.1", title: "Що таке давач: фізична величина → електричний сигнал", status: "done" },
        { mrt: "5.1.2", title: "Класи перетворювачів: резистивні, ємнісні, індуктивні", status: "done" },
        { mrt: "5.1.3", title: "П'єзо-, оптичні, напівпровідникові", status: "done" },
        { mrt: "5.1.4", title: "Характеристики: чутливість, лінійність, діапазон", status: "done" },
        { mrt: "5.1.5", title: "Дрейф, гістерезис, шум", status: "done" },
        { mrt: "5.1.6", title: "Калібрування: від сирого сигналу до величини", status: "done" },
        { mrt: "5.1.7", title: "Узгодження давача з входом", status: "done" },
        { mrt: "5.1.8", title: "Вимірювання струму й напруги в системі: шунт, Холл, дільник", status: "empty" },
        { mrt: "5.1.9", title: "Тензодавачі й вимірювання ваги", status: "empty" },
        { mrt: "5.1.10", title: "Мікрофон і динамік", status: "empty" },
        { kind: "hist", file: "hist-seebeck.md", at: "chapter", status: "done", title: "Ефект Зеебека й термопара (1821)" },
        { kind: "hist", file: "hist-strain-gauge.md", at: "5.1.9", status: "done", title: "Тензорезистор двічі: Сіммонс і Руге (1938)" }
      ] },
    { n: 2, title: "Вимірювання відстані й оточення", dir: "block-5-sensors-control/distance-environment", main: "distance-environment.md", status: "done",
      scope: "Принципи вимірювання відстані: час польоту (звук/світло), тріангуляція, відбиття/поглинання; джерела похибки й межі точності.",
      topics: [
        { mrt: "5.2.1", title: "Як виміряти відстань без дотику", status: "done" },
        { mrt: "5.2.2", title: "Час польоту (ToF): звук", status: "done" },
        { mrt: "5.2.3", title: "Час польоту: світло/лазер", status: "done" },
        { mrt: "5.2.4", title: "Тріангуляція", status: "done" },
        { mrt: "5.2.5", title: "Відбиття й поглинання: IR-перешкода, вплив освітленості", status: "done" },
        { mrt: "5.2.6", title: "Похибки вимірювання відстані", status: "done" },
        { mrt: "5.2.7", title: "Інші давачі оточення: рух (PIR), температура/вологість, газ", status: "done" },
        { kind: "hist", file: "hist-sonar.md", at: "chapter", status: "done", title: "Як навчилися «бачити» відлунням: від кажанів до сонара" }
      ] },
    { n: 3, title: "Давачі обертання й положення: енкодери", status: "empty",
      scope: "Потенціометр як давач кута; оптичний інкрементальний енкодер; квадратура A/B; датчики Холла й магнітні енкодери; абсолютні енкодери й код Грея; одометрія та її дрейф.",
      topics: [
        { mrt: "5.3.1", title: "Навіщо міряти кут і оберти", status: "empty" },
        { mrt: "5.3.2", title: "Потенціометр як давач кута (і його межі)", status: "empty" },
        { mrt: "5.3.3", title: "Оптичний інкрементальний енкодер: диск, фотопара, імпульси", status: "empty" },
        { mrt: "5.3.4", title: "Квадратура: напрямок із двох каналів (A/B; ×4 роздільність)", status: "empty" },
        { mrt: "5.3.5", title: "Датчики Холла й магнітні енкодери", status: "empty" },
        { mrt: "5.3.6", title: "Абсолютний vs інкрементальний (код Грея)", status: "empty" },
        { mrt: "5.3.7", title: "Одометрія: від тіків до шляху (і чому вона «пливе»)", status: "empty" }
      ] },
    { n: 4, title: "Цифрова фільтрація сигналів", dir: "block-5-sensors-control/digital-filtering", main: "digital-filtering.md", status: "done",
      scope: "Шум і викиди; ковзне середнє, медіана, експоненційне згладжування — з формулами й межами; компроміс згладжування/затримка.",
      topics: [
        { mrt: "5.4.1", title: "Шум у сигналі: чому давачі «брешуть»", status: "done" },
        { mrt: "5.4.2", title: "Ковзне середнє", status: "done" },
        { mrt: "5.4.3", title: "Медіанний фільтр", status: "done" },
        { mrt: "5.4.4", title: "Експоненційне згладжування (EMA)", status: "done" },
        { mrt: "5.4.5", title: "Компроміс згладжування ↔ затримка", status: "done" },
        { mrt: "5.4.6", title: "Який фільтр коли", status: "done" }
      ] },
    { n: 5, title: "Спектр і перетворення Фур'є", dir: "block-5-sensors-control/spectrum-fourier", main: "spectrum-fourier.md", status: "done",
      scope: "Сигнал у часі й частоті; ідея ДПФ/ШПФ на пальцях; навіщо частотна область; вікно й витік спектра.",
      topics: [
        { mrt: "5.5.1", title: "Сигнал у часі й частоті: дві мови", status: "done" },
        { mrt: "5.5.2", title: "Ідея Фур'є: будь-який сигнал = сума синусоїд", status: "done" },
        { mrt: "5.5.3", title: "Спектр: що він показує", status: "done" },
        { mrt: "5.5.4", title: "Дискретне перетворення Фур'є (ДПФ)", status: "done" },
        { mrt: "5.5.5", title: "Швидке перетворення Фур'є (ШПФ/FFT)", status: "done" },
        { mrt: "5.5.6", title: "Вікно й витік спектра", status: "done" },
        { mrt: "5.5.7", title: "Навіщо частотна область", status: "done" },
        { kind: "hist", file: "hist-fourier.md", at: "chapter", status: "done", title: "Фур'є й рівняння теплоти (1807)" },
        { kind: "hist", file: "hist-fft.md", at: "5.5.5", status: "done", title: "ШПФ: Кулі й Тьюкі (1965)" }
      ] },
    { n: 6, title: "Цифрові фільтри в мікроконтролері", dir: "block-5-sensors-control/digital-filters-mcu", main: "digital-filters-mcu.md", status: "done",
      scope: "КІХ та БІХ інтуїтивно; смугові фільтри; реалізація з фіксованою комою; обмеження обчислень у реальному часі.",
      topics: [
        { mrt: "5.6.1", title: "Фільтр як «формувач спектра»", status: "done" },
        { mrt: "5.6.2", title: "КІХ-фільтр (FIR): скінченна пам'ять", status: "done" },
        { mrt: "5.6.3", title: "БІХ-фільтр (IIR): зворотний зв'язок", status: "done" },
        { mrt: "5.6.4", title: "Смугові фільтри: НЧ, ВЧ, смуговий", status: "done" },
        { mrt: "5.6.5", title: "Реалізація на МК: fixed-point і швидкодія", status: "done" },
        { mrt: "5.6.6", title: "КІХ vs БІХ: коли що", status: "done" }
      ] },
    { n: 7, title: "Інерціальні давачі: MEMS", dir: "block-5-sensors-control/imu-mems", main: "imu-mems.md", status: "done",
      scope: "Як мікромеханіка міряє прискорення (ємнісні гребінки) і кутову швидкість (Коріоліс); шум, зсув нуля, температурний дрейф; межі кожного давача.",
      topics: [
        { mrt: "5.7.1", title: "MEMS: машини розміром із порошинку", status: "done" },
        { mrt: "5.7.2", title: "Акселерометр: міряти прискорення", status: "done" },
        { mrt: "5.7.3", title: "Гіроскоп: міряти обертання", status: "done" },
        { mrt: "5.7.4", title: "Магнітометр: відчути сторони світу", status: "done" },
        { mrt: "5.7.5", title: "Шум, зсув нуля, дрейф", status: "done" },
        { mrt: "5.7.6", title: "Чому потрібен фьюжн", status: "done" },
        { mrt: "5.7.7", title: "Читання IMU: data-ready і FIFO", status: "empty" },
        { mrt: "5.7.8", title: "Вібрації й механічна розв'язка IMU", status: "empty" },
        { mrt: "5.7.9", title: "Калібрування IMU й магнітометра", status: "empty" },
        { kind: "hist", file: "hist-mems-airbag.md", at: "chapter", status: "done", title: "MEMS: як подушки безпеки зробили акселерометр масовим" }
      ] },
    { n: 8, title: "Орієнтація й керування зі зворотним зв'язком (ПІД)", dir: "block-5-sensors-control/orientation-pid", main: "orientation-pid.md", status: "done",
      scope: "Кути Ейлера проти кватерніонів; комплементарний фільтр; ідея фільтра Калмана; ПІД-регулятор (P/I/D, стійкість), дискретний ПІД (anti-windup, фільтр похідної), каскадні контури.",
      topics: [
        { mrt: "5.8.1", title: "Орієнтація в просторі: кути Ейлера", status: "done" },
        { mrt: "5.8.2", title: "Кватерніони: чому з ними зручніше", status: "done" },
        { mrt: "5.8.3", title: "Комплементарний фільтр", status: "done" },
        { mrt: "5.8.4", title: "Ідея фільтра Калмана", status: "done" },
        { mrt: "5.8.5", title: "Зворотний зв'язок: розімкнене vs замкнене керування", status: "done" },
        { mrt: "5.8.6", title: "Пропорційний регулятор (P)", status: "done" },
        { mrt: "5.8.7", title: "Інтегральна складова (I)", status: "done" },
        { mrt: "5.8.8", title: "Диференційна складова (D)", status: "done" },
        { mrt: "5.8.9", title: "Дискретний ПІД на МК", status: "done" },
        { mrt: "5.8.10", title: "Налаштування й каскадні контури", status: "done" },
        { mrt: "5.8.11", title: "Чому контур збуджується: затримка, підсилення і запас стійкості", status: "empty" },
        { mrt: "5.8.12", title: "Пізнати об'єкт: крокова відповідь, стала часу й запізнення", status: "empty" },
        { mrt: "5.8.13", title: "Феєдфорвард: не чекати на помилку", status: "empty" },
        { kind: "hist", file: "hist-governor-pid.md", at: "chapter", status: "done", title: "Від відцентрового регулятора Уатта до ПІД" },
        { kind: "hist", file: "hist-kalman.md", at: "5.8.4", status: "done", title: "Фільтр Калмана й «Аполлон»" }
      ] },
    { n: 9, title: "Виконавчі механізми: мотори й рух", status: "empty",
      scope: "Щітковий DC-мотор, H-міст, кроковий мотор і драйвер, hobby-серво, соленоїд/вібромотор, струм заклинювання й нагрів, редуктори, вибір актуатора.",
      topics: [
        { mrt: "5.9.1", title: "Щітковий DC-мотор: момент зі струму", status: "empty" },
        { mrt: "5.9.2", title: "H-міст застосовно: напрямок, швидкість, гальмо", status: "empty" },
        { mrt: "5.9.3", title: "Кроковий мотор і його драйвер", status: "empty" },
        { mrt: "5.9.4", title: "Hobby-серво зсередини", status: "empty" },
        { mrt: "5.9.5", title: "Соленоїд, вібромотор, п'єзо-актуатор", status: "empty" },
        { mrt: "5.9.6", title: "Струм, заклинювання, нагрів", status: "empty" },
        { mrt: "5.9.7", title: "Редуктори й передачі: момент ↔ оберти", status: "empty" },
        { mrt: "5.9.8", title: "Вибір актуатора під задачу", status: "empty" },
        { mrt: "5.9.9", title: "Профілі руху: трапеція, S-крива й синхронні осі", status: "empty" }
      ] },
    { n: 10, title: "Давачі середовища глибше", status: "empty",
      scope: "Газові давачі MOX, NDIR-CO₂, електрохімічні комірки, пил і аерозолі, УФ/освітленість, лічильник Гейгера, барометр-альтиметр, перехресна чутливість і компенсація.",
      topics: [
        { mrt: "5.10.1", title: "Газові давачі MOX: оксид металу й нагрівач", status: "empty" },
        { mrt: "5.10.2", title: "NDIR: CO₂ за поглинанням інфрачервоного", status: "empty" },
        { mrt: "5.10.3", title: "Електрохімічні комірки: CO й токсичні гази", status: "empty" },
        { mrt: "5.10.4", title: "Пил і аерозолі: розсіювання світла", status: "empty" },
        { mrt: "5.10.5", title: "УФ та освітленість: фотодіоди зі спектральними фільтрами", status: "empty" },
        { mrt: "5.10.6", title: "Іонізуюче випромінювання: лічильник Гейгера—Мюллера", status: "empty" },
        { mrt: "5.10.7", title: "Тиск і висота: барометр як альтиметр", status: "empty" },
        { mrt: "5.10.8", title: "Перехресна чутливість і компенсація", status: "empty" }
      ] },
    { n: 11, title: "Час і синхронізація вимірювань", status: "empty",
      scope: "Час вимірювання як частина вимірювання; мітки часу; джиттер вибірки; синхронні зчитування; PPS як еталон; зсув/дрейф годинників між платами; компенсація затримки давача у фьюжні.",
      topics: [
        { mrt: "5.11.1", title: "Час вимірювання — частина вимірювання", status: "empty" },
        { mrt: "5.11.2", title: "Мітки часу: коли саме зроблено вимір", status: "empty" },
        { mrt: "5.11.3", title: "Джиттер вибірки і його ціна", status: "empty" },
        { mrt: "5.11.4", title: "Синхронні зчитування кількох давачів", status: "empty" },
        { mrt: "5.11.5", title: "PPS: секундний імпульс як еталон", status: "empty" },
        { mrt: "5.11.6", title: "Зсув і дрейф годинників між платами", status: "empty" },
        { mrt: "5.11.7", title: "Затримка давача й компенсація у фьюжні", status: "empty" }
      ] }
  ]
});
