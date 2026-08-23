# Аналіз модуля «napivprovidnyky» — «Напівпровідники й діоди»

Курс: guide/embedded («Вбудована електроніка й автономні системи»), секція №4 з 14.
Поточний склад: 7 тем (1 ref + 6 own).

## 1. Поточний стан модуля

| # | Крок | Вид | Що це насправді |
|---|------|-----|-----------------|
| 1 | ref:electronics/esd-damage «Електростатичний розряд» | ref | чому статика вбиває чіпи (затворний оксид MOSFET) |
| 2 | own:diodes «Діоди» | own | ПРАКТИКУМ родин діодів: 1N4148/1N400x/Шотткі — «що коли брати» |
| 3 | own:nor-vs-nand «NOR і NAND» | own | дві архітектури ФЛЕШ-пам'яті |
| 4 | own:eeprom-fram «EEPROM і FRAM» | own | технології нелеткої пам'яті |
| 5 | own:sic-gan-comparison «SiC і GaN» | own | широкозонні матеріали проти кремнію |
| 6 | own:mram-rram-pcm «MRAM, RRAM і PCM» | own | нові нелеткі пам'яті |
| 7 | own:power-fail-safety «Захист від зникнення живлення» | own | brown-out МК + рятування стану в EEPROM/FRAM |

**Головний діагноз.** Модуль називається «Напівпровідники й діоди», але напівпровідників у ньому нема: жодного кроку про те, що таке напівпровідник, легування, p-n перехід, і жодного про транзистор. Натомість 4 з 7 тем — це технології **пам'яті** (флеш, EEPROM/FRAM, MRAM/RRAM/PCM, рятування стану), які тематично належать сусідній секції «Цифра й памʼять» (cyfra-pamyat). Модуль — фактично «зіпсований ярлик»: під вивіскою приладової фізики живе блок про сховища даних.

Перевірено за текстами (перші ~40 рядків, лише неоднозначні):
- `diodes.md` — перший абзац прямо посилається на `root:embedded/zener-schottky` («Те, чим звичайний діод відрізняється від Зенера й Шотткі за фізикою, — лише півсправи») і на `book:physics/pn-junction`. Тобто «Діоди» — це НЕ вступ у діоди, а практикум вибору типономіналів, який ПРИПУСКАЄ вже пройдені зенер/Шотткі та p-n перехід.
- `zener-schottky.md` (живе в komponenty, §3) — відкривається «Звичайний PN-діод — лише один із сімейства» і посилається на `book:electronics/diode-iv-curve` (пробій). Припускає знання звичайного діода і його ВАХ — яких у курсі ніде до того нема.
- `nor-vs-nand.md` — «Кожна комірка флеші — це транзистор», посилається на `root:embedded/memory-cell-physics` (плаваючий затвор; крок секції osnovy №1!), на логічні вентилі NAND/NOR, на DRAM і на `root:embedded/choosing-memory` (cyfra-pamyat).
- `power-fail-safety.md` — відкривається посиланням на `root:embedded/eeprom-fram`; пояснює brown-out detector МК, посилається на `book:electronics/comparator`; аргументація через пороги затворів транзисторів у логічних вентилях.

## 2. Порушення порядку (конкретно)

1. **esd-damage стоїть ПЕРШИМ кроком модуля, перед diodes** — а стаття пояснює пошкодження затворного оксиду і p-n структур; на цю мить курсу читач не бачив ані p-n переходу, ані MOSFET (MOSFET як пояснювальної теми в курсі нема ВЗАГАЛІ). Фізичні передумови (трибоелектрика, пробій повітря) в osnovy є — але приладових нема жодної.
2. **own:diodes вимагає zener-schottky і pn-junction, яких на його місці нема**: zener-schottky живе в іншій секції (komponenty, §3 — формально раніше, але це сам по собі злам: «особливі діоди» подано серед пасивних компонентів ДО того, як пояснено звичайний діод), а physics/pn-junction не є кроком курсу ніде.
3. **nor-vs-nand стоїть одразу після diodes, хоча вимагає**: (а) MOSFET із плаваючим затвором — транзисторів у курсі ще не було; (б) логічних вентилів NAND/NOR — цифрова логіка з'являється лише в cyfra-pamyat (§5); (в) DRAM — ніде в курсі; (г) memory-cell-physics — крок секції osnovy (§1), де він сам стоїть абсурдно рано.
4. **eeprom-fram** — та сама діра: тунелювання крізь оксид, сегнетоелектрична комірка — без транзисторної бази; тема про технологію пам'яті, не про напівпровідники.
5. **mram-rram-pcm** — порівняльна тема «нових пам'ятей»; коректно стоїть після nor-vs-nand/eeprom-fram, але весь блок не звідси.
6. **power-fail-safety вимагає мікроконтролера** (brown-out detector — вузол МК, реакція — прошивка) і компаратора; МК з'являється в §7 (mk), компаратор у курсі окремим кроком не подано. Стоїть за три секції до МК.
7. **sic-gan-comparison стоїть після блоку пам'ятей**, хоча це матеріалознавча тема про транзистори й діоди (SiC MOSFET, GaN HEMT) — вимагає розуміння MOSFET, якого нема, і логічно живе біля фабрикації/матеріалів, а не між EEPROM і MRAM.
8. **Глобальний злам довкола модуля**: секції, що СТОЯТЬ РАНІШЕ, вже вовсю користуються напівпровідниковими приладами — kola (§2): bjt-load-driving, bjt-vs-mosfet, darlington-vs-sziklai, multistage-amplifier, ОП-теми; komponenty (§3): zener-schottky, flyback-protection, datasheet-bjt, surge-protection-cascade. Тобто читач «водить» транзистори й зенери за дві секції до того, як дізнається про існування p-n переходу.

