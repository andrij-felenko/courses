# ⚙️ Робочий DAO: два джерела, нуль бази в тесті

Візьмімо крихітну ділову задачу й доведімо її від інтерфейсу до працюючого тесту. Раз на день застосунок має скласти **дайджест погодження**: за кожним оплаченим замовленням — рядок «пошта власника → сума», щоб надіслати відповідальним зведення «хто на скільки накупив». Даних два роди: користувачі й замовлення. Питань теж два: які замовлення оплачені й хто їхній власник.

До цієї задачі ми ставимо три вимоги, і кожна — привід для DAO. Перша: код мусить працювати **однаково** над реальною реляційною базою в проді й над мапою в пам'яті в тесті. Друга: жодна `SQLException` не сміє витекти в бізнес-код — застосунок не має знати, що внизу JDBC. Третя: тест на дайджест мусить бігати **без бази** — швидко й передбачувано, щоб таких тестів були тисячі.

Зберемо все з нуля — носії даних, два інтерфейси, дві реалізації над різними джерелами, фабрику, що обирає джерело за конфігом, і власний виняток на межі. А потім навмисно зламаємо: покажемо, як та сама абстракція тихо стріляє сотнею запитів і як протікає джерело, яке мала сховати.

## Що будуємо

Сім деталей, і кожна робить одне: **носії даних** (плоскі записи), **два інтерфейси** DAO (контракти), **реалізації над базою**, **реалізації в пам'яті**, **фабрика** (звідки береться реалізація), **власний виняток** (щоб механізм не тік), **сервіс і тест** (заради чого все).

Почнемо з того, чим DAO обмінюється зі світом, — з плоских записів. Ніякої поведінки, самі поля: один — користувач, другий — замовлення.

```java
record UserRow(long id, String email, String role, boolean active) {}
record OrderRow(long id, long userId, String status, long cents) {}
```

Далі — самі контракти. `UserDao` уміє знайти користувача, знайти за роллю, **знайти купку за списком id** (це знадобиться проти N+1) і змінити. `OrderDao` вужчий — нам треба лише вибирати замовлення за станом.

```java
interface UserDao {
    Optional<UserRow> findById(long id);
    List<UserRow> findByRole(String role);
    List<UserRow> findByIds(Collection<Long> ids);   // одразу пачку, не по одному
    void insert(UserRow u);
    void update(UserRow u);
    void delete(long id);
}

interface OrderDao {
    List<OrderRow> findByStatus(String status);
    void insert(OrderRow o);
}
```

Одна дрібниця тут навмисна: `findById` повертає `Optional<UserRow>`, а не `UserRow`, який міг би бути `null`. «Немає такого користувача» — це нормальний результат запиту, а не збій; коли він виражений типом, викликач не забуде його обробити, і `NullPointerException` не прилетить через три шари вгорі, де його вже не пов'язати з відсутнім рядком.

## Реалізація над базою

Тепер клас, якому **дозволено** знати про SQL, драйвер і з'єднання, — бо в цьому вся його робота. `SqlUserDao` тримає `DataSource` (пул з'єднань) і перекладає кожен метод контракту на запит.

```java
class SqlUserDao implements UserDao {
    private final DataSource ds;
    SqlUserDao(DataSource ds) { this.ds = ds; }

    public List<UserRow> findByRole(String role) {
        String sql = "SELECT id, email, role, active FROM users "
                   + "WHERE role = ? ORDER BY id";
        try (Connection c = ds.getConnection();
             PreparedStatement st = c.prepareStatement(sql)) {
            st.setString(1, role);                       // параметр, а не склейка рядка
            try (ResultSet rs = st.executeQuery()) {
                List<UserRow> out = new ArrayList<>();
                while (rs.next()) out.add(map(rs));
                return out;
            }
        } catch (SQLException e) {
            throw new DataAccessException("findByRole(" + role + ")", e);
        }
    }

    public List<UserRow> findByIds(Collection<Long> ids) {
        if (ids.isEmpty()) return List.of();             // порожній список — не ходити в базу
        String marks = ids.stream().map(x -> "?").collect(joining(", "));
        String sql = "SELECT id, email, role, active FROM users "
                   + "WHERE id IN (" + marks + ") ORDER BY id";
        try (Connection c = ds.getConnection();
             PreparedStatement st = c.prepareStatement(sql)) {
            int i = 1;
            for (Long id : ids) st.setLong(i++, id);
            try (ResultSet rs = st.executeQuery()) {
                List<UserRow> out = new ArrayList<>();
                while (rs.next()) out.add(map(rs));
                return out;
            }
        } catch (SQLException e) {
            throw new DataAccessException("findByIds", e);
        }
    }

    public void insert(UserRow u) {
        String sql = "INSERT INTO users(id, email, role, active) VALUES (?, ?, ?, ?)";
        try (Connection c = ds.getConnection();
             PreparedStatement st = c.prepareStatement(sql)) {
            st.setLong(1, u.id());
            st.setString(2, u.email());
            st.setString(3, u.role());
            st.setBoolean(4, u.active());
            st.executeUpdate();
        } catch (SQLException e) {
            throw new DataAccessException("insert(" + u.id() + ")", e);
        }
    }

    // findById, update, delete — так само над цим самим SQL
    // ...

    private static UserRow map(ResultSet rs) throws SQLException {
        return new UserRow(rs.getLong("id"), rs.getString("email"),
                           rs.getString("role"), rs.getBoolean("active"));
    }
}
```

