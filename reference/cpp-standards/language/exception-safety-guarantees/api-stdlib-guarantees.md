# 📋 Обіцянки стандартної бібліотеки: операція за операцією

Ця довідка відповідає на одне питання й лише на нього: **що лишиться від об'єкта, якщо конкретна операція стандартної бібліотеки вилетить винятком** — дослівними формулюваннями стандарту, з умовами на тип елемента й з позначкою випуску там, де формулювання переписували. Тримати таблиці в голові не треба; треба знати, що обіцянка належить не контейнерові, а трійці «контейнер + операція + тип елемента», і вміти знайти потрібний рядок.

## Як читати таблиці

Стандарт не називає рівнів. Слів «basic guarantee» чи «strong guarantee» у специфікаціях операцій немає — там стоять три канцелярські звороти, і кожен означає рівно одне:

| Зворот стандарту | Що обіцяно | Позначка нижче |
|---|---|---|
| `there are no effects` / `has no effect` | стан такий самий, як до виклику | **S** — сильна |
| `Throws: Nothing` або [`noexcept`](book:cpp-standards/noexcept) у сигнатурі | виняток звідси не вилітає взагалі | **N** — не кидає |
| нічого з переліченого | об'єкт цілий, інваріанти тримаються, значення не визначене | **Б** — базова |

Позначка **Б** ніде в стандарті не записана: вона означає «окремої обіцянки для цієї операції немає», і саме її отримує все, що не потрапило в перші два рядки. Тому пошук у стандарті виглядає так: знайти операцію, прочитати її абзац `Remarks:` і `Throws:` — і якщо там немає ні «no effects», ні «Nothing», то більшого ніхто не обіцяв.

## Наскрізні правила бібліотеки

| Правило | Дослівно | Де записано |
|---|---|---|
| Деструктори бібліотеки не кидають | «Destructor operations defined in the C++ standard library shall not throw exceptions. Every destructor in the C++ standard library shall behave as if it had a non-throwing exception specification.» | `[res.on.exception.handling]/3` |
| Функції C-бібліотеки не кидають | «Functions from the C standard library shall not throw exceptions except when such a function calls a program-supplied function that throws an exception.» | `[res.on.exception.handling]/2` |
| Реалізація має право посилити обіцянку | «An implementation may strengthen the exception specification for a non-virtual function by adding a non-throwing exception specification.» | `[res.on.exception.handling]/5` |
| Деструктор *вашого* типу-елемента теж не має права кидати | вимога `Cpp17Destructible`: «no exception is propagated» | `[utility.arg.requirements]`, таблиця `Cpp17Destructible` |
| Звільнення пам'яті не кидає, виділення — може | `a.deallocate(p, n)` — «Throws: Nothing»; про `a.allocate(n)` сказано, що вона «may throw an appropriate exception» | `[allocator.requirements.general]` |

У цьому переліку варто помітити те, чого в ньому **немає**: жодного речення на кшталт «бібліотека не втрачає ресурсів». Підрозділ стандарту, що регулює винятки в бібліотеці наскрізно, складається рівно з п'яти вимог (суть трьох із них — у перших рядках таблиці), і жодна не говорить ні про витоки, ні про рівні гарантій. Мінімум «нічого не витекло» — не окрема обіцянка, а наслідок трьох речей одразу: кожну операцію описано поіменно, деструктори не кидають, `deallocate` не кидає. Отже, розкрутка стека всередині бібліотечної операції завжди має чим прибрати за собою.

Рядок про право реалізації посилити обіцянку — практична пастка. `noexcept`, який ви бачите у власному заголовку `<vector>`, може бути щедрішим за те, що вимагає стандарт: код, зібраний іншою реалізацією, цієї щедрості не успадкує. Спиратися варто на текст стандарту, а не на заголовок під рукою.

Передостанній рядок стосується вас, а не бібліотеки. Якщо деструктор вашого типу здатен кинути, контейнер із таким елементом не порушує жодної обіцянки — просто всі обіцянки, які ви прочитаєте нижче, його вже не стосуються, бо тип не задовольняє вимог, за яких їх дано.

## Спільне правило всіх контейнерів

Найголовніший абзац у всьому питанні — `[container.reqmts]/66`. Він дає обіцянки одразу всім контейнерам розділу, і всі окремі таблиці нижче — це або він, або поіменне послаблення до нього.