## 3. Задум перебудови

Зробити з модуля те, що обіцяє назва: **приладовий модуль** — від фізики кристала до готового чіпа. Пам'яті віддати cyfra-pamyat (сусідня секція, там уже живуть when-memory-runs-out і choosing-memory, а nor-vs-nand сам посилається на choosing-memory). Втягнути сюди приладові теми, що заблукали в kola/komponenty (zener-schottky, bjt-vs-mosfet, bjt-load-driving). Прогалини закрити ref-ами: у предметних книгах уже Є ГОТОВІ (basic: done) статті майже на все — physics/semiconductor, doping, pn-junction; electronics/bjt-structure, bjt, mosfet-structure, mosfet-threshold, nmos-pmos, body-diode, cmos, silicon-monocrystal, photolithography, doping-etching-metal, process-node, ic-invention, diode-bias, diode-iv-curve, led-photodiode, optocoupler, tvs-diode. Лише два ref-и в книгах ще pending: physics/avalanche-breakdown, (опційний physics/holes-carriers — не включаю, бо його зміст покриють semiconductor+doping).

### Розділи (5 розділів, 28 кроків)

**Розділ 1. Кристал і перехід: фізика напівпровідника (4)**
1. ref:physics/conductors-insulators «Провідники й діелектрики» — ДОДАТИ: місток від «природи опору» (osnovy) до класифікації матеріалів; готова (done).
2. ref:physics/semiconductor «Напівпровідник» — ДОДАТИ: що таке напівпровідник, електрони й дірки; done.
3. ref:physics/doping «Легування» — ДОДАТИ: n- і p-тип; done.
4. ref:physics/pn-junction «PN-перехід» — ДОДАТИ: збіднена область, вбудований потенціал; на нього ВЖЕ посилаються diodes.md і zener-schottky.md; done.

**Розділ 2. Діод і його родина (6)**
1. ref:electronics/diode-bias «Зміщення діода» — ДОДАТИ: пряме/зворотне зміщення, «вентиль»; done.
2. ref:electronics/diode-iv-curve «ВАХ діода» — ДОДАТИ: коліно 0.6–0.7 В, пробій; zener-schottky.md посилається саме сюди; done.
3. ref:physics/avalanche-breakdown «Лавинний пробій і тунелювання Зенера» — ДОДАТИ: фізика керованого пробою перед зенером (у книзі pending — треба написати).
4. own:zener-schottky «Діоди Зенера» — MOVE_IN з komponenty: тепер усі його передумови (звичайний діод, ВАХ, пробій) стоять просто перед ним.
5. own:diodes «Діоди» — лишається; тепер його посилання (zener-schottky, pn-junction) справді пройдені; практикум-замикач розділу.
6. ref:electronics/led-photodiode «Світлодіод» — ДОДАТИ: діод, що світиться, + фотодіод; курс миготить LED-ами з перших проєктів і будує на фотодіодах LiDAR/камери (davachi, drony), але ніде їх не вводить; done.