Три дрібниці варті ока, бо кожна виправляє типову помилку. Значення підставляються через `?` (`st.setString`, `st.setLong`), а не вклеюються в текст запиту рядком — інакше пошта на кшталт `'; DROP TABLE users; --` стала б командою, а не даними. У `findByIds` динамічний лише **скільки** знаків питання, самі значення все одно параметри — тож `IN (...)` теж безпечний. І кожен `catch (SQLException e)` **не ковтає** збій, а перевидає власним `DataAccessException`, передаючи оригінал причиною, — механізм зупиняється на межі DAO.

Ось цей виняток. Він навмисно **неперевірний** (`extends RuntimeException`): якби він був checked, він знову змусив би кожен метод вище оголошувати `throws` — і знання про те, що внизу база, знову протекло б угору, тепер уже через сигнатури.

```java
public class DataAccessException extends RuntimeException {
    public DataAccessException(String op, Throwable cause) {
        super("доступ до даних не вдався: " + op, cause);   // причину НЕ губимо
    }
}
```

Передати `cause` — не косметика. Він тягне за собою повний стек первісної `SQLException`: код помилки бази, SQLState, конкретний рядок драйвера. Загорни без причини (`new DataAccessException("...")`) — і замість «унікальний ключ порушено на вставці замовлення 42» діагностика перетвориться на голе «доступ не вдався», а справжня біда лишиться в проковтнутому стеку.

`OrderDao` над базою — дзеркало того самого; наведу лиш його єдиний метод, бо решта така сама.

```java
class SqlOrderDao implements OrderDao {
    private final DataSource ds;
    SqlOrderDao(DataSource ds) { this.ds = ds; }

    public List<OrderRow> findByStatus(String status) {
        String sql = "SELECT id, user_id, status, cents FROM orders "
                   + "WHERE status = ? ORDER BY id";
        try (Connection c = ds.getConnection();
             PreparedStatement st = c.prepareStatement(sql)) {
            st.setString(1, status);
            try (ResultSet rs = st.executeQuery()) {
                List<OrderRow> out = new ArrayList<>();
                while (rs.next())
                    out.add(new OrderRow(rs.getLong("id"), rs.getLong("user_id"),
                                         rs.getString("status"), rs.getLong("cents")));
                return out;
            }
        } catch (SQLException e) {
            throw new DataAccessException("findByStatus(" + status + ")", e);
        }
    }

    public void insert(OrderRow o) { /* INSERT ... як у SqlUserDao */ }
}
```

Тепер найгостріше в реалізації над базою — **керування ресурсами**. З'єднання, підготований запит і курсор треба закрити завжди, зокрема коли посеред читання летить виняток. У Java це робить `try`-з-ресурсами, у Python — контекст-менеджер `with`. Ідея одна, форма різна — гляньмо `findById` у двох мовах поруч.

