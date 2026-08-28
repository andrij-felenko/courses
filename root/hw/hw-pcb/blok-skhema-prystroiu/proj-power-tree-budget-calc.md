# ⚙️ Розрахунок дерева живлення, ККД перетворювачів та теплового балансу

Ручний розрахунок складної ієрархічної системи живлення з десятком споживачів, імпульсними перетворювачами різного ККД та лінійними стабілізаторами неминуче призводить до прихованих помилок у бюджеті струму: неврахування спадного ККД при малому навантаженні, недооцінка пікового струму первинного джерела під час холодного старту або катастрофічний тепловий перегрів LDO при максимальній температурі навколишнього середовища. Ця інженерна утиліта реалізує обхід графа дерева живлення (Power Tree Graph) знизу вгору (bottom-up propagation), обчислює статичний і динамічний струми кожного вузла, враховує нелінійну криву ефективності DC-DC перетворювачів, розраховує розсіювану теплову потужність кожного стабілізатора та верифікує температуру кристала за тепловим опором корпусу.

## Графова модель ієрархічного дерева живлення

Будь-яка система вторинного електроживлення друкованої плати моделюється як орієнтований кореневий граф-дерево G = (V, E), де множина вершин V представляє фізичні компоненти перетворення та споживання енергії, а множина ребер E — силові провідники та полігони живлення певної номінальної напруги.

У графовій моделі виділяють три типи вершин:

1. **Кореневе джерело (Root Source Node):** Вхідний роз'єм первинного живлення (зовнішній блок живлення 24 В, акумулятор або шина USB). Кореневий вузол не має вхідних ребер, але має вихідні ребра, що передають енергію первинним перетворювачам.
2. **Вузли перетворення (Converter Nodes):** Проміжні стабілізатори напруги — знижувальні перетворювачі (Buck), підвищувальні регулятори (Boost), лінійні стабілізатори з низьким спадом напруги (LDO) та гальванічно ізольовані DC-DC модулі. Кожен вузол перетворення має рівно одне вхідне ребро від джерела вищого рівня та одне або кілька вихідних ребер до споживачів нижчого рівня.
3. **Листові вузли навантаження (Leaf Load Nodes):** Кінцеві споживачі електричної енергії — обчислювальні ядра процесорів, мікросхеми оперативної та флеш-пам'яті, мережеві трансивери, буферні операційні підсилювачі, датчики, світлодіоди індикації та котушки реле. Листові вузли мають лише одне вхідне ребро живлення і не мають вихідних ребер.

```txt
[Первинне джерело 24V]
        │
        ▼
[DC-DC Buck (24V -> 5V)]
   ┌────┴───────────────────────────┬───────────────────────────────┐
   ▼                                ▼                               ▼
[DC-DC Buck (5V -> 3.3V)]   [DC-DC Buck (5V -> 1.2V)]    [LDO (5V -> 3.3V_ANA)]
   ├─► MCU I/O (120 мА)            └─► MCU Core (850 мА)          ├─► 24-bit ADC (15 мА)
   ├─► Flash QSPI (45 мА)                                         ├─► Op-Amps (25 мА)
   └─► Ethernet PHY (180 мА)                                      └─► VREF (5 мА)
```

Математичний розрахунок дерева живлення базується на фундаментальному законі збереження енергії: потужність, що входить у будь-який проміжний вузол перетворення, дорівнює сумі потужностей усіх підключених до нього споживачів плюс власна потужність теплових втрат перетворювача.

Розрахунок виконується у два зустрічні проходи:

- **Прямий прохід зверху вниз (Top-Down Voltage Propagation):** Перевіряється доступність і номінальний рівень напруги на кожному рівні ієрархії. Кожен перетворювач транслює на свій вихід задану стабілізовану напругу V_out.
- **Зворотний прохід знизу вгору (Bottom-Up Current Propagation):** Кожен листовий споживач декларує свій робочий струм I_load у різних режимах функціонування. Проміжний перетворювач підсумовує струми всіх своїх нащадків, визначає загальну вихідну потужність P_out, розраховує свій ККД η при даному навантаженні, обчислює споживану вхідну потужність P_in та вхідний струм I_in, який він споживає від батьківського вузла.

## Математичні моделі фізичних втрат та ККД перетворювачів

Точність оцінки бюджету живлення залежить від реалістичності моделей втрат для кожного типу перетворювача. Використання фіксованого ККД є грубою помилкою, оскільки ефективність реальних імпульсних стабілізаторів суттєво залежить від вихідного струму.

### 1. Лінійні стабілізатори з низьким спадом напруги (LDO)

Лінійний регулятор підтримує стабільну вихідну напругу за рахунок регулювання опору прохідного польового або біполярного транзистора, що працює в лінійному (активному) режимі. Струм навантаження I_out протікає безпосередньо від входу до виходу.

Вхідний струм LDO дорівнює сумі струму навантаження та власного струму споживання мікросхеми (Quiescent Current, I_q):

```txt
I_in = I_out + I_q
```

Оскільки струм споживання внутрішніх кіл керування I_q для сучасних LDO зазвичай становить від одиниць до сотень мікроамперів, при робочих струмах навантаження понад 10–50 мА ним часто можна знехтувати. Тоді ККД лінійного стабілізатора визначається виключно відношенням напруг:

```txt
η_LDO = (V_out · I_out) / (V_in · (I_out + I_q)) ≈ V_out / V_in
```

Розсіювана на кристалі LDO теплова потужність становить:

```txt
P_loss_LDO = (V_in - V_out) · I_out + V_in · I_q
```

Важливим фактором є температурна стабільність опору відкритого каналу польового транзистора регулятора. При нагріванні напівпровідника опір R_ds(on) зростає за формулою:

```txt
R_ds(T) = R_ds(25) · (1 + α · (T - 25))
```

де α ≈ 0.005–0.007 1/°C для кремнієвих MOSFET. Це означає, що при нагріванні кристала до +125 °C мінімально необхідне падіння напруги (Drop-Out Voltage) зростає на 50–70%, що може викликати передчасний вихід стабілізатора з режиму регулювання при просіданні вхідної напруги.

### 2. Імпульсні знижувальні та підвищувальні перетворювачі (Buck / Boost)

В імпульсних перетворювачах енергія передається порціями через індуктивний накопичувач за рахунок високочастотної комутації силових MOSFET-ключів. Втрати енергії в DC-DC конвертері складаються з чотирьох фундаментальних фізичних механізмів:

1. **Статичні втрати провідності (Conduction Losses):** Зумовлені протіканням струму через опір відкритого каналу верхнього транзистора R_ds_high, нижнього транзистора R_ds_low, активний опір постійного струму обмотки дроселя R_dcr та еквівалентний послідовний опір ESR вихідних конденсаторів:

