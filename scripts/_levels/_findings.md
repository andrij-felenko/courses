# Побічні знахідки фази оцінки рівнів

Оцінювачі бачать книгу списком тем цілком — під таким кутом видно те, чого не видно
з окремої теми. Записую сюди, щоб не загубилося. **Нічого з цього не виправлено.**

## sf-algorithms — можливі дублі понять

Оцінювач C, ставлячи Р1, помітив пари, де друга тема виглядає тим самим поняттям:

| ймовірний дубль | наявна тема | що каже |
|---|---|---|
| `k-d-tree` | `kd-tree` | той самий термін, різне написання слуга |
| `edmonds-algorithm` | `edmonds-blossom-algorithm` | абревіатура й повна назва |
| `perfect-matching` | `bipartite-matching` | вужче й ширше про те саме |
| `adjacency-matrix` | `graph-representation` | частина під цілим |
| `run-length-codes` | `rle` | розшифровка й абревіатура |

Це рівно ті чотири сигнали, які стереже `manifest-patch.js` перед заведенням нової теми
(`⚠ МОЖЛИВІ ДУБЛІ ПОНЯТЬ`) — але вони вже в корпусі, тобто пройшли повз попередження або
були заведені до нього. Об'єднувати чи ні — рішення людське (`AUTHORING §6`), тому список
лежить, а не виконується.

## sys-unix — можливі дублі й перекриття

Оцінювач C помітив, ставлячи оцінки:

| ймовірний дубль | наявна тема | що каже |
|---|---|---|
| `systemd-sysusers-and-sysctl-d` | `sysusers-declarative-accounts` | те саме, ширше й вужче |
| `ftrace-tracepoints` | `ftrace-kernel-tracing` | частина під цілим |

Окремо: **`classic-filters` перекриває чотири окремі теми** — `grep`, `sed`, `awk`,
`sort-and-uniq`. Тут дубль не пари, а зонтика над уже наявними темами: або зонтик має стати
оглядом із посиланнями, або чотири теми зайві. Рішення людське.

### sf-algorithms — підтверджено трьома оцінювачами незалежно

Усі три назвали `hash-table` найсильнішою темою книги. Двоє з трьох самі, без запитання,
винесли дублі окремим спостереженням; третій просто збив їх на Р1. Додаткові пари від
оцінювача A: `spatial-index` ↔ `r-tree`.

## ph-condensed — перекриття всередині розділу

| тема | розділ | сусіди, що її накривають |
|---|---|---|
| `shot-flicker-noise` | Власні шуми | `thermal-noise`, `shot-noise`, `flicker-noise` — усі три поруч |
| `ferromagnetism-domains` | Домени й гістерезис | `magnetic-domains`, `saturation-hysteresis` |

Перевірено по маніфесту: сусіди справді лежать у ТОМУ САМОМУ розділі. `shot-flicker-noise` —
це буквально дві сусідні теми, склеєні в назві однієї третьої.

### sys-unix — підтверджено всіма трьома

`classic-filters` як зонтик над `grep`/`sed`/`awk`/`sort-and-uniq` і пара
`sysusers-declarative-accounts` ↔ `systemd-sysusers-and-sysctl-d` названі незалежно
трьома оцінювачами. Оцінювач B додав ще дві пари «похідне від сусіда»:
`mptcp-path-managers` ↔ `multipath-tcp-mptcp` і
`ktls-hw-offload-and-enablement` ↔ `kernel-tls-record-layer`.

### ph-condensed — підтверджено двома

`shot-flicker-noise` названо дублем незалежно оцінювачами B і C: це дві сусідні теми
того самого розділу (`shot-noise`, `flicker-noise`), склеєні в назві третьої.

## sf-distributed — роздрібнення, а не поодинокі дублі

Тут інший масштаб проблеми. Двоє оцінювачів **незалежно** повернули майже однаковий перелік —
19 пар, і **всі 19 справді існують у маніфесті**; **13 із них лежать у ТОМУ САМОМУ розділі**.

Перевірено скриптом по маніфесту (`ОДИН РОЗДІЛ` = обидві теми в одному розділі):