:::tabs
```java
public Optional<UserRow> findById(long id) {
    String sql = "SELECT id, email, role, active FROM users WHERE id = ?";
    try (Connection c = ds.getConnection();                // 1) взяти з пулу
         PreparedStatement st = c.prepareStatement(sql)) {  // 2) підготувати
        st.setLong(1, id);
        try (ResultSet rs = st.executeQuery()) {            // 3) курсор
            return rs.next() ? Optional.of(map(rs)) : Optional.empty();
        }
    } catch (SQLException e) {
        throw new DataAccessException("findById(" + id + ")", e);
    }
    // усі три ресурси закриються в ЗВОРОТНОМУ порядку — навіть на винятку
}
```
```py
def find_by_id(self, id: int) -> Optional[UserRow]:
    sql = "SELECT id, email, role, active FROM users WHERE id = %s"
    try:
        with self._pool.connection() as conn:      # 1) взяти з пулу
            with conn.cursor() as cur:              # 2) курсор
                cur.execute(sql, (id,))             # параметр, не формат-рядок
                row = cur.fetchone()               # 3) прочитати
                return _map(row) if row else None
    except psycopg.Error as e:
        raise DataAccessException(f"find_by_id({id})") from e
    # обидва `with` закриють ресурс на виході — і на винятку теж
```
:::

`try (A; B)` закриває `B`, потім `A` — у зворотному порядку відкриття — і робить це в неявному `finally`, тож виняток посеред `executeQuery()` не лишить курсор висіти. Два вкладені `with` у Python — це те саме: вихід із блоку (звичайний чи через виняток) кличе `__exit__`, який поверне з'єднання в пул і закриє курсор. А `raise ... from e` — прямий відповідник передавання `cause`: він чіпляє первісну помилку до нової, щоб слід не обірвався. Одне слово на мову — і ресурс не тече, і причина не губиться.

## Реалізація в пам'яті

А тепер той самий контракт над звичайною мапою. Жодної бази — записи просто лежать у `HashMap`. Це не іграшка: саме ця реалізація дасть нам тести без бази.

```java
class InMemoryUserDao implements UserDao {
    private final Map<Long, UserRow> store = new HashMap<>();

    public Optional<UserRow> findById(long id) {
        return Optional.ofNullable(store.get(id));
    }
    public List<UserRow> findByRole(String role) {
        return store.values().stream()
            .filter(u -> u.role().equals(role))
            .sorted(comparingLong(UserRow::id)).toList();   // той самий порядок, що ORDER BY id
    }
    public List<UserRow> findByIds(Collection<Long> ids) {
        return ids.stream().map(store::get).filter(Objects::nonNull)
            .sorted(comparingLong(UserRow::id)).toList();
    }
    public void insert(UserRow u) { store.put(u.id(), u); }
    public void update(UserRow u) { store.put(u.id(), u); }
    public void delete(long id)   { store.remove(id); }
}

class InMemoryOrderDao implements OrderDao {
    private final Map<Long, OrderRow> store = new HashMap<>();

    public List<OrderRow> findByStatus(String status) {
        return store.values().stream()
            .filter(o -> o.status().equals(status))
            .sorted(comparingLong(OrderRow::id)).toList();
    }
    public void insert(OrderRow o) { store.put(o.id(), o); }
}
```

Один рядок тут вирішальний — `.sorted(comparingLong(...::id))`. У базі порядок задає `ORDER BY id`; у пам'яті `HashMap` не має жодного порядку. Якби реалізація в пам'яті віддавала записи як прийдеться, тест міг би вимагати `[ann, bob]`, а прод — віддавати `[bob, ann]`: тест зелений, продакшн неправильний. Обидві реалізації мусять **сходитися в спостережуваній поведінці** — тому обидві сортують за `id`. Це перший натяк на те, як реалізація в пам'яті може тихо збрехати; про це ще буде мова.

## Фабрика: звідки береться реалізація

Ми маємо дві реалізації одного контракту. Хтось мусить вирішити, яку підставити, — і краще, щоб це вирішувалося **в одному місці за конфігом**, а не купою `new SqlUserDao(...)`, розсипаних по коду. Це робота фабрики DAO.

```java
public class DaoFactory {
    public enum Backend { SQL, MEMORY }

    private final Backend backend;
    private final DataSource ds;                          // потрібен лише для SQL
    private final InMemoryUserDao  memUsers  = new InMemoryUserDao();
    private final InMemoryOrderDao memOrders = new InMemoryOrderDao();

    private DaoFactory(Backend backend, DataSource ds) {
        this.backend = backend;
        this.ds = ds;
    }

    // джерело вирішує конфіг, а не місце виклику
    public static DaoFactory fromConfig(DataSource ds) {
        String name = System.getenv().getOrDefault("DAO_BACKEND", "SQL");
        return new DaoFactory(Backend.valueOf(name), ds);
    }

    public UserDao users() {
        return backend == Backend.SQL ? new SqlUserDao(ds) : memUsers;
    }
    public OrderDao orders() {
        return backend == Backend.SQL ? new SqlOrderDao(ds) : memOrders;
    }
}
```