```txt
P_cond = I_rms_high^2 · R_ds_high + I_rms_low^2 · R_ds_low + I_out^2 · R_dcr + I_ripple_rms^2 · ESR
```

де для знижувального перетворювача в режимі неперервного струму (CCM) середньоквадратичні значення струмів визначаються коефіцієнтом заповнення D = V_out / (V_in · η):

```txt
I_rms_high = I_out · √D
I_rms_low = I_out · √(1 - D)
```

2. **Динамічні комутаційні втрати (Switching Losses):** Виникають у моменти відкривання та закривання силових ключів, коли струм і напруга на транзисторі одночасно мають ненульові значення під час інтервалів наростання t_rise та спаду t_fall:

```txt
P_sw = 0.5 · V_in · I_out · (t_rise + t_fall) · f_sw
```

3. **Втрати на перезаряджання затворів та паразитних ємностей (Gate Charge Losses):** Енергія, яка витрачається внутрішнім драйвером контролера на заряд і розряд ємностей затворів силових транзисторів на кожному періоді комутації:

```txt
P_gate = (Q_g_high + Q_g_low) · V_gate · f_sw
```

4. **Втрати в магнітопроводі дроселя (Core Losses):** Зумовлені циклічним перемагнічуванням ферітового осердя (гістерезис) та вихровими струмами Фуко в матеріалі сердечника. Вони описуються емпіричним рівнянням Штейнметца:

```txt
P_core = k_fe · f_sw^α · B_pk^β · V_core
```

де B_pk — амплітуда змінної складової магнітної індукції в осерді, а α і β — коефіцієнти матеріалу (зазвичай α ≈ 1.2–1.8, β ≈ 2.0–2.6).

5. **Втрати мертвого часу та зворотного відновлення (Dead-Time & Reverse Recovery Losses):** Протягом інтервалу мертвого часу t_dead, який запобігає наскрізному струму через обидва транзистори, струм дроселя замикається через внутрішній антипаралельний діод нижнього MOSFET, що призводить до додаткового розсіювання потужності:

```txt
P_dead = V_body_diode · I_out · t_dead · f_sw + Q_rr · V_in · f_sw
```

Повна математична модель ККД імпульсного регулятора інтегрує всі перелічені складові:

```txt
η(I_out) = P_out / (P_out + P_cond(I_out) + P_sw(I_out) + P_gate + P_core + P_dead(I_out))
```

При малих струмах (I_out < 0.1 · I_max) домінують постійні втрати P_gate, P_core та власний струм мікросхеми, тому ККД падає. У діапазоні середніх струмів (40–80% від максимуму) перетворювач досягає пікового ККД (90–96%). При максимальних струмах ККД знову знижується через квадратичне зростання втрат провідності I_out^2 · R_ds.

## Теплове моделювання напівпровідникового кристала та друкованої плати

Кожен міліват електричних втрат P_loss перетворюється на теплову енергію, яка розігріває напівпровідниковий кристал мікросхеми. Для забезпечення довговічності та надійності роботи температура кристала T_j (Junction Temperature) не повинна перевищувати максимально допустимого значення, вказаного виробником (зазвичай +125 °C або +150 °C).

Тепловий потік від кристала в навколишній простір описується тепловим аналогом закону Ома: різниця температур еквівалентна різниці потенціалів (напрузі), теплова потужність — струму, а тепловий опір — електричному опору.

Температура кристала без зовнішнього радіатора розраховується за формулою:

```txt
T_j = T_ambient + P_loss · θ_JA
```

де:
- T_ambient — максимальна температура повітря всередині корпусу пристрою (приймається рівною +50...+70 °C для промислового обладнання);
- θ_JA — повний тепловий опір кристал-середовище (Junction-to-Ambient), що залежить від типу корпусу мікросхеми, площі мідного полігону тепловідводу та кількості шарів плати (наприклад, 25–40 °C/Вт для корпусів QFN/DFN з відкритим тепловим майданчиком Exposed Pad і до 120–180 °C/Вт для мініатюрних корпусів SOT-23/SC-70).

Якщо на мікросхему встановлюється додатковий радіатор або плата контактує з металевим шасі приладу через термопрокладку, повний тепловий опір розраховується як послідовне з'єднання окремих ланок:

```txt
θ_total = θ_JC + θ_CS + θ_SA
```

де θ_JC — тепловий опір кристал-корпус (Junction-to-Case), θ_CS — тепловий опір термоінтерфейсу (Case-to-Heatsink), а θ_SA — тепловий опір радіатора у навколишнє повітря (Heatsink-to-Ambient).

Для надійної безвідмовної роботи вводиться обов'язковий інженерний запас надійності (Thermal Derating): максимальна розрахункова температура кристала T_j в найгіршому піковому режимі не повинна перевищувати 80% від абсолютного паспортного максимуму (тобто не більше +100...+105 °C при паспортній межі +125 °C).

### Теплові перехідні отвори (Thermal Vias) під корпусами силових мікросхем

Для мікросхем у корпусах QFN, DFN та PowerSO основним шляхом відведення тепла є металізований майданчик (Exposed Thermal Pad) на нижньому боці корпусу. Тепловий опір одного перехідного отвору діаметром 0.3 мм з товщиною мідної стінки 25 мкм та висотою 1.6 мм становить приблизно:

```txt
θ_via = h / (k_cu · A_cu)
      ≈ 0.0016 / (390 · π · 0.0003 · 0.000025)
      ≈ 174 °C/Вт
```

Один отвір забезпечує недостатнє відведення тепла. Проте масив із 9–16 перехідних отворів, з'єднаних паралельно під тепловим майданчиком, зменшує еквівалентний тепловий опір переходу до внутрішніх земляних шарів друкованої плати до:

```txt
θ_array = θ_via / N
        = 174 / 16
        ≈ 10.9 °C/Вт
```

Внутрішні суцільні мідні шари землі (GND) товщиною 35 мкм (1 oz) або 70 мкм (2 oz) виконують роль планарного розподільника тепла (Heat Spreader), збільшуючи ефективну площу тепловіддачі в навколишнє повітря.

## Повний покроковий числовий розрахунок тестового дерева живлення

Розглянемо практичний розрахунок промислового контролера з первинним живленням 24 В DC при температурі навколишнього середовища T_amb = +60 °C.

### Крок 1. Розрахунок листових навантажень

Підсумовуємо струми споживання кінцевих споживачів на кожній вторинній шині живлення:

- **Шина 3.3 В (Цифрова):**
  - MCU I/O та периферія: I_1 = 120 мА (0.120 А);
  - QSPI Flash пам'ять: I_2 = 45 мА (0.045 А);
  - Ethernet PHY (трансивер): I_3 = 180 мА (0.180 А);
  - Загальний струм шини 3.3 В: I_3v3_total = 0.120 + 0.045 + 0.180 = 0.345 А;
  - Корисна вихідна потужність: P_3v3_out = 3.3 В · 0.345 А = 1.1385 Вт.

- **Шина 1.2 В (Ядро MCU):**
  - Cortex-M7 Core на частоті 480 МГц: I_core = 850 мА (0.850 А);
  - Корисна вихідна потужність: P_1v2_out = 1.2 В · 0.850 А = 1.020 Вт.

- **Шина 3.3 В Analog (Прецизійна):**
  - 24-бітний сигма-дельта АЦП: I_adc = 15 мА (0.015 А);
  - Буферні операційні підсилювачі: I_opamp = 25 мА (0.025 А);
  - Джерело опорної напруги VREF: I_vref = 5 мА (0.005 А);
  - Загальний струм шини 3.3V_ANA: I_ana_total = 0.015 + 0.025 + 0.005 = 0.045 А;
  - Корисна вихідна потужність: P_ana_out = 3.3 В · 0.045 А = 0.1485 Вт.

- **Шина 5.0 В Isolated (Польова):**
  - Ізольований CAN-FD трансивер: I_can = 60 мА (0.060 А);
  - Ізольований RS-485 трансивер: I_rs485 = 80 мА (0.080 А);
  - Загальний струм шини 5V_ISO: I_iso_total = 0.060 + 0.080 = 0.140 А;
  - Корисна вихідна потужність: P_iso_out = 5.0 В · 0.140 А = 0.700 Вт.

### Крок 2. Розрахунок вторинних перетворювачів (Каскад 2)

Обчислюємо вхідні струми, які вторинні перетворювачі споживають від проміжної шини 5.0 В:

- **DC-DC Buck 3.3V (5.0V -> 3.3V):**
  - Вихідна потужність: P_out = 1.1385 Вт;
  - ККД перетворювача при I_out = 0.345 А: η = 94% (0.94);
  - Вхідна споживана потужність: P_in = 1.1385 / 0.94 ≈ 1.2112 Вт;
  - Вхідний струм від шини 5.0 В: I_in_3v3 = 1.2112 / 5.0 = 0.2422 А;
  - Теплові втрати: P_loss_3v3 = 1.2112 - 1.1385 = 0.0727 Вт;
  - Температура кристала (θ_JA = 45 °C/Вт): T_j = 60 + 0.0727 · 45 = 63.3 °C (норма).

- **DC-DC Buck 1.2V Core (5.0V -> 1.2V):**
  - Вихідна потужність: P_out = 1.020 Вт;
  - ККД перетворювача при I_out = 0.850 А: η = 88% (0.88);
  - Вхідна споживана потужність: P_in = 1.020 / 0.88 ≈ 1.1591 Вт;
  - Вхідний струм від шини 5.0 В: I_in_1v2 = 1.1591 / 5.0 = 0.2318 А;
  - Теплові втрати: P_loss_1v2 = 1.1591 - 1.020 = 0.1391 Вт;
  - Температура кристала (θ_JA = 50 °C/Вт): T_j = 60 + 0.1391 · 50 = 67.0 °C (норма).

- **LDO 3.3V Analog (5.0V -> 3.3V_ANA):**
  - Вихідний струм: I_out = 0.045 А;
  - Вхідний струм: I_in_ldo = I_out = 0.045 А;
  - ККД лінійного стабілізатора: η = 3.3 / 5.0 = 66.0% (0.66);
  - Вхідна споживана потужність: P_in = 5.0 · 0.045 = 0.225 Вт;
  - Теплові втрати: P_loss_ldo = (5.0 - 3.3) · 0.045 = 0.0765 Вт;
  - Температура кристала (θ_JA = 62 °C/Вт): T_j = 60 + 0.0765 · 62 = 64.7 °C (норма).

- **Ізольований DC-DC 5V_ISO (5.0V -> 5.0V_ISO):**
  - Вихідна потужність: P_out = 0.700 Вт;
  - ККД ізольованого модуля: η = 78% (0.78);
  - Вхідна споживана потужність: P_in = 0.700 / 0.78 ≈ 0.8974 Вт;
  - Вхідний струм від шини 5.0 В: I_in_iso = 0.8974 / 5.0 = 0.1795 А;
  - Теплові втрати: P_loss_iso = 0.8974 - 0.700 = 0.1974 Вт;
  - Температура кристала (θ_JA = 70 °C/Вт): T_j = 60 + 0.1974 · 70 = 73.8 °C (норма).

### Крок 3. Розрахунок первинного перетворювача (Каскад 1)

Сумуємо струми всіх вторинних стабілізаторів на шині 5.0 В:

```txt
I_5v_total = I_in_3v3 + I_in_1v2 + I_in_ldo + I_in_iso
           = 0.2422 + 0.2318 + 0.0450 + 0.1795
           = 0.6985 А       [сумарний струм навантаження шини 5.0 В]
```

- Вихідна корисна потужність шини 5.0 В: P_5v_out = 5.0 В · 0.6985 А = 3.4925 Вт;
- ККД головного перетворювача Buck 24V->5V при I_out = 0.70 А: η = 91% (0.91);
- Загальна вхідна потужність, споживана від первинного джерела 24 В:

```txt
P_in_total = P_5v_out / η
           = 3.4925 / 0.91
           ≈ 3.8379 Вт
```

- Вхідний постійний струм від джерела 24 В:

```txt
I_in_24v = P_in_total / 24.0
         = 3.8379 / 24.0
         ≈ 0.1599 А       [160 мА від джерела 24 В]
```

- Теплові втрати головного перетворювача:

```txt
P_loss_buck24 = P_in_total - P_5v_out
              = 3.8379 - 3.4925
              = 0.3454 Вт
```

- Температура кристала головного перетворювача (θ_JA = 35 °C/Вт):

```txt
T_j = T_amb + P_loss · θ_JA
    = 60 + 0.3454 · 35
    ≈ 72.1 °C       [відповідає запасу надійності < 105 °C]
```

Загальний системний ККД від первинного входу 24 В до кінцевих споживачів становить:

```txt
η_system = (P_3v3_out + P_1v2_out + P_ana_out + P_iso_out) / P_in_total
         = (1.1385 + 1.020 + 0.1485 + 0.700) / 3.8379
         = 3.007 / 3.8379
         ≈ 78.35%
```