| ОДИН РОЗДІЛ | пара |
|---|---|
| так | `poison-message` ↔ `dead-letter-queue` — карантин і мертва черга з двох боків |
| так | `load-shedding` ↔ `graceful-degradation-primary` — «плавна деградація» стоїть у назві першої |
| так | `replication-lag` ↔ `read-model-lag` |
| так | `replication-leader-follower` ↔ `multi-leader-replication` ↔ `quorum-and-leaderless` — парасолька накриває обидві сусідні |
| так | `gossip-dissemination` ↔ `gossip-pull-vs-push` |
| так | `idempotency` ↔ `idempotent-consumers-deep` ↔ `replay-protection-tactics` — одна тема в трьох слугах |
| так | `distributed-locks` ↔ `fencing-tokens` |
| так | `durable-workflows` ↔ `durable-workflow-cluster-under-load` |
| так | `message-bus` ↔ `message-bus-topology` ↔ `enterprise-service-bus` — одна шина на три статті |
| так | `vector-clocks` ↔ `vector-clocks-vs-crdt` |
| ні | `cache-stampede` ↔ `thundering-herd` — «Thundering herd» стоїть у назві першої |
| ні | `gossip-dissemination` ↔ `anti-entropy-repair` |
| ні | `saga-pattern` ↔ `orchestration-vs-choreography` |
| ні | `lamport-clocks` ↔ `clock-offset-drift` ↔ `timestamps` |
| ні | `vector-clocks-vs-crdt` ↔ `crdt` — середня тема складається з двох крайніх |

Обидва оцінювачі окремо назвали найдрібніше роздрібненими групи **«Плітки» (10 тем)** і
**«Транспорт повідомлень» (12)** — саме там зібралися одиниці й двійки.

Це вже не «дві теми випадково про одне», а системне роздрібнення однієї книги, і воно
прямо суперечить правилу проти роздрібнення, доданому в корпус 2026-08-28 (коміт `6463d0be6`).

## sys-plang-cpp — та сама хвороба, видна з назв

| ймовірний дубль | накриває | усі троє? |
|---|---|---|
| `std-typy-bez-kupy` | `span-contiguous`, `string-and-string-view`, `optional` — усі в тому самому розділі | 2 з 3 |
| `cpp26-features` | `static-reflection`, `contracts`, `p2300-senders-receivers` — заголовок оглядової теми складається з трьох власних тем книги | 2 з 3 |
| `future-promise` ↔ `async-and-packaged-task` | `async`/`packaged_task` — обгортки над promise/future | 3 з 3 |
| `core-guidelines` ↔ `gsl-support-library` | GSL існує лише як підпірка Guidelines | 3 з 3 |
| `coroutines` ↔ `std-generator` | генератор — окремий випадок корутини | 3 з 3 |
| `auto-type-deduction` ↔ `template-argument-deduction` | правила ті самі | 3 з 3 |
| `crtp` ↔ `deducing-this` | друге навмисно заміщає перше | 2 з 3 |
| `std-thread-jthread` ↔ `stop-token` | сенс jthread саме в stop_token | 2 з 3 |

## ⚠ Хиба методу, знайдена і виправлена 2026-08-28