| Пункт | Дослівно | Позначка |
|---|---|---|
| 66.1 | «If an exception is thrown by an `insert()` or `emplace()` function while inserting a single element, that function has no effects.» | **S** |
| 66.2 | «If an exception is thrown by a `push_back()`, `push_front()`, `emplace_back()`, or `emplace_front()` function, that function has no effects.» | **S** |
| 66.3 | «No `erase()`, `clear()`, `pop_back()` or `pop_front()` function throws an exception.» | **N** |
| 66.4 | «No copy constructor or assignment operator of a returned iterator throws an exception.» | **N** |
| 66.5 | «No `swap()` function throws an exception.» | **N** |
| 66.6 | «No `swap()` function invalidates any references, pointers, or iterators referring to the elements of the containers being swapped.» (примітка стандарту: ітератор `end()` не посилається на елемент, тож на нього обіцянка не поширюється) | — |

Абзац починається словами «Unless otherwise specified», і далі в дужках перелічено, **де саме** правило переписують: `[associative.reqmts.except]`, `[unord.req.except]`, `[deque.modifiers]`, `[inplace.vector.modifiers]` і `[vector.modifiers]`. П'ять адрес — п'ять місць, де загальна обіцянка звужується. Це і є повний список винятків; шукати послаблення деінде не треба.

Пункт 66.6 не про винятки, а про дійсність ітераторів — його вставлено поруч, бо на `swap` спираються обидві обіцянки одночасно, і плутати їх легко.

Обидва рядки про `swap` мають передумову, від якої `noexcept` не рятує: обмін двох контейнерів визначено, лише якщо `allocator_traits<A>::propagate_on_container_swap::value` істинне **або** алокатори цих контейнерів рівні. Порушите — і це вже [невизначена поведінка](book:programming/undefined-behavior), а не виняток; `noexcept` у сигнатурі стосується винятків, а не передумов. Що саме означають ці риси й коли вони справджуються — у темі про [власні алокатори](book:cpp-standards/custom-allocators).

## vector

| Операція | Гарантія | Дослівна умова | Де |
|---|---|---|---|
| `push_back`, `emplace_back`, вставка одного елемента в кінець | **S**, якщо `T` є `Cpp17CopyInsertable` **або** `is_nothrow_move_constructible_v<T>` істинне; інакше — «the effects are unspecified» | «If an exception is thrown while inserting a single element at the end and `T` is `Cpp17CopyInsertable` or `is_nothrow_move_constructible_v<T>` is `true`, there are no effects.» | `[vector.modifiers]/2` (з C++14) |
| `insert`/`emplace` одного елемента **не** в кінець | **S** проти всього, крім кидка самого `T` | «If an exception is thrown other than by the copy constructor, move constructor, assignment operator, or move assignment operator of `T` … there are no effects.» | `[vector.modifiers]/2` |
| `insert` діапазону, `insert_range`, `assign`, `assign_range` | **Б** | з-під **S** виведено ще й «or by any `InputIterator` operation» | `[vector.modifiers]/2` |
| `reserve(n)` | **S**, крім кидка конструктора переміщення не-`Cpp17CopyInsertable` `T`; плюс «Throws: `length_error` if `n > max_size()`» | «If an exception is thrown other than by the move constructor of a non-`Cpp17CopyInsertable` `T`, there are no effects.» | `[vector.capacity]/5,7` |
| `shrink_to_fit()` | **S** з тією самою умовою | те саме формулювання | `[vector.capacity]/11` |
| `resize(sz)` | **S** з тією самою умовою | те саме формулювання | `[vector.capacity]/16` |
| `resize(sz, const T& c)` | **S** беззастережно | «If an exception is thrown, there are no effects.» | `[vector.capacity]/19` |
| `erase`, `pop_back` | **N**, крім присвоєння `T` | «Throws: Nothing unless an exception is thrown by the assignment operator or move assignment operator of `T`.» | `[vector.modifiers]/5` |
| `clear()` | **N** | загальне правило 66.3 | `[container.reqmts]/66.3` |
| `operator=(const vector&)`, `assign` | **Б** | окремої обіцянки немає | — |
| `operator=(vector&&)` | **N**, якщо істинне `propagate_on_container_move_assignment::value` **або** `is_always_equal::value` | умова стоїть просто в сигнатурі | `[vector.overview]` (з C++17) |
| `swap` | **N**, якщо істинне `propagate_on_container_swap::value` **або** `is_always_equal::value` | сама вимога «no swap function throws» діяла й до C++17 | `[container.reqmts]/66.5`, `[vector.overview]` |
| `at(n)` | кидає `out_of_range`, нічого не змінює | — | — |