Цей числовий результат наочно демонструє перевагу каскадної архітектури: незважаючи на два послідовні ступені перетворення, загальний ККД перевищує 78%, а сумарні теплові втрати всіх регуляторів разом становлять менше 0.84 Вт.

## Багатопрофільний аналіз енергоспоживання (Multi-Profile Scenario Modeling)

У реальних вбудованих системах енергоспоживання є нестаціонарним процесом. Пристрій циклічно перемикається між різними функціональними профілями. Для коректної оцінки ресурсу джерела живлення та теплового балансу утиліта підтримує розрахунок трьох сценаріїв:

1. **Профіль сну (Sleep / Standby Profile):**
   - Мікроконтролер у режимі Stop/Standby (споживання ядра < 2 мА);
   - Ethernet PHY переведено в режим енергозбереження IEEE 802.3az (Energy-Efficient Ethernet);
   - Аналоговий тракт та польові трансивери знеструмлені ключами живлення Load Switch;
   - Сумарний струм від 24 В знижується до 8–15 мА;
   - Цей профіль визначає мінімальне фонове нагрівання та час автономної роботи.

2. **Номінальний робочий профіль (Nominal Operational Profile):**
   - Ядро мікроконтролера завантажене на 40–50%;
   - Періодичне опитування датчиків 10 разів на секунду;
   - Мережевий обмін даними телеметрії короткими пакетами;
   - Середнє споживання від 24 В становить 80–100 мА.

3. **Піковий профіль максимального навантаження (Worst-Case Peak Profile):**
   - Одночасна передача даних по Ethernet на швидкості 100 Мбіт/с та CAN-FD на 5 Мбіт/с;
   - Запис логів у флеш-пам'ять OctoSPI на максимальній тактовій частоті;
   - Одночасна комутація всіх релейних виходів;
   - Максимальний розрахунковий струм від 24 В досягає 160–220 мА.

Середньозважена потужність пристрою за добу розраховується як сума потужностей профілів, зважених за їхніми коефіцієнтами заповнення в часі (Duty Cycle, D_i):

```txt
P_average = D_sleep · P_sleep + D_nominal · P_nominal + D_peak · P_peak
```

Для системи, яка 90% часу перебуває в сні (D_sleep = 0.90), 9% у номіналі (D_nominal = 0.09) та 1% у піковому навантаженні (D_peak = 0.01), середньодобова потужність становить:

```txt
P_average = 0.90 · 0.24 Вт + 0.09 · 2.10 Вт + 0.01 · 3.84 Вт
          = 0.216 + 0.189 + 0.0384
          ≈ 0.443 Вт
```

Це дозволяє точно розрахувати необхідну ємність резервного акумулятора для заданого часу автономної роботи (наприклад, для роботи протягом 48 годин без зовнішнього живлення потрібна корисна енергія W = 0.443 Вт · 48 год = 21.28 Вт·год).

## Динамічні перехідні процеси та цільовий імпеданс шин (Target Impedance)

Окрім статичного балансу потужності, дерево живлення повинно забезпечувати стабільність напруги при динамічних стрибках струму споживання (Load Transients). Коли процесор Cortex-M7 раптово переходить зі стану низького споживання WFI (Wait-for-Interrupt) до виконання обчислень з плаваючою комою, струм шини 1.2 В зростає від 50 мА до 850 мА за час менше 10 наносекунд:

```txt
(dI / dt) = (0.850 - 0.050) / (10 · 10^(-9)) = 8 · 10^7 А/с       [80 амперів за мікросекунду]
```

Контур зворотного зв'язку DC-DC перетворювача з типовою смугою пропускання 50–100 кГц фізично не здатний відреагувати на такий швидкий процес (його час реакції становить 10–20 мікросекунд). Протягом цього інтервалу струм у навантаження постачається виключно за рахунок енергії, накопиченої у вихідних керамічних конденсаторах дев'язки (Decoupling Capacitors).

Щоб просідання напруги ΔV_max не перевищило допустимих меж (наприклад, ±3% від 1.2 В, тобто ΔV_max = 36 мВ), імпеданс шини живлення у всьому робочому діапазоні частот повинен бути меншим за цільовий імпеданс (Target Impedance):

```txt
Z_target = ΔV_allowed / ΔI_transient
         = 0.036 / 0.800
         = 0.045 Ом       [45 міліом]
```

Для підтримки імпедансу нижче 45 мОм у діапазоні частот від сотень кілогерців до сотень мегагерців на блок-схемі закладається багаторівнева конденсаторна мережа:

1. **Об'ємні конденсатори (Bulk Capacitors):** Танталові полімерні або алюмінієві електролітичні конденсатори ємністю 47–100 мкФ (підтримують напругу на частотах до 100 кГц, поки не відреагує контур стабілізатора).
2. **Середні керамічні конденсатори:** Кераміка MLCC типорозміру 0805/0603 ємністю 10–22 мкФ (працюють у діапазоні 100 кГц – 5 МГц).
3. **Локальні високочастотні блокувальні конденсатори:** Кераміка MLCC типорозміру 0402/0201 ємністю 0.1–1.0 мкФ з ультранизькою власною індуктивністю ESL, розміщена впритул до виводів живлення BGA/QFP корпусу мікроконтролера (працюють на частотах від 5 МГц до 200 МГц).

## Повна реалізація утиліти на мовах C99 та C++20

Нижче наведено повну реалізацію розрахункового рушія дерева живлення на C99 та C++20 у перемикачі вкладок.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_CHILDREN 8
#define MAX_NODES 32

typedef enum {
    NODE_ROOT_SOURCE,
    NODE_BUCK_CONVERTER,
    NODE_BOOST_CONVERTER,
    NODE_LDO_REGULATOR,
    NODE_ISOLATED_DCDC,
    NODE_LEAF_LOAD
} node_type_t;

typedef struct power_node {
    int id;
    const char *name;
    node_type_t type;
    float v_out;                 /* Вихідна напруга, В */
    float i_leaf_load;           /* Власний струм споживання (для листових вузлів), А */
    float i_max_limit;           /* Паспортний ліміт вихідного струму, А */
    float efficiency_nominal;    /* Номінальний ККД для DC-DC (0.0 .. 1.0) */
    float theta_ja;              /* Тепловий опір кристал-середовище, °C/Вт */
    float t_j_max;               /* Максимально допустима температура кристала, °C */

    struct power_node *parent;
    struct power_node *children[MAX_CHILDREN];
    size_t children_count;

    /* Розрахункові вихідні поля */
    float calculated_i_out;      /* Сумарний струм на виході вузла, А */
    float calculated_p_out;      /* Корисна вихідна потужність, Вт */
    float calculated_efficiency; /* Розрахунковий ККД */
    float calculated_p_in;       /* Вхідна споживана потужність, Вт */
    float calculated_i_in;       /* Вхідний струм споживання, А */
    float calculated_p_loss;     /* Потужність теплових втрат, Вт */
    float calculated_t_j;        /* Розрахункова температура кристала, °C */
    bool has_overcurrent_error;
    bool has_overheat_error;
} power_node_t;