Придивися до асиметрії всередині. Для SQL фабрика щоразу робить **новий** `SqlUserDao` — і це правильно: він без стану, увесь стан лежить у базі, а сам об'єкт — тонка обгортка над `DataSource`. Для пам'яті вона щоразу віддає **той самий** `memUsers` — теж правильно, але з протилежної причини: тут стан **і є** об'єкт, його `HashMap`. Верни новий `InMemoryUserDao` на кожен виклик — і те, що поклав перший виклик, другий уже не побачить, бо це порожня мапа. Плутанина цих двох випадків — тихе джерело багів: спільний DAO там, де мав бути свіжий, або навпаки.

Фабрика лише **робить** потрібну реалізацію; хто саме передасть її сервісу — це вже [впровадження залежностей](topic:sf-apps/dependency-injection): екземпляр подають конструктору ззовні, тож сам сервіс і гадки не має, звідки DAO взявся.

## Сервіс і тест без бази

Тепер — заради чого все. `DigestService` бере два DAO й відповідає на ділове питання. Ось версія, до якої ми хочемо прийти, — **пакетна**: один запит по замовленнях, один по всіх власниках гуртом.

```java
public class DigestService {
    private final UserDao users;
    private final OrderDao orders;
    public DigestService(UserDao users, OrderDao orders) {
        this.users = users;
        this.orders = orders;
    }

    public List<String> digest() {
        List<OrderRow> paid = orders.findByStatus("paid");           // 1 запит
        Set<Long> ids = paid.stream().map(OrderRow::userId).collect(toSet());
        Map<Long, UserRow> byId = users.findByIds(ids).stream()      // 1 запит на ВСІХ
            .collect(toMap(UserRow::id, u -> u));
        return paid.stream()
            .map(o -> byId.get(o.userId()).email() + " → " + money(o.cents()))
            .toList();
    }

    private static String money(long cents) {
        return String.format("%d.%02d", cents / 100, cents % 100);   // 1500 → 15.00
    }
}
```

Сервіс не знає слова «SQL». Він тримає `UserDao` й `OrderDao` — і байдуже, база під ними чи мапа. Тому тест підставляє реалізацію в пам'яті, наповнює її прямо в коді й перевіряє правило — без бази, без схеми, без прибирання за собою.

```java
class DigestServiceTest {
    @Test
    void digestPairsPaidOrdersWithOwnerEmail() {
        UserDao users = new InMemoryUserDao();
        OrderDao orders = new InMemoryOrderDao();
        users.insert(new UserRow(1, "ann@co", "approver", true));
        users.insert(new UserRow(2, "bob@co", "buyer", true));
        orders.insert(new OrderRow(10, 1, "paid",  1500));
        orders.insert(new OrderRow(11, 2, "paid",   900));
        orders.insert(new OrderRow(12, 1, "draft",  400));   // не оплачене — поза дайджестом

        List<String> digest = new DigestService(users, orders).digest();

        assertEquals(List.of("ann@co → 15.00", "bob@co → 9.00"), digest);
    }
}
```

Цей тест іде мікросекунди, бо немає ні диску, ні мережі. Він **детермінований**: тих самих трьох рядків досить, ніякого чужого стану зі спільної бази, а порядок стабільний, бо обидві реалізації сортують за `id`. І він **чесний** — перевіряє саме ділове правило (оплачені → пошта власника → сума), а не JDBC. Тисячу таких тестів можна ганяти на кожен коміт; повільний тест із живою базою лишається тонким шаром окремо, де перевіряють уже сам `SqlUserDao`.

## Де воно ламається

Патерн, який так легко зібрати, так само легко й скалічити. Три способи зіпсувати цей DAO варто впізнавати наперед — і всі три ми щойно навмисно обійшли.

**Прихований N+1.** `digest()` вище зроблено пакетним не випадково. Ось як його пишуть, коли забувають, що DAO ходить у базу:

```java
public List<String> naiveDigest() {
    List<String> lines = new ArrayList<>();
    for (OrderRow o : orders.findByStatus("paid")) {              // 1 запит
        UserRow u = users.findById(o.userId()).orElseThrow();     // +1 запит на КОЖНЕ
        lines.add(u.email() + " → " + money(o.cents()));
    }
    return lines;
}
```