Умова в першому рядку виглядає дивно, доки не спитати, що вектор робить при перевиділенні. Він мусить перенести всі наявні елементи в новий буфер, і саме це перенесення є фіксацією операції: якщо воно провалиться посередині, обидва буфери неповні. Тому реалізація питає в типу, чи його конструктор переміщення позначено `noexcept` (це робить `std::move_if_noexcept`), і в разі «ні» переносить **копіюванням** — старий буфер тоді лишається цілим і слугує точкою відкату. Отже, з двох варіантів умови працює або той, або той: або тип копійовний і є куди відкотитися, або переміщення не кидає і провалу нема де статися. Тип, який не копіюється й має кидкий конструктор переміщення, не лишає вектору жодного виходу — звідси «the effects are unspecified». Механіку самого переміщення розібрано в темі про [семантику переміщення](book:cpp-standards/move-semantics), а риса `is_nothrow_move_constructible` — одна зі стандартних [рис типів](book:cpp-standards/type-traits), тобто запитання до типу, на яке відповідають під час компіляції.

> 🔧 **Навіщо це.** Читати цю таблицю треба з кінця: спочатку подивіться на свій `T`, потім на рядок. Той самий `push_back` для `std::string` дає **S**, для типу з `noexcept`-переміщенням — **S**, а для типу, який заборонив копіювання й забув `noexcept` на переміщенні, — не дає нічого. Одна пропущена позначка в чужому класі змінює обіцянку вашого коду.

Зверніть увагу й на другий рядок: вставка одного елемента **всередину** вектора формально не потрапляє під умову «at the end», тож для неї працює лише перше речення — сильна проти невдалого виділення пам'яті, базова проти кидка самого `T`.

## deque

| Операція | Гарантія | Дослівна умова | Де |
|---|---|---|---|
| `push_front`, `push_back`, `emplace_front`, `emplace_back`, вставка одного елемента з будь-якого кінця | **S** беззастережно | «If an exception is thrown while inserting a single element at either end, there are no effects.» | `[deque.modifiers]/3` |
| `insert` усередину | **S** проти всього, крім кидка самого `T` | «If an exception is thrown other than by the copy constructor, move constructor, assignment operator, or move assignment operator of `T`, there are no effects.» | `[deque.modifiers]/3` |
| вставка всередину, коли `T` не `Cpp17CopyInsertable` і його переміщення кидає | ефекти не визначені | «Otherwise, if an exception is thrown by the move constructor of a non-`Cpp17CopyInsertable` `T`, the effects are unspecified.» | `[deque.modifiers]/3` |
| `erase`, `pop_front`, `pop_back` | **N**, крім присвоєння `T` | «Throws: Nothing unless an exception is thrown by the assignment operator of `T`.» | `[deque.modifiers]/5` |
| `clear()` | **N** | загальне правило 66.3 | `[container.reqmts]/66.3` |

Різниця з вектором в одному рядку — і вона не випадкова. Зростання дека з кінця не рухає наявних елементів: додається новий блок, старі лишаються на місці. Фіксації, здатної провалитися на середині, тут просто немає, тому й умови на `T` немає — обіцянка беззастережна.

## list і forward_list

| Операція | Гарантія | Дослівно | Де |
|---|---|---|---|
| `insert`, `emplace`, `push_front`, `push_back` | **S** | «Does not affect the validity of iterators and references. If an exception is thrown, there are no effects.» | `[list.modifiers]/2` |
| `erase` | **N** | «Throws: Nothing.» | `[list.modifiers]/4` |
| `clear()`, `pop_front`, `pop_back` | **N** | загальне правило 66.3 | `[container.reqmts]/66.3` |

Формулювання тут найкоротше в усій бібліотеці, бо структура не лишає місця для умов: вузол виділяють і будують у ньому елемент, поки список про новий вузол ще нічого не знає, а потім переставляють два вказівники. Ризикована половина роботи фізично відокремлена від фіксації.

## map, set, multimap, multiset

Три абзаци `[associative.reqmts.except]` — це весь текст стандарту про винятки в упорядкованих асоціативних контейнерах.