static power_node_t* create_node(int id, const char *name, node_type_t type, 
                                 float v_out, float i_leaf, float i_limit, 
                                 float eff, float theta, float tj_max) {
    power_node_t *node = (power_node_t*)malloc(sizeof(power_node_t));
    if (!node) return NULL;
    memset(node, 0, sizeof(power_node_t));

    node->id = id;
    node->name = name;
    node->type = type;
    node->v_out = v_out;
    node->i_leaf_load = i_leaf;
    node->i_max_limit = i_limit;
    node->efficiency_nominal = eff;
    node->theta_ja = theta;
    node->t_j_max = tj_max;

    return node;
}

static bool add_child(power_node_t *parent, power_node_t *child) {
    if (!parent || !child || parent->children_count >= MAX_CHILDREN) {
        return false;
    }
    parent->children[parent->children_count++] = child;
    child->parent = parent;
    return true;
}

static float evaluate_converter_efficiency(const power_node_t *node, float i_out) {
    if (node->type == NODE_LDO_REGULATOR) {
        if (node->parent && node->parent->v_out > 0.01f) {
            return node->v_out / node->parent->v_out;
        }
        return 0.5f;
    }

    if (node->type == NODE_BUCK_CONVERTER || node->type == NODE_BOOST_CONVERTER || 
        node->type == NODE_ISOLATED_DCDC) {
        if (i_out <= 0.001f) return 0.20f; /* Низький ККД на холостому ході */
        
        float load_ratio = i_out / (node->i_max_limit > 0.01f ? node->i_max_limit : 1.0f);
        if (load_ratio > 1.0f) load_ratio = 1.0f;

        /* Модель нелінійності ККД: плавний вихід на плато з падінням при малому струмі */
        float eff = node->efficiency_nominal * (1.0f - 0.15f * (1.0f - load_ratio) * (1.0f - load_ratio));
        return (eff > 0.1f) ? eff : 0.1f;
    }

    return 1.0f;
}

static void calculate_power_tree_recursive(power_node_t *node, float ambient_temp) {
    if (!node) return;

    /* Рекурсивно обчислюємо всіх нащадків (Bottom-Up) */
    float sum_child_current = 0.0f;
    for (size_t i = 0; i < node->children_count; ++i) {
        calculate_power_tree_recursive(node->children[i], ambient_temp);
        sum_child_current += node->children[i]->calculated_i_in;
    }

    if (node->type == NODE_LEAF_LOAD) {
        node->calculated_i_out = node->i_leaf_load;
        node->calculated_p_out = node->v_out * node->calculated_i_out;
        node->calculated_efficiency = 1.0f;
        node->calculated_p_in = node->calculated_p_out;
        node->calculated_i_in = node->calculated_i_out;
        node->calculated_p_loss = 0.0f;
        node->calculated_t_j = ambient_temp;
        node->has_overcurrent_error = false;
        node->has_overheat_error = false;
        return;
    }

    node->calculated_i_out = sum_child_current;
    node->calculated_p_out = node->v_out * node->calculated_i_out;
    node->has_overcurrent_error = (node->i_max_limit > 0.0f && node->calculated_i_out > node->i_max_limit);

    if (node->type == NODE_ROOT_SOURCE) {
        node->calculated_efficiency = 1.0f;
        node->calculated_p_in = node->calculated_p_out;
        node->calculated_i_in = node->calculated_i_out;
        node->calculated_p_loss = 0.0f;
        node->calculated_t_j = ambient_temp;
        node->has_overheat_error = false;
        return;
    }

    /* Розрахунок перетворювача */
    float v_in = node->parent ? node->parent->v_out : node->v_out;
    node->calculated_efficiency = evaluate_converter_efficiency(node, node->calculated_i_out);

    if (node->type == NODE_LDO_REGULATOR) {
        node->calculated_p_loss = (v_in - node->v_out) * node->calculated_i_out;
        node->calculated_p_in = node->calculated_p_out + node->calculated_p_loss;
        node->calculated_i_in = node->calculated_i_out;
    } else {
        node->calculated_p_in = (node->calculated_efficiency > 0.01f) 
                                ? (node->calculated_p_out / node->calculated_efficiency) 
                                : node->calculated_p_out;
        node->calculated_p_loss = node->calculated_p_in - node->calculated_p_out;
        node->calculated_i_in = (v_in > 0.01f) ? (node->calculated_p_in / v_in) : 0.0f;
    }

    node->calculated_t_j = ambient_temp + (node->calculated_p_loss * node->theta_ja);
    node->has_overheat_error = (node->calculated_t_j > node->t_j_max);
}

static void print_node_report(const power_node_t *node, int depth) {
    if (!node) return;

    char indent[64] = {0};
    for (int i = 0; i < depth && i < 30; ++i) {
        strcat(indent, "  ");
    }

    const char *type_str = "LOAD";
    if (node->type == NODE_ROOT_SOURCE)      type_str = "ROOT";
    else if (node->type == NODE_BUCK_CONVERTER)   type_str = "BUCK";
    else if (node->type == NODE_BOOST_CONVERTER)  type_str = "BOOST";
    else if (node->type == NODE_LDO_REGULATOR)    type_str = "LDO";
    else if (node->type == NODE_ISOLATED_DCDC)    type_str = "ISO-DC";

    printf("%s[%s] %-20s | %4.1fV | I_out: %5.3fA | P_out: %5.2fW | ККД: %4.1f%% | P_loss: %5.2fW | T_j: %5.1fC",
           indent, type_str, node->name, node->v_out, node->calculated_i_out,
           node->calculated_p_out, node->calculated_efficiency * 100.0f,
           node->calculated_p_loss, node->calculated_t_j);

    if (node->has_overcurrent_error) printf(" -> [УВАГА: СТРУМ > ЛІМІТ!]");
    if (node->has_overheat_error)    printf(" -> [УВАГА: ПЕРЕГРІВ КРИСТАЛА!]");
    printf("\n");

    for (size_t i = 0; i < node->children_count; ++i) {
        print_node_report(node->children[i], depth + 1);
    }
}