Читається невинно: цикл по замовленнях, для кожного дістати власника. Але `users.findById(...)` усередині циклу — це окремий похід у базу на **кожне** замовлення. П'ятсот оплачених замовлень — п'ятсот і один запит замість двох. Мережеві затримки складаються, і дайджест, який мав будуватися десяток мілісекунд, тягне секунди. Це класична [проблема N+1](topic:sf-data/active-record): один запит по список плюс по одному на кожен його елемент.

![Два ряди-порівняння кількості походів у базу. Верхній ряд «наївно, цикл по рядках»: один блок findByStatus, далі п'ять червоних блоків findById і три крапки, праворуч червона плашка «1 + N запитів». Нижній ряд «пакетно, один IN-запит»: блок findByStatus і зелений блок findByIds(ids), праворуч зелена плашка «2 запити». Унизу підпис: та сама відповідь, ліворуч сотня походів у базу, праворуч два](img/dao-n-plus-one.svg)

*Обидва цикли дають однаковий дайджест. Різниця — у кількості походів у базу: наївний цикл викликів робить 1 + N запитів, пакетний — рівно два. DAO ховає SQL, але не його ціну.*

Ліки — зібрати всі потрібні id й дістати власників **одним** `findByIds` (той самий `IN (...)`, заради якого метод і клали в контракт). І пастка тут підступна вдвічі: у тесті з `InMemoryUserDao` наївна версія теж миттєва, бо `HashMap.get` дешевий, — тобто тест **не спіймає** N+1. Проблема живе рівно там, де її не видно з тесту; ловлять її вже на реальній базі — за кількістю запитів у логах чи профайлером.

**Дірява абстракція.** DAO має вигляд об'єкта в пам'яті, і за цим виглядом легко почати брехати про те, що всередині. Три звичні протікання. Перше — метод, що повертає назовні сирий об'єкт драйвера:

```java
ResultSet findAllUsers();   // ← так НЕ можна
```

Це вже не DAO: `ResultSet` тримає відкритий курсор і живе з'єднання, тож викликач мусить знати про JDBC і закривати ресурс — саме те, що DAO мав сховати. Абстракція, крізь яку видно драйвер, нічого не ховає.

Друге — «дістати все й відфільтрувати в коді»:

```java
users.findAll().stream().filter(u -> u.role().equals("approver"))  // ← тягне всю таблицю
```

Виглядає чисто, а насправді витягує **мільйон** рядків, щоб лишити три; фільтр належить у `WHERE`, тобто в метод `findByRole`, а не в клієнта. Третє — те саме мовчазне протікання порядку, яке ми закрили сортуванням: якщо реалізація в пам'яті віддає записи в іншому порядку, ніж база, абстракція протекла спостережуваною поведінкою, і тест бреше.

**Ресурси й з'єднання.** Пул з'єднань — скінченний. Кожен `ds.getConnection()` без `try`-з-ресурсами (чи `with` у Python) — це з'єднання, що не повернулося в пул; під навантаженням пул вичерпується, і застосунок стає **колом** на `getConnection()`, чекаючи вільного місця, якого вже не буде. Тонкість, про яку часто спотикаються: `Connection.close()` на пуловому з'єднанні не рве фізичний сокет — він **повертає** з'єднання в пул. Тому закривати треба **завжди й одразу**, а не «берегти відкритим, бо ще знадобиться»: відкрите з'єднання, яке ти тримаєш, — це з'єднання, якого бракує всім іншим.

Є й четверта межа, якої DAO свідомо не перетинає, — **транзакція**. Наш `digest()` тільки читає, тож питання не постає. Але щойно ділова операція **пише** через кілька DAO — списати з рахунку і зарахувати на інший, — звести їхні зміни в одне «усе або нічого» не може окремий DAO: кожен знає лише про своє з'єднання й свою дію. Межу тримають вище — сервіс явно або [Unit of Work](topic:sf-data/unit-of-work), що збирає всі зміни й фіксує їх разом. DAO виконує окремі дії; де починається й кінчається транзакція, вирішує той, хто ними диригує.

Спільна нитка всіх чотирьох пасток одна: DAO **ховає** механізм, але не **скасовує** його. Запити коштують, з'єднань обмаль, порядок і транзакційність — реальні, навіть коли за фасадом їх не видно. Абстракція варта свого шару рівно доти, доки лишається тонкими дверима до джерела — дістати, покласти, оновити, видалити, — а про ціну за цими дверима пам'ятаєш сам.