Спершу оцінювачам подавали САМІ recheck-теми. Двоє з трьох на `sys-plang-cpp` через це
доповіли про «діру: немає теми про модель пам'яті й атоміки» — а тема **`std-atomic`
(«std::atomic і порядок пам'яті», розділ `memory-order`) існує**, просто вона `done` і в
список не потрапила. Сусідні теми через уявну діру дістали завищену оцінку.

Виправлено: вхід тепер містить УСЮ книгу, теми на оцінку позначені `*`, решта — контекст
без оцінки. Оцінюваний набір не змінився — це й далі рівно recheck-теми.

Оцінені старим входом (частка книги, яку бачив оцінювач): `sys-unix` 41%, `sys-dron` 43%,
`embedded` 58%, `sf-algorithms` 90%, `ph-condensed` 91%, `sf-distributed` 98%,
`sys-plang-cpp` 99%. Переоцінку не робили — рішення власника корпусу.

## sys-dron — 6 пар в одному розділі

Двоє оцінювачів незалежно, перевірено по маніфесту:

| ОДИН РОЗДІЛ | пара |
|---|---|
| так | `hlushinnia-gnss` ↔ `vyiavlennia-hlushinnia-za-pokaznykamy-pryimacha` — «як глушіння виглядає з боку приймача» і «виявлення за показниками приймача»; обидва назвали це найближчим дублем книги |
| так | `motor-mixer` ↔ `actuator-allocation` — мікшер це окремий випадок розподілу |
| так | `utrymannia-kursu-vysoty-i-pozytsii` ↔ `utrymannia-pozytsii-i-povernennia-na-liniiu` |
| так | `boustrophedon-coverage` ↔ `survey-grid-coverage` — покриття галсами двічі |
| так | `mavlink-param-protocol-model` ↔ `mavlink-param-tuning-and-diagnostics` |
| так | `mavlink-mission-items` ↔ `mavlink-commands` — спільний MAV_CMD |
| ні | `telemetry-stream` ↔ `stream-rates` · `vid-tochky-marshrutu-do-ustavky` ↔ `waypoint-route-sequencing` |

## hw-components — дублі ЧЕРЕЗ МЕЖУ статусів (це дав новий вхід із контекстом)

Двоє оцінювачів незалежно, перевірено по маніфесту. Тут уперше видно пари, де одна тема вже
написана, а друга ще чекає на письмо, — старий вхід (самі recheck) таких показати не міг:

| ОДИН РОЗДІЛ | пара | статуси |
|---|---|---|
| ні | `abs-max-ratings` ↔ `absolute-maximum-ratings` | **done ↔ pending** |
| так | `safe-operating-area` ↔ `soa-power-devices` | done ↔ done |
| так | `thermal-runaway` ↔ `bjt-thermal-runaway` | done ↔ done |
| так | `flash-cell-types` ↔ `nand-cell-levels` — обидві «SLC/MLC/TLC/QLC» | recheck ↔ done |
| так | `derating` ↔ `component-derating` (+ `power-derating` в іншому розділі) | recheck ↔ pending ↔ done |
| ні | `resistor-tolerance` ↔ `tolerance` | recheck ↔ pending |
| ні | `depletion-mode-mosfet` ↔ `mosfet-modes` | recheck ↔ done |
| так | `rtc-timekeeping` ↔ `rtc-calendar-time` | recheck ↔ recheck |
| так | `capacitor-esr-impedance` ↔ `dielectric-losses` — ESR у назві обох | recheck ↔ recheck |

**Найдорожчий випадок — `abs-max-ratings` [done] ↔ `absolute-maximum-ratings` [pending]:**
абревіатура вже написана, розшифровка стоїть у черзі на письмо. Написати її означає
заплатити за другу статтю про те саме.

Те саме з `derating`: три теми (`derating` recheck, `component-derating` pending,
`power-derating` done), причому перші дві в ОДНОМУ розділі.

## sf-security — ДОСЛІВНІ дублі, обидві статті НАПИСАНІ

Найгірший випадок за весь прохід. Два оцінювачі незалежно; звірено з маніфестом разом
із назвами. Усі три пари — **в одному розділі, обидві теми в статусі `recheck`,
тобто обидві вже написані**:

| слуг | статус | назва |
|---|---|---|
| `cryptographic-hash` | recheck | Криптографічні **геш**функції |
| `cryptographic-hash-functions` | recheck | Криптографічні **хеш**-функції |
| | | ↑ та сама назва, різниться лише написання «геш/хеш» |
| `rsa` | recheck | RSA |
| `rsa-cryptosystem` | recheck | Криптосистема RSA |
| `dnssec` | recheck | DNSSEC: підписи зони і ланцюг довіри до відповіді DNS |
| `dns-sec` | recheck | DNSSEC: цифровий підпис і ланцюг довіри в системі доменних імен |

Це не «дві теми про суміжне» — це одна тема, написана двічі, тричі поспіль. Заплачено
за шість статей там, де мало бути три.

Ще одна пара, дорога інакше: `flush-reload` [recheck, «Сайд-канал атаки Flush+Reload»]
↔ `cache-side-channel` [**pending**, «Кеш як побічний канал: Flush+Reload і Prime+Probe»] —
перша написана, друга стоїть у черзі на письмо й накриє першу цілком.

Сильні накладання в одному розділі: `keyed-hash-mac` ↔ `hmac` · `bt-pairing-security` ↔
`ble-security` · `tls` ↔ `tls-handshake` · `ataky-na-krystal` ↔
`zbiini-ataky-hlitchynh-dekapsuliatsiia-i-chomu`.

## ph-mechanics — усі в одному розділі

`proper-acceleration` ↔ `specific-force` (усі троє назвали найгострішим) · `mass` ↔ `weight` ·
`boundary-layer` ↔ `momentum-integral` · `material-fatigue` ↔ `cycle-counting-palmgren-miner` ·
`thrust-vs-weight` ↔ `statychna-i-dynamichna-tiaha`.

Окремо — **іменна пастка**: слуг `momentum` вкладений у `momentum-integral` по межі
сегмента. Поняття різні, але це рівно шаблон, на який лається `manifest-patch.js`.
Варто перейменувати на `boundary-layer-momentum-integral`.

## Локальний сканер — `scripts/dupescan.js`

Те, що оцінювачі знаходили руками, тепер рахується скриптом по ВСЬОМУ корпусу за нуль токенів.
Шість сигналів: вкладений слуг · збіг без дефісів · різниця лише в числі · той самий слуг в іншій
книзі · однакова назва теми · слово, що є ЛИШЕ у двох темах книги і становить ≥½ коротшого слуга.

Повний перелік — `_dupescan.md`. **1187 сильних сигналів, 447 із них в одному розділі.**

Щільність по книгах (пар на тему, книги від 20 тем):

| книга | пар | тем | % |
|---|--:|--:|--:|
| `com-devices` | 32 | 94 | 34.0 |
| `ph-quantum` | 16 | 46 | 33.7 |
| `com-medium` | 23 | 72 | 31.3 |
| `hw-analog` | 52 | 168 | 31.0 |
| `hw-components` | 71 | 255 | 27.8 |
| `hw-digital` | 32 | 122 | 26.2 |

Два налаштування, зроблені по ходу, обидва заміряні:
* нормалізація назв викидала однолітерні токени й зливала «І-складова» з «Д-складова» —
  виправлено, короткі токени збережено;
* правило «рідкісне спільне слово» без умови покриття давало 1600 сигналів замість 368;
  додано вимогу, щоб спільні слова становили ≥½ коротшого слуга — вийшло 1187, і серед них
  ловляться справжні пари на кшталт `gilbert-elliott-model` ↔ `gilbert-elliott-channel`,
  `viterbi-algorithm` ↔ `viterbi-decoder`, яких вкладеність слугів не бачить.

## Знахідки хвиль 3–5 (перевірені по маніфесту вибірково)

**`com-modulation`** — `gilbert-elliott-model` ↔ `gilbert-elliott-channel` · `ldpc` ↔ `ldpc-codes` ·
`viterbi-algorithm` ↔ `viterbi-decoder` · `composite-video` ↔ `cvbs-signal` · `crc` ↔ `crc-algorithm`.
Усі — в одному розділі, усі знайдені трьома оцінювачами незалежно.

**`com-medium`** — `transmission-line` ↔ `transmission-lines` (однина/множина) ·
`rs-485-multidrop-bus` ↔ `rs485-multidrop-bus` (дефіс) · трійка `antenna-feed` ↔
`antenna-feedline-matching-and-balun` ↔ `balun` (балун у назві всіх трьох) ·
`mdi-mdix` ↔ `auto-negotiation` (перша в назві містить «і авто-погодження») ·
`reflection-coefficient` ↔ `vswr` ↔ `return-loss` (одна величина в трьох записах).

**`com-devices`** — найщільніша книга корпусу (34% тем мають пару). Гроно розтягування такту
з ЧОТИРЬОХ тем: `clock-stretch-arbitration` ↔ `i2c-bus-timing` ↔
`i2c-clock-stretching-timing-budget` ↔ `i2c-clock-stretching-hardware`. Гроно таймінгу SPI теж
із чотирьох: `spi-speed` ↔ `spi-timing` ↔ `spi-cs-timing` ↔ `spi-mode-timing-and-faults`.
Плюс `i2c` [готова] ↔ `i2c-bus` з тим самим заголовком · `baud-vs-bitrate` ↔ `baud-rate` ·
`usb-device-basics` переказує чотири готові теми, перелічені в її ж підзаголовку.

**`hw-sensing`** — `4wire-resistance` ↔ `kelvin-connection` (усі троє назвали найчистішим) ·
`avalanche-photodiode` ↔ `spad-photon-counting` · `power-monitor` ↔ `current-monitor` ↔
`mikroskhema-lichylnyk-enerhii` ↔ `kilovat-hodyna`.

**`com-signal`** — `nyquist-aliasing` ↔ `sampling-theorem` ↔ `aliasing` (три теми на одне) ·
`dft` ↔ `dft-spectrum` · `discrete-cosine-transform` ↔ `dct` (DCT заведено двічі в різних групах) ·
`rtk-integer-ambiguity` ↔ `lambda-method-rtk` · `visual-inertial-odometry` ↔ `msckf-odometry`.

**`progarch`** (курс) — інший різновид: пари не в одному розділі, а РОЗКИДАНІ ПО ТОМАХ, і тому
невидимі зсередини кожного. «Коли ліцензія міняється під тобою» ↔ «Ліцензія, що змінилася під
тобою» · «Приймання чужої роботи» ↔ «Приймання системи від підрядника» · «Клієнт, якого ти не
оновиш» ↔ «…під час переїзду» · «Дублі й переупорядкування як норма» ↔ «Вкидання дубля й
переупорядкування».

**`progarch` — збій нумерації, не дубль:** `capstone-scale-secure-ops` називається «Капстон,
крок 4», і `capstone-peer-review` теж «Капстон, крок 4», хоча між ними стоїть
`capstone-org-evolution` = «крок 5». Ревізія має бути кроком 6.

## Знахідка з атрибуції — `ph-electromagnetism/hist-lenz-law`

Оцінювач зауважив при розкладці: **Емілій Ленц — балтійський німець із Дорпата (Тарту)**,
підданий Російської імперії, професор Петербурзького університету. Писати «російський
фізик» означає стерти і його етнічну, і його територіальну належність.

Це рівно той клас імперської атрибуції, від якого треба берегтися при письмі історичних
вставок. Варте окремого проходу по всіх `hist-` вставках корпусу, де фігурують науковці
Російської імперії й СРСР.