static void free_tree(power_node_t *node) {
    if (!node) return;
    for (size_t i = 0; i < node->children_count; ++i) {
        free_tree(node->children[i]);
    }
    free(node);
}

int main(void) {
    const float ambient_temperature = 60.0f; /* Промисловий діапазон +60 °C */

    /* 1. Створення вузлів дерева живлення */
    power_node_t *root = create_node(1, "Primary 24V DC", NODE_ROOT_SOURCE, 24.0f, 0.0f, 5.0f, 1.0f, 0.0f, 125.0f);
    power_node_t *buck_5v = create_node(2, "Buck 24V->5V", NODE_BUCK_CONVERTER, 5.0f, 0.0f, 2.5f, 0.91f, 35.0f, 125.0f);

    power_node_t *buck_3v3 = create_node(3, "Buck 5V->3.3V", NODE_BUCK_CONVERTER, 3.3f, 0.0f, 1.5f, 0.94f, 45.0f, 125.0f);
    power_node_t *buck_1v2 = create_node(4, "Buck 5V->1.2V Core", NODE_BUCK_CONVERTER, 1.2f, 0.0f, 1.2f, 0.88f, 50.0f, 125.0f);
    power_node_t *ldo_3v3a = create_node(5, "LDO 5V->3.3V_ANA", NODE_LDO_REGULATOR, 3.3f, 0.0f, 0.2f, 0.66f, 62.0f, 125.0f);
    power_node_t *iso_5v   = create_node(6, "ISO DC-DC 5V->5V", NODE_ISOLATED_DCDC, 5.0f, 0.0f, 0.3f, 0.78f, 70.0f, 125.0f);

    /* Листові навантаження 3.3V */
    power_node_t *load_mcu_io = create_node(7, "MCU I/O & Periph", NODE_LEAF_LOAD, 3.3f, 0.120f, 0.0f, 1.0f, 0.0f, 105.0f);
    power_node_t *load_flash  = create_node(8, "QSPI Flash 32MB",  NODE_LEAF_LOAD, 3.3f, 0.045f, 0.0f, 1.0f, 0.0f, 105.0f);
    power_node_t *load_eth    = create_node(9, "Ethernet PHY",     NODE_LEAF_LOAD, 3.3f, 0.180f, 0.0f, 1.0f, 0.0f, 105.0f);

    /* Листові навантаження 1.2V Core */
    power_node_t *load_core   = create_node(10, "MCU Cortex-M7 Core", NODE_LEAF_LOAD, 1.2f, 0.850f, 0.0f, 1.0f, 0.0f, 105.0f);

    /* Листові навантаження 3.3V Analog */
    power_node_t *load_adc    = create_node(11, "24-bit Delta-Sigma ADC", NODE_LEAF_LOAD, 3.3f, 0.015f, 0.0f, 1.0f, 0.0f, 105.0f);
    power_node_t *load_opamp  = create_node(12, "Input Buffer Op-Amps",   NODE_LEAF_LOAD, 3.3f, 0.025f, 0.0f, 1.0f, 0.0f, 105.0f);
    power_node_t *load_vref   = create_node(13, "Precision 2.5V VREF",    NODE_LEAF_LOAD, 3.3f, 0.005f, 0.0f, 1.0f, 0.0f, 105.0f);

    /* Листові навантаження 5V Isolated */
    power_node_t *load_can    = create_node(14, "CAN-FD Transceiver", NODE_LEAF_LOAD, 5.0f, 0.060f, 0.0f, 1.0f, 0.0f, 105.0f);
    power_node_t *load_rs485  = create_node(15, "RS-485 Modbus Node", NODE_LEAF_LOAD, 5.0f, 0.080f, 0.0f, 1.0f, 0.0f, 105.0f);

    /* 2. Побудова ієрархії зв'язків */
    add_child(root, buck_5v);

    add_child(buck_5v, buck_3v3);
    add_child(buck_5v, buck_1v2);
    add_child(buck_5v, ldo_3v3a);
    add_child(buck_5v, iso_5v);

    add_child(buck_3v3, load_mcu_io);
    add_child(buck_3v3, load_flash);
    add_child(buck_3v3, load_eth);

    add_child(buck_1v2, load_core);

    add_child(ldo_3v3a, load_adc);
    add_child(ldo_3v3a, load_opamp);
    add_child(ldo_3v3a, load_vref);

    add_child(iso_5v, load_can);
    add_child(iso_5v, load_rs485);

    /* 3. Розрахунок бюджету дерева живлення */
    calculate_power_tree_recursive(root, ambient_temperature);

    /* 4. Вивід звіту */
    printf("========================================================================================\n");
    printf("         ІНЖЕНЕРНИЙ ЗВІТ РОЗРАХУНКУ ДЕРЕВА ЖИВЛЕННЯ ТА ТЕПЛОВОГО БАЛАНСУ (C99)          \n");
    printf("         Температура середовища T_amb = %.1f °C                                         \n", ambient_temperature);
    printf("========================================================================================\n");
    print_node_report(root, 0);
    printf("========================================================================================\n");
    printf("Підсумок: Вхідна потужність = %.2f Вт | Вхідний струм від 24V = %.3f А | Втрати = %.2f Вт\n",
           root->calculated_p_in, root->calculated_i_in, root->calculated_p_in - (buck_3v3->calculated_p_out + buck_1v2->calculated_p_out + ldo_3v3a->calculated_p_out + iso_5v->calculated_p_out));
    printf("========================================================================================\n");

    free_tree(root);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <string_view>
#include <format>
#include <numeric>
#include <algorithm>
#include <cstdint>

namespace hw::powertree {

enum class NodeType : uint8_t {
    RootSource,
    BuckConverter,
    BoostConverter,
    LdoRegulator,
    IsolatedDcDc,
    LeafLoad
};

struct NodeConfig {
    std::string name;
    NodeType type{NodeType::LeafLoad};
    float v_out{3.3f};
    float i_leaf_load{0.0f};
    float i_max_limit{1.0f};
    float efficiency_nominal{0.90f};
    float theta_ja{40.0f};
    float t_j_max{125.0f};
};

struct CalculatedMetrics {
    float i_out{0.0f};
    float p_out{0.0f};
    float efficiency{1.0f};
    float p_in{0.0f};
    float i_in{0.0f};
    float p_loss{0.0f};
    float t_junction{25.0f};
    bool is_overcurrent{false};
    bool is_overheated{false};
};

class PowerNode {
public:
    explicit PowerNode(NodeConfig config)
        : config_{std::move(config)} {}

    void addChild(std::shared_ptr<PowerNode> child) {
        if (child) {
            children_.push_back(child);
            child->parent_ = this;
        }
    }

    void calculateBottomUp(float ambient_temp_c) noexcept {
        float sum_child_current = 0.0f;
        for (const auto& child : children_) {
            child->calculateBottomUp(ambient_temp_c);
            sum_child_current += child->metrics_.i_in;
        }

        if (config_.type == NodeType::LeafLoad) {
            metrics_.i_out = config_.i_leaf_load;
            metrics_.p_out = config_.v_out * metrics_.i_out;
            metrics_.efficiency = 1.0f;
            metrics_.p_in = metrics_.p_out;
            metrics_.i_in = metrics_.i_out;
            metrics_.p_loss = 0.0f;
            metrics_.t_junction = ambient_temp_c;
            metrics_.is_overcurrent = false;
            metrics_.is_overheated = false;
            return;
        }

        metrics_.i_out = sum_child_current;
        metrics_.p_out = config_.v_out * metrics_.i_out;
        metrics_.is_overcurrent = (config_.i_max_limit > 0.0f && metrics_.i_out > config_.i_max_limit);

        if (config_.type == NodeType::RootSource) {
            metrics_.efficiency = 1.0f;
            metrics_.p_in = metrics_.p_out;
            metrics_.i_in = metrics_.i_out;
            metrics_.p_loss = 0.0f;
            metrics_.t_junction = ambient_temp_c;
            metrics_.is_overheated = false;
            return;
        }

        const float v_in = parent_ ? parent_->config_.v_out : config_.v_out;
        metrics_.efficiency = computeEfficiency(metrics_.i_out, v_in);

        if (config_.type == NodeType::LdoRegulator) {
            metrics_.p_loss = (v_in - config_.v_out) * metrics_.i_out;
            metrics_.p_in = metrics_.p_out + metrics_.p_loss;
            metrics_.i_in = metrics_.i_out;
        } else {
            metrics_.p_in = (metrics_.efficiency > 0.01f) 
                            ? (metrics_.p_out / metrics_.efficiency) 
                            : metrics_.p_out;
            metrics_.p_loss = metrics_.p_in - metrics_.p_out;
            metrics_.i_in = (v_in > 0.01f) ? (metrics_.p_in / v_in) : 0.0f;
        }

        metrics_.t_junction = ambient_temp_c + (metrics_.p_loss * config_.theta_ja);
        metrics_.is_overheated = (metrics_.t_junction > config_.t_j_max);
    }

    void printReport(int depth = 0) const {
        std::string indent(static_cast<size_t>(depth * 2), ' ');

        std::string_view type_label = "LOAD";
        switch (config_.type) {
            case NodeType::RootSource:    type_label = "ROOT"; break;
            case NodeType::BuckConverter: type_label = "BUCK"; break;
            case NodeType::BoostConverter:type_label = "BOOST"; break;
            case NodeType::LdoRegulator:  type_label = "LDO"; break;
            case NodeType::IsolatedDcDc:  type_label = "ISO-DC"; break;
            case NodeType::LeafLoad:      type_label = "LOAD"; break;
        }

        std::cout << std::format("{}[{:6}] {:<20} | {:4.1f}V | I_out: {:5.3f}A | P_out: {:5.2f}W | ККД: {:4.1f}% | P_loss: {:5.2f}W | T_j: {:5.1f}°C",
                                 indent, type_label, config_.name, config_.v_out, metrics_.i_out,
                                 metrics_.p_out, metrics_.efficiency * 100.0f,
                                 metrics_.p_loss, metrics_.t_junction);

        if (metrics_.is_overcurrent) std::cout << " -> [УВАГА: СТРУМ > ЛІМІТ!]";
        if (metrics_.is_overheated)  std::cout << " -> [УВАГА: ПЕРЕГРІВ КРИСТАЛА!]";
        std::cout << '\n';

        for (const auto& child : children_) {
            child->printReport(depth + 1);
        }
    }

    [[nodiscard]] const CalculatedMetrics& metrics() const noexcept { return metrics_; }
    [[nodiscard]] const NodeConfig& config() const noexcept { return config_; }

private:
    [[nodiscard]] float computeEfficiency(float i_out, float v_in) const noexcept {
        if (config_.type == NodeType::LdoRegulator) {
            return (v_in > 0.01f) ? (config_.v_out / v_in) : 0.5f;
        }

        if (i_out <= 0.001f) return 0.20f;
        float load_ratio = i_out / (config_.i_max_limit > 0.01f ? config_.i_max_limit : 1.0f);
        load_ratio = std::clamp(load_ratio, 0.0f, 1.0f);

        float eff = config_.efficiency_nominal * (1.0f - 0.15f * (1.0f - load_ratio) * (1.0f - load_ratio));
        return std::max(eff, 0.10f);
    }

    NodeConfig config_;
    CalculatedMetrics metrics_;
    PowerNode* parent_{nullptr};
    std::vector<std::shared_ptr<PowerNode>> children_;
};

} // namespace hw::powertree

int main() {
    using namespace hw::powertree;

    constexpr float ambient_temp = 60.0f;

    auto root = std::make_shared<PowerNode>(NodeConfig{"Primary 24V DC", NodeType::RootSource, 24.0f, 0.0f, 5.0f, 1.0f, 0.0f, 125.0f});
    auto buck_5v = std::make_shared<PowerNode>(NodeConfig{"Buck 24V->5V", NodeType::BuckConverter, 5.0f, 0.0f, 2.5f, 0.91f, 35.0f, 125.0f});

    auto buck_3v3 = std::make_shared<PowerNode>(NodeConfig{"Buck 5V->3.3V", NodeType::BuckConverter, 3.3f, 0.0f, 1.5f, 0.94f, 45.0f, 125.0f});
    auto buck_1v2 = std::make_shared<PowerNode>(NodeConfig{"Buck 5V->1.2V Core", NodeType::BuckConverter, 1.2f, 0.0f, 1.2f, 0.88f, 50.0f, 125.0f});
    auto ldo_3v3a = std::make_shared<PowerNode>(NodeConfig{"LDO 5V->3.3V_ANA", NodeType::LdoRegulator, 3.3f, 0.0f, 0.2f, 0.66f, 62.0f, 125.0f});
    auto iso_5v   = std::make_shared<PowerNode>(NodeConfig{"ISO DC-DC 5V->5V", NodeType::IsolatedDcDc, 5.0f, 0.0f, 0.3f, 0.78f, 70.0f, 125.0f});

    root->addChild(buck_5v);
    buck_5v->addChild(buck_3v3);
    buck_5v->addChild(buck_1v2);
    buck_5v->addChild(ldo_3v3a);
    buck_5v->addChild(iso_5v);

    buck_3v3->addChild(std::make_shared<PowerNode>(NodeConfig{"MCU I/O & Periph", NodeType::LeafLoad, 3.3f, 0.120f}));
    buck_3v3->addChild(std::make_shared<PowerNode>(NodeConfig{"QSPI Flash 32MB",  NodeType::LeafLoad, 3.3f, 0.045f}));
    buck_3v3->addChild(std::make_shared<PowerNode>(NodeConfig{"Ethernet PHY",     NodeType::LeafLoad, 3.3f, 0.180f}));

    buck_1v2->addChild(std::make_shared<PowerNode>(NodeConfig{"MCU Cortex-M7 Core", NodeType::LeafLoad, 1.2f, 0.850f}));

    ldo_3v3a->addChild(std::make_shared<PowerNode>(NodeConfig{"24-bit Delta-Sigma ADC", NodeType::LeafLoad, 3.3f, 0.015f}));
    ldo_3v3a->addChild(std::make_shared<PowerNode>(NodeConfig{"Input Buffer Op-Amps",   NodeType::LeafLoad, 3.3f, 0.025f}));
    ldo_3v3a->addChild(std::make_shared<PowerNode>(NodeConfig{"Precision 2.5V VREF",    NodeType::LeafLoad, 3.3f, 0.005f}));

    iso_5v->addChild(std::make_shared<PowerNode>(NodeConfig{"CAN-FD Transceiver", NodeType::LeafLoad, 5.0f, 0.060f}));
    iso_5v->addChild(std::make_shared<PowerNode>(NodeConfig{"RS-485 Modbus Node", NodeType::LeafLoad, 5.0f, 0.080f}));

    root->calculateBottomUp(ambient_temp);

    std::cout << "========================================================================================\n";
    std::cout << "        ІНЖЕНЕРНИЙ ЗВІТ РОЗРАХУНКУ ДЕРЕВА ЖИВЛЕННЯ ТА ТЕПЛОВОГО БАЛАНСУ (C++20)         \n";
    std::cout << std::format("        Температура середовища T_amb = {:.1f} °C                                         \n", ambient_temp);
    std::cout << "========================================================================================\n";
    root->printReport();
    std::cout << "========================================================================================\n";
    std::cout << std::format("Підсумок: Вхідна потужність = {:.2f} Вт | Вхідний струм від 24V = {:.3f} А\n",
                             root->metrics().p_in, root->metrics().i_in);
    std::cout << "========================================================================================\n";

    return 0;
}
```
:::

## Інженерні пастки та крайові випадки при розрахунку живлення

При практичному моделюванні дерева живлення розробники часто стикаються з чотирма критичними ефектами, неврахування яких призводить до відмов обладнання під час випробувань:

1. **Падіння напруги Drop-Out на LDO при просіданні первинної шини:** Якщо вхідна шина 5.0 В через динамічний накид навантаження короткочасно просідає до 3.5 В, лінійний стабілізатор 3.3 В виходить із режиму стабілізації (його прохідний польовий транзистор повністю відкривається, перетворюючись на звичайний резистор). Опорна напруга АЦП починає коливатися вслід за шумами первинної шини, що руйнує точність вимірювань.
2. **Падіння ККД імпульсних перетворювачів у режимі легкого навантаження (Light-Load Efficiency):** У сплячому режимі (Sleep Mode) мікроконтролер споживає лише 50 мкА. Більшість імпульсних перетворювачів переходять у режим пропуску імпульсів (Pulse-Skipping / Burst Mode). Якщо регулятор не підтримує цей режим, його ККД падає нижче 20%, а власні втрати починають у 10 разів перевищувати корисну потужність навантаження.
3. **Температурне зниження ємності керамічних конденсаторів (DC Bias & Thermal Derating):** Багатошарові керамічні конденсатори MLCC діелектрика X7R/X5R втрачають до 50–70% своєї номінальної ємності при подачі постійної робочої напруги, близької до номінальної. Зниження реальної вихідної ємності C_out удвічі призводить до подвоєння комутаційних пульсацій та можливої втрати фазової стійкості контуру зворотного зв'язку DC-DC перетворювача.
4. **Каскадне спрацьовування захисту від перевантаження:** Якщо первинний перетворювач 24V->5V розрахований на межу 2.5 А, а вторинні стабілізатори під час холодного старту одночасно споживають сумарний піковий пусковий струм 3.2 А, первинний контролер переходить у режим захисту (Hiccup Mode). Система потрапляє в нескінченний цикл перезавантажень, не маючи змоги вийти на робочий режим без реалізації послідовного запуску (Power Sequencing).
5. **Нелінійне насичення силових дроселів при високих температурах (Inductor Saturation Roll-Off):** При нагріванні осердя дроселя до +100 °C індукція насичення фериту B_sat падає на 20–30%. Якщо піковий струм перетворювача наближається до струму насичення I_sat, диференційна індуктивність дроселя різко падає, що викликає лавиноподібне зростання пікового струму через силовий транзистор, різке зростання електромагнітного випромінювання (EMI) та аварійне спрацьовування захисту overcurrent. При виборі індуктивності на блок-схемі обов'язково закладається запас: струм насичення дроселя I_sat при температурі +100 °C повинен перевищувати піковий струм перетворювача щонайменше на 30–40%.
6. **Інтеграція моделі живлення в процес проектування та автоматичний аудит схем (Hardware CI/CD):** Розрахунковий модуль дерева живлення може бути інтегрований у систему автоматизованого проектування друкованих плат (EDA) або конвеєр неперервної інтеграції (CI/CD) апаратного проекту. Скрипт зчитує список кіл (Netlist) і перелік компонентів (BOM), будує граф живлення та автоматично генерує звіт про дотримання теплових меж і запасів за струмом під час кожного збереження проекту схеми. Якщо в процесі модифікації схеми додається новий енергоємний периферійний вузол, який перевантажує шину 3.3 В або розігріває стабілізатор LDO вище допустимого порогу, конвеєр CI повертає помилку верифікації ще до передачі плати на трасування та виготовлення прототипу.
7. **Верифікація на фізичному випробувальному стенді (Bench Testing):** Після виготовлення перших зразків друкованої плати теоретичні розрахунки дерева живлення валідуються за допомогою тепловізора (FLIR / Thermal Camera) у термокамері при максимальній робочій температурі +60 °C, а також за допомогою швидкісного осцилографа з токовими пробниками для фіксації реальних перехідних процесів і амплітуди шуму шин живлення під час динамічних накидів навантаження.