**Розділ 3. Транзистори: BJT і MOSFET (8)** — найбільша прогалина всього курсу
1. ref:electronics/bjt-structure «Будова BJT» — ДОДАТИ: два p-n переходи, npn/pnp; done.
2. ref:electronics/bjt «BJT-транзистори» — ДОДАТИ: підсилення струму, ключ; done.
3. ref:electronics/mosfet-structure «Будова MOSFET» — ДОДАТИ: затвор, канал, оксид; done.
4. ref:electronics/mosfet-threshold «Поріг MOSFET» — ДОДАТИ: Vth, увімкнення полем; done.
5. ref:electronics/nmos-pmos «NMOS/PMOS» — ДОДАТИ: два знаки каналу; done.
6. ref:electronics/body-diode «Body-діод» — ДОДАТИ: зшиває MOSFET із розділом про діоди; критично для zhyvlennia (reverse-polarity, ideal diode); done.
7. own:bjt-vs-mosfet «BJT проти MOSFET» — MOVE_IN з kola: порівняння приладів — приладова тема; в kola стояла ДО будь-якого пояснення транзисторів.
8. own:bjt-load-driving «BJT: навантаження» — MOVE_IN з kola: перший практичний транзисторний ключ (реле, LED) — природний замикач розділу; в kola (§2) стояла до введення транзисторів узагалі.

**Розділ 4. Від транзистора до чіпа (7)**
1. ref:electronics/cmos «CMOS» — ДОДАТИ: пара NMOS+PMOS → інвертор; місток до cyfra-pamyat; done.
2. ref:electronics/ic-invention «Винайдення інтегральної схеми» — ДОДАТИ: навіщо інтегрувати (Кілбі/Нойс); done.
3. ref:electronics/silicon-monocrystal «Кремній і монокристал» — ДОДАТИ: звідки береться пластина; done.
4. ref:electronics/photolithography «Фотолітографія» — ДОДАТИ; done.
5. ref:electronics/doping-etching-metal «Шар за шаром» — ДОДАТИ: повний цикл шарів; done.
6. ref:electronics/process-node «Техпроцес» — ДОДАТИ: що значать «нанометри» в даташиті МК; done.
7. own:sic-gan-comparison «SiC і GaN» — лишається: матеріали поза кремнієм; тепер після MOSFET і фабрикації — на своєму місці.

**Розділ 5. Крихкий кристал: ESD і захист (3)**
1. ref:electronics/esd-damage «Електростатичний розряд» — лишається, але ПЕРЕНЕСЕНО з першої позиції в кінець: тепер читач знає затворний оксид (розд. 3–4), а трибоелектрику/пробій повітря дав osnovy.
2. ref:electronics/tvs-diode «TVS-діод» — ДОДАТИ: прилад-захисник від ESD; на нього спирається zhyvlennia/esd-protection-circuits (comp-tvs-array); done.
3. ref:electronics/optocoupler «Оптопара» — ДОДАТИ: LED+фототранзистор (потребує розд. 2 і 3), гальванічна розв'язка — знадобиться в живленні й АС-комутації; done.

Розділ 5 короткий (3 кроки) — свідомо: це епілог-«техніка безпеки» модуля; за бажання можна влити в розділ 4, але тоді той розпухає до 10 і мішає фабрикацію з захистом.

## 4. move_out (4 теми)

| Тема | Куди | Чому |
|------|------|------|
| own:nor-vs-nand | cyfra-pamyat | технологія пам'яті; сама посилається на memory-cell-physics, логічні вентилі, DRAM і choosing-memory (усе — матерія cyfra-pamyat); межі секцій стають різкими: тут прилади — там біти |
| own:eeprom-fram | cyfra-pamyat | те саме: технологія нелеткої пам'яті, пара до nor-vs-nand, передує choosing-memory |
| own:mram-rram-pcm | cyfra-pamyat | «нові пам'яті» — порівняльний хвіст блоку пам'ятей; іде слідом за nor-vs-nand/eeprom-fram |
| own:power-fail-safety | cyfra-pamyat | капстоун блоку пам'ятей («рятування стану в нелетку пам'ять»); відкривається посиланням на eeprom-fram — має стояти одразу після нього; альтернативний адресат — proshyvka (прошивочна половина теми), але розривати блок гірше |

Разом із цим (поза моїми повноваженнями, для аналітиків osnovy/cyfra-pamyat): **osnovy/memory-cell-physics «Фізика комірок»** стоїть у секції №1 — до транзисторів і цифри — а на неї посилається nor-vs-nand; їй місце на початку блоку пам'ятей у cyfra-pamyat.

## 5. move_in (3 теми)