| Операція | Гарантія | Дослівно | Де |
|---|---|---|---|
| `insert`/`emplace` одного елемента | **S** проти **будь-якої** операції, включно з кидком `Compare` | «if an exception is thrown by any operation from within an insert or emplace function inserting a single element, the insertion has no effect» | `[associative.reqmts.except]/2` |
| `operator[]`, `try_emplace` | **S** | `operator[](x)` визначено як «Equivalent to: `return try_emplace(x).first->second;`», тобто це вставка одного елемента | `[map.access]`, `[associative.reqmts.except]/2` |
| `insert_or_assign` | **S** лише на гілці вставки | коли ключ уже є, вставки не відбувається — див. нижче | `[associative.reqmts.except]/2` |
| `insert` діапазону, `insert(initializer_list)` | **Б** | обіцянку дано «inserting a single element», не більше | — |
| `erase(k)` | **N**, крім кидка `Compare` | «`erase(k)` does not throw an exception unless that exception is thrown by the container's `Compare` object (if any)» | `[associative.reqmts.except]/1` |
| `erase(q)`, `clear()` | **N** | «no `clear()` function throws an exception» | `[associative.reqmts.except]/1` |
| `swap` | **N**, крім обміну `Compare` | «no `swap` function throws an exception unless that exception is thrown by the swap of the container's `Compare` object (if any)» | `[associative.reqmts.except]/3` |
| `merge(a2)` | **N**, крім кидка компаратора | «Throws: Nothing unless the comparison object throws.» | `[associative.reqmts]` |
| `extract(k)`, `extract(q)` | окремої обіцянки немає | абзацу `Throws:` у специфікації немає | `[associative.reqmts]` |

Один рядок таблиці легко прочитати щедріше, ніж написано. `insert_or_assign` має дві гілки: коли ключа немає — вона вставляє, і обіцянка на неї поширюється; коли ключ уже є — вона **присвоює**, а жодної вставки не відбувається, тож фразі «the insertion has no effect» просто немає до чого застосуватися. Якщо присвоєння значення кине, ви лишитеся з напівприсвоєним значенням у контейнері — і це не порушення стандарту, а точне його читання.

Так само варто помітити слова «by **any** operation» у пункті 2: на відміну від вектора, тут із-під сильної гарантії не виведено навіть кидок компаратора. Дерево ще не змінене, коли компаратор шукає місце, — тож провал пошуку нічого не псує.

## unordered_map, unordered_set і решта хеш-контейнерів

| Операція | Гарантія | Дослівно | Де |
|---|---|---|---|
| `insert`/`emplace` одного елемента | **S**, **крім кидка самої хеш-функції** | «if an exception is thrown by any operation other than the container's hash function from within an insert or emplace function inserting a single element, the insertion has no effect» | `[unord.req.except]/2` |
| `rehash(n)` | **S**, крім кидка хеш-функції або функції порівняння | «if an exception is thrown from within a `rehash()` function other than by the container's hash function or comparison function, the `rehash()` function has no effect» | `[unord.req.except]/4` |
| `reserve(n)` | те саме, що `rehash` | «Equivalent to `a.rehash(ceil(n / a.max_load_factor()))`» | `[unord.req.general]` |
| `erase(k)` | **N**, крім кидка `Hash` або `Pred` | «`erase(k)` does not throw an exception unless that exception is thrown by the container's `Hash` or `Pred` object (if any)» | `[unord.req.except]/1` |
| `clear()` | **N** | «no `clear()` function throws an exception» | `[unord.req.except]/1` |
| `swap` | **N**, крім обміну `Hash` або `Pred` | «no `swap` function throws an exception unless that exception is thrown by the swap of the container's `Hash` or `Pred` object (if any)» | `[unord.req.except]/3` |

Виняток «other than the container's hash function» — найширша дірка в гарантіях контейнерів, і ширша вона, ніж здається на перший погляд. Вставка може потягнути за собою перебудову таблиці (коли після додавання елемента порушується межа `max_load_factor`), а перебудова заново хешує **кожен** наявний елемент. Отже, кидок вашої хеш-функції може статися не на новому елементі, а на сотому старому — посеред переселення, коли частина елементів уже в новій таблиці, а частина в старій. Стандарт у цьому місці не обіцяє нічого.