| Тема | Звідки | Чому |
|------|--------|------|
| own:zener-schottky «Діоди Зенера» | komponenty | зенер/Шотткі — напівпровідникові прилади, а не «пасивні компоненти»; у komponenty стояли ДО пояснення звичайного діода; тут стають між ВАХ/пробоєм і практикумом diodes, який на них посилається |
| own:bjt-vs-mosfet «BJT проти MOSFET» | kola | порівняння двох приладів — приладова тема; в kola (§2) стояла до того, як курс узагалі пояснив, що таке транзистор |
| own:bjt-load-driving «BJT: навантаження» | kola | перший практичний ключ (реле/LED через транзистор) — природний вихід із розділу про транзистори; в kola стояла без жодної транзисторної бази |

Файли move_in-тем фізично лежать у guide/embedded/komponenty/... і guide/embedded/kola/... — при переносі треба git mv тек (і оновити внутрішні guide:-посилання не треба — вони за slug, але шляхи картинок у md прив'язані до секції: перевірити).

## 6. Прогалини (missing) — усі закриваються готовими статтями книг

Новачкові, щоб пройти модуль без стіни незнаного: conductors-insulators → semiconductor → doping → pn-junction → diode-bias → diode-iv-curve (це буквально ланцюг передумов, на який уже посилаються власні статті курсу). Для повноти теми модуля: транзистори (bjt-structure, bjt, mosfet-structure, mosfet-threshold, nmos-pmos, body-diode), CMOS і фабрикація (ic-invention, silicon-monocrystal, photolithography, doping-etching-metal, process-node), оптоелектроніка (led-photodiode, optocoupler), захист (tvs-diode), фізика пробою (avalanche-breakdown — єдиний pending у книзі).

Свідомо НЕ додаю: тиристор/симістор/IGBT (electronics/thyristor-scr, triac, igbt — done) — їх вводить zhyvlennia/ac-switch-need там, де вони потрібні; дублювати тут не варто. physics/holes-carriers (pending) — дірки покриють semiconductor+doping. Варистор — керамічний прилад, лишається в темі каскадного захисту komponenty.

## 7. Органічність ref/own

- Зараз модуль — 6 own + 1 ref, і єдиний ref (esd-damage) стоїть не на місці. Після перебудови — ~21 ref + 7 own (з move_in). Розділи 1 і 4 — ланцюжки ref-ів (4 і 6 поспіль) без own-прошарку: прийнятно, бо це самодостатні фізичні/фабрикаційні атоми, а наративні вузли модуля тримають own-статті (zener-schottky → diodes у розд. 2; bjt-vs-mosfet → bjt-load-driving у розд. 3; sic-gan у розд. 4). Якщо колись захочеться «нитки», просити не нову статтю, а 1–2-абзацні вступи розділів.
- Зворотний випадок (ref там, де треба own) — не знайдено; навпаки, own-статті блоку пам'ятей чудово написані кумулятивно і саме тому мусять переїхати ТУДИ, куди ведуть їхні власні посилання (cyfra-pamyat).

## 8. Модуль як ціле

- **Назва.** «Напівпровідники й діоди» після перебудови тісна: модуль покриває діоди, транзистори, CMOS і фабрикацію. Пропозиція: **«Напівпровідники: від p-n переходу до чіпа»** (або «Напівпровідникові прилади»).
- **Місце в курсі.** Позиція №4 (після osnovy → kola → komponenty) правильна за передумовами (діодам/транзисторам потрібні закон Ома, дільники, KCL/KVL, RC), АЛЕ тоді kola і komponenty мусять віддати свої напівпровідникові теми: мої move_in забирають zener-schottky, bjt-vs-mosfet, bjt-load-driving; решта активної аналоговки kola (multistage-amplifier, darlington-vs-sziklai, tail-current-source, single-supply-opamp, opamp-input-types, feedback-topologies, dc-ac-bias, kcl-opamp-analysis) має стати окремим модулем «Аналогові схеми: транзистор і ОП» ПІСЛЯ цього модуля — це поза моєю секцією, але без цього злам лишиться. Так само komponenty/datasheet-bjt і surge-protection-cascade мають опинитися після напівпровідників.
- **Не ділити й не зливати.** 5 розділів / 28 кроків — один зв'язний модуль (фізика → діод → транзистор → чіп → захист). Зливати з cyfra-pamyat не можна — саме розділення «прилади ↔ біти» лікує розмиті межі, на які скаржиться користувач.
- **Ефект для сусідів.** Після цієї перебудови cyfra-pamyat отримує цілісний блок пам'ятей (memory-cell-physics з osnovy + nor-vs-nand + eeprom-fram + mram-rram-pcm + power-fail-safety + наявні when-memory-runs-out/choosing-memory) — його аналітику варто зібрати з них розділ «Нелетка пам'ять».