> 🔧 **Навіщо це.** Практичний висновок з одного рядка: **хеш-функтор має бути `noexcept`**. Хеш, що виділяє пам'ять або кидає з якоїсь іншої причини, знімає з `unordered_*` усі обіцянки, які ви щойно прочитали, — і знімає їх мовчки, без жодного попередження компілятора.

## basic_string

`basic_string` — рідкісний випадок, коли обіцянку дано одразу на весь клас, а не на окремі операції:

| Правило | Дослівно | Де |
|---|---|---|
| **S** на всі члени класу | «If any member function or operator of `basic_string` throws an exception, that function or operator has no other effect on the `basic_string` object.» | `[string.require]/2` |
| Перевищення `max_size()` | «If any operation would cause `size()` to exceed `max_size()`, that operation throws an exception object of type `length_error`.» | `[string.require]/1` |

Перевіряти окремі операції `std::string` не треба: сильну гарантію дано всім членам і операторам класу гуртом. Букву формулювання, щоправда, варто прочитати точно — воно говорить про **члени** класу; вільні функції на кшталт `operator+` під нього формально не підпадають (хоч вони й будують новий рядок, не чіпаючи аргументів). Про самі типи роботи з текстом — у темі про [string і string_view](book:cpp-standards/string-and-string-view).

## Алгоритми

У цій таблиці немає жодного рядка **S**, і це не недогляд: у специфікаціях алгоритмів `<algorithm>` фрази «there are no effects» немає ніде.

| Операція | Що обіцяно |
|---|---|
| `sort`, `stable_sort`, `nth_element` — кидок компаратора | **Б**: діапазон лишається діапазоном дійсних об'єктів у невизначеному порядку; жодного відкату перестановок |
| `remove`, `remove_if`, `unique` — кидок присвоєння з переміщення | **Б**: у діапазоні можуть лишитися дублікати й переміщені-з об'єкти |
| `copy`, `transform` у діапазон-приймач | **Б**: частина приймача вже перезаписана |
| `for_each` із кидким функтором | виняток просто проходить назовні; скільки елементів алгоритм устиг обробити — не визначено |

Причина спільна: алгоритм працює з чужою пам'яттю через ітератори й не володіє нічим, що можна було б відкотити. Копії всього діапазону він не робить (це коштувало б стільки ж, скільки сам алгоритм), а без копії лінії фіксації скласти нема з чого. Тому правило просте: **транзакційність діапазону — робота того, хто викликає**. Хочете відкат — робіть алгоритм над копією і міняйте місцями після успіху. Про самі алгоритми — у темі про [алгоритми STL](book:cpp-standards/stl-algorithms).

Окремо стоять паралельні версії, і там правило жорсткіше:

| Правило | Дослівно | Де |
|---|---|---|
| Нема тимчасової пам'яті на розпаралелювання | «if temporary memory resources are required for parallelization and none are available, the algorithm throws a `bad_alloc` exception» | `[algorithms.parallel.exceptions]/1` |
| Виняток із функції доступу до елемента | «if the invocation of an element access function exits via an uncaught exception, the behavior is determined by the execution policy» | `[algorithms.parallel.exceptions]/2` |
| Що каже політика | «if the invocation of an element access function exits via an exception, `terminate` is invoked» | `[execpol.seq]`; решта стандартних політик формулюють це так само |

Тобто виняток із компаратора чи предиката, переданого в паралельний алгоритм, — це не помилка, яку можна перехопити, а смерть процесу. Про самі політики виконання — у темі про [паралельні алгоритми](book:cpp-standards/parallel-algorithms).

## Розумні вказівники

| Операція | Гарантія | Дослівно | Де |
|---|---|---|---|
| `shared_ptr(Y* p)` | якщо конструктор кине (не вистачило пам'яті на керівний блок), сирий вказівник не витече | «If an exception is thrown, `delete p` is called when `T` is not an array type, `delete[] p` otherwise.» | `[util.smartptr.shared.const]/6` |
| `shared_ptr(Y* p, D d)` | те саме, але прибирання робить переданий вами `d` | «If an exception is thrown, `d(p)` is called.» | `[util.smartptr.shared.const]/11` |
| обидва — що саме кидають | `bad_alloc` або виняток реалізації | «Throws: `bad_alloc`, or an implementation-defined exception when a resource other than memory cannot be obtained.» | `[util.smartptr.shared.const]/8,13` |
| `unique_ptr` — усі операції | **N** | вказівник просто переставляють | — |

Перший рядок означає більше, ніж здається: `shared_ptr` бере володіння **до** того, як може провалитися, — тому конструктор, який не встиг створити керівний блок, усе одно зобов'язаний знищити переданий об'єкт. Це рідкісний випадок, коли функція прибирає за аргументом, який їй не вдалося прийняти. Про самі лічильники посилань — у темі про [shared_ptr і weak_ptr](book:cpp-standards/shared-weak-ptr).

## Що означає «no effects» — і чого воно не означає

Означає рівно одне: після винятку стан об'єкта такий самий, яким був перед викликом. Не означає при цьому чотирьох речей, які цій фразі регулярно приписують:

- **Не означає, що ітератори лишилися дійсними.** Це окремий контракт, і напрямок у нього протилежний: `reserve` дає **S** при невдачі й робить недійсними геть усі ітератори при **успіху**.
- **Не означає обіцянки про аргументи.** Якщо ви передали елемент через `std::move`, а операція провалилася, стан вашого джерела описується правилами переміщення, а не гарантією контейнера.
- **Не означає нічого про побічні дії типу `T`.** Лічильники, журнали, файли, які встиг зачепити конструктор елемента, — поза межами обіцянки; вона стосується контейнера.
- **Не поширюється за межі однієї операції.** Два виклики з **S** поспіль дають лише **Б** для їхньої пари.

Записана обіцянка завжди в одному з двох місць: або в абзаці `Remarks:` конкретної операції, або в спільному `[container.reqmts]/66`. Сам абзац `Throws:` за визначенням `[structure.specifications]` перелічує «any exceptions thrown by the function, and the conditions that would cause the exception» — тобто **які** винятки, а не **що після них лишиться**; «no effects» ніколи не стоїть у `Throws:`, тільки в `Remarks:`.

## Хронологія формулювань

| Випуск | Що змінилося |
|---|---|
| **C++03** | загальне правило контейнерів уже давало `push_back()`/`push_front()` беззастережне «no effects»; переміщення в мові ще не було, тож і умов на тип не було |
| **C++11** | з'явився конструктор переміщення, а з ним у `[vector.modifiers]` — фраза «If an exception is thrown by the move constructor of a non-`CopyInsertable` `T`, the effects are unspecified». Оскільки `[vector.modifiers]` стоїть у переліку «unless otherwise specified», ця фраза перебила загальне правило, і `push_back` вектора тихо втратив те, що мав у C++03. Заразом у загальному пункті забули згадати нові `emplace_back`/`emplace_front`. Деструктори стали неявно `noexcept` |
| **C++14** | LWG-питання **2252** «Strong guarantee on `vector::push_back()` still broken with C++11?» (відкрито 2013-04-21, вирішено зі статусом C++14) дописало три речі: у `[vector.modifiers]` — умову «`T` is `CopyInsertable` or `is_nothrow_move_constructible<T>::value` is `true`», у `[deque.modifiers]` — «If an exception is thrown while inserting a single element at either end, there are no effects», а в загальний пункт контейнерів — `emplace_back()` і `emplace_front()` |
| **C++17** | з'явилася риса `allocator_traits<A>::is_always_equal`, і `swap` та присвоєння переміщенням контейнерів отримали видиму в сигнатурі умову `noexcept(...)`. У синопсисі C++11 і C++14 стояло просто `void swap(vector&);`, а вимога «no `swap()` function throws an exception» жила лише в тексті вимог — тобто вимога існувала й до C++17, а от **перевірити** її з коду через `noexcept(...)` стало можливо тільки з C++17 |
| **C++20** | іменовані вимоги перейменовано з префіксом: `CopyInsertable` → `Cpp17CopyInsertable`, `Destructible` → `Cpp17Destructible` — щоб прості імена звільнилися під концепти. Суть вимог та сама |
| **чинний проєкт** | до переліку послаблень загального правила додано `[inplace.vector.modifiers]` — разом із самим `inplace_vector` |

Читати цю хронологію варто з одним практичним висновком: обіцянки бібліотеки — не константа, а текст, який править комітет через LWG-питання, і виправлення такого питання діє **заднім числом** на вже випущений стандарт. Саме тому реалізації давно поводяться так, як написано в рядку C++14, навіть коли ви компілюєте з `-std=c++11`. Як влаштований цей механізм правок — у темі про [процес стандартизації](book:cpp-standards/standardization-process).
