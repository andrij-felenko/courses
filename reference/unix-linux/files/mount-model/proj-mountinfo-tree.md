# ⚙️ Дерево монтувань із `mountinfo`: у якому монтуванні опиниться цей шлях

Програма, яка читає `/proc/self/mountinfo`, збирає з нього дерево монтувань і на будь-який шлях відповідає двома речами: у якому саме монтуванні шлях опиниться і де він лежить усередині своєї файлової системи. Задача виглядає дрібною рівно доти, доки не спробувати розв'язати її очевидним способом — і не побачити, що очевидний спосіб помиляється на цілком буденних розкладках, а формат файлу має три місця, де наївний розбір мовчки псує дані.

## Чому номер пристрою на це питання не відповідає

Перша думка — викликати `stat` і взяти `st_dev`. Номер пристрою справді називає файлову систему, але не монтування, а це різні речі:

```
31 25 8:3 /        /home    rw,relatime shared:12 - ext4 /dev/sda3 rw
52 25 8:3 /ann/pub /srv/pub ro,relatime shared:12 - ext4 /dev/sda3 rw
```

`/home/ann/pub/x` і `/srv/pub/x` — це той самий файл: той самий диск, той самий inode, той самий `st_dev` = `8:3`. Записати можна лише через перший, бо друге монтування має прапорець `ro`. [Номер пристрою](book:unix-linux/inode-model) — властивість суперблока, спільна для всіх його монтувань; прапорці, обмеження й видима частина ФС — властивості монтування. Тож питання «чи можна сюди писати», «чи спрацює перейменування без копіювання», «до якої квоти це зарахується» вимагають знайти саме монтування, і знайти його доводиться по шляху.

Готової відповіді ядро донедавна не давало зовсім: усе, що є, — текст у `/proc/self/mountinfo`. Отже, розбираємо текст.

## Формат: два місця, де кількість полів невідома наперед

Поля йдуть у такому порядку: ідентифікатор монтування, ідентифікатор батька, `major:minor`, корінь монтування, точка монтування, прапорці монтування, **нуль чи кілька необов'язкових полів**, роздільник `-`, тип ФС, джерело, прапорці суперблока.

Необов'язкові поля — це мітки поширення: `shared:X`, `master:X`, `propagate_from:X`, `unbindable`. Їх може не бути жодного, а може бути три (монтування буває водночас спільним і підлеглим). Головне тут не число, а те, що документація ядра прямо просить **не спиратися на набір**: розбирачі мусять пропускати незнайомі мітки, бо список має право рости. Тому єдиний правильний спосіб — **шукати роздільник**, а не рахувати позиції.

Рахувати з кінця теж не можна, хоч документація й обіцяє після `-` рівно три поля. Тип і джерело ядро проганяє через власне екранування, а останнє поле складає драйвер файлової системи — і на пробіли в ньому та сама сітка вже не поширюється. Тому надійний розбір такий: знайти `-`, узяти два наступні поля як тип і джерело, а весь залишок рядка вважати одним полем прапорців суперблока.

## Екранування: один прохід, а не низка замін

Пробіли, табуляції, переведення рядка й самі зворотні слеші ядро записує як зворотний слеш і **рівно три вісімкові цифри**: `\040`, `\011`, `\012`, `\134` — той самий набір ядро застосовує й у полях типу та джерела. Саме тому розбити рядок за пробілами можна безпечно: справжніх пробілів усередині полів не лишилося.

Пастка не в тому, як екранування зняти, а в тому, **в якому порядку**. Каталог, що зветься `a\040b` — де зворотний слеш справжній, — ядро запише як `a\134040b`. Хто зніме екранування низкою замін і почне з `\134`, дістане проміжний рядок `a\040b`, а наступна заміна перетворить його на `a b`. Ім'я з шести символів стало іменем із трьох, і жодна перевірка про це не повідомила.

![Угорі шість квадратних комірок із символами a, зворотний слеш, 0, 4, 0, b і підпис «справжнє ім'я каталогу — шість символів»; нижче стрілка до рамки з рядком a\134040b і підписом, що ядро екранує сам зворотний слеш. Від рамки дві стрілки: ліворуч червона гілка «спершу замінити \134 на слеш, потім \040 на пробіл» і результат із трьох комірок a, пробіл, b із підписом «три символи — ім'я зіпсовано»; праворуч зелена гілка «один прохід зліва направо: побачив слеш — узяв рівно три вісімкові цифри й пішов далі з наступного символу» і результат із шести комірок a, зворотний слеш, 0, 4, 0, b із підписом «шість символів — ім'я відновлено»](img/mountinfo-unescape.svg)

*Низка замін має порядок, і один із порядків хибний. Проходу зліва направо впорядковувати нічого — тому й питання не виникає.*

Прохід зліва направо знімає це питання назавжди: побачив зворотний слеш, перевірив, що далі три вісімкові цифри, склав із них байт і пішов далі **з наступного за ними символу**. Те, що вже покладено у вихід, більше ніколи не переглядається.

## Найдовший збіг дає не ту відповідь

Далі напрошується просте правило: узяти всі точки монтування, вибрати найдовшу, що є початком нашого шляху, — і це відповідь. Правило дає правильний результат у більшості випадків і хибний — там, де монтування накладаються.

Змонтуємо флешку в `/mnt/usb`, потім покладемо в `/mnt/usb/photos` тимчасову ФС, а тоді накриємо всю `/mnt/usb` іншою тимчасовою. Три рядки в `mountinfo`:

```
44 28 8:17 / /mnt/usb        rw,nosuid,nodev - vfat  /dev/sdb1 rw,fmask=0022
70 44 0:36 / /mnt/usb/photos rw,relatime     - tmpfs tmpfs     rw
61 44 0:35 / /mnt/usb        rw,relatime     - tmpfs tmpfs     rw
```

Найдовший збіг для шляху `/mnt/usb/photos` — рядок 70. Але потрапити в монтування 70 більше не можна: воно висить у монтуванні 44, а корінь 44 накрито монтуванням 61. Ядро, розбираючи шлях, дійде до `/mnt/usb`, стрибне в 44, побачить, що на корені 44 стоїть 61, стрибне ще раз — і `photos` шукатиме вже в 61. Правильна відповідь — 61, і рядок 70 у файлі досі стоїть із точкою, яка нікуди не веде.

![Ліворуч дерево з чотирьох рамок: угорі «монтування 28 — точка /, ext4 /dev/sda2», під нею «монтування 44 — точка /mnt/usb, vfat /dev/sdb1, відносна точка mnt/usb», від неї дві стрілки вниз — ліворуч зелена рамка «монтування 61 — точка /mnt/usb, tmpfs, відносна точка сам корінь 44», праворуч червона рамка «монтування 70 — точка /mnt/usb/photos, tmpfs, відносна точка photos» з підписом «недосяжне: 61 накрило точку /mnt/usb». Праворуч п'ять рамок обходу згори вниз: старт монтування 28 позиція слеш; крок mnt дитини немає; крок usb тут дитина 44; у 44 позиція корінь а на корені 44 стоїть 61; крок photos у 61 дітей немає. Унизу дві рамки: червона «найдовший збіг по стовпчику точок дає 70, але в цю точку вже не потрапити» і зелена «обхід дерева дає 61, а всередині ФС /photos — саме туди й потрапить open()»](img/mountinfo-walk.svg)

*Стовпчик точок монтування — це не покажчик. Точка в ньому описує, куди монтування причепили, а не те, куди зараз веде цей шлях.*

Виходить, що стовпчик точок читати як таблицю відповідностей не можна взагалі. Він каже, **де монтування причепили**, а не **чи веде туди шлях**. Ці дві речі розходяться щоразу, коли монтування накладаються, — а накладаються вони постійно: контейнерне середовище будує дерево з десятків прив'язок і накриває одні одними, і `/etc/resolv.conf` чи `/proc/sys` усередині контейнера — це рівно такі накладені монтування.

> 🔧 **Навіщо це.** Інструмент, який вирішує, чи можна писати в шлях, чи входить він у резервну копію, чи в яку квоту зарахувати файл, помиляється саме на накритих монтуваннях — і помиляється тихо, віддаючи прапорці чужого монтування. Різниця між «дозволено» і «заборонено» тут визначається одним зайвим стрибком у дереві.

## Ідея: зібрати дерево й пройти його так, як ходить ядро

Пара «ідентифікатор — батько» дає дерево напряму. Але для обходу потрібна не абсолютна точка монтування, а **точка відносно батька** — той самий каталог усередині батьківського монтування, до якого це монтування причепили. Її дістають відніманням: точка батька завжди є початком точки дитини, бо ядро друкує шлях, ідучи вгору саме по батьках. Що лишиться після віднімання — і є відносна точка.

Порожній залишок теж має сенс, і саме він описує накладання: монтування 61 має точку `/mnt/usb`, його батько 44 має точку `/mnt/usb`, різниця порожня — отже, 61 стоїть **на самому корені** монтування 44.

Далі обхід повторює те, що робить [розбір шляху](book:unix-linux/path-resolution) в ядрі. Тримаємо пару «поточне монтування + позиція всередині нього». Беремо чергову складову шляху, дописуємо її до позиції — і перевіряємо, чи немає в поточного монтування дитини з такою відносною точкою. Якщо є, переходимо в неї, а позиція стає її коренем; і перевіряємо знову, бо на корені може стояти наступне монтування. Коли складові скінчилися, поточне монтування і є відповідь, а позиція — шлях усередині його файлової системи.

Лишається питання, звідки починати. Кореневого рядка у файлі може не бути взагалі: точку монтування ядро друкує **відносно кореня процесу**, і якщо шлях не виходить порахувати — рядок просто не виводиться. У [chroot](book:unix-linux/chroot) або в контейнері це означає, що верхні монтування посилаються на батьків, яких у файлі немає. Розв'язок акуратний: завести вигаданий вузол «те, чого у файлі немає» і чіпляти до нього всіх сиріт із їхніми абсолютними точками. Тоді обхід має з чого починатися завжди, а якщо він так у цьому вузлі й лишився — це чесна відповідь «монтування невідоме», а не тиха неправда.

## Код

Дві рівноцінні реалізації одного алгоритму. Обидві читають `/proc/self/mountinfo` (або файл із `MOUNTINFO=…`, щоб перевіряти на збережених знімках), без аргументів друкують дерево, а з аргументами відповідають по кожному шляху.

:::tabs

```cpp
// mountwhich.cpp — дерево монтувань із mountinfo і пошук монтування за шляхом.
// g++ -O2 -std=c++17 -o mountwhich mountwhich.cpp

#include <fcntl.h>
#include <limits.h>   // PATH_MAX
#include <stdlib.h>   // realpath — це POSIX, у std:: його немає
#include <unistd.h>

#include <algorithm>
#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <unordered_map>
#include <vector>

struct Mount {
    int id = 0, parent = 0;
    std::string dev, root, point, opts, fstype, source, sbopts;
    std::vector<std::string> tags;   // shared:12, master:7, unbindable…
    std::vector<std::string> comps;  // точка, розібрана на складники
    std::vector<std::string> rel;    // точка ВІДНОСНО батька
    std::vector<Mount *> kids;
};

/* Ядро екранує ' ', '\t', '\n', '\\' — і в шляхах, і в типі та джерелі — як
   зворотний слеш плюс рівно три вісімкові цифри. Знімаємо ОДНИМ проходом:
   послідовність замін, що починається з \134, псує справжні слеші в іменах. */
static std::string unescape(const std::string &s) {
    std::string out;
    out.reserve(s.size());
    for (size_t i = 0; i < s.size();) {
        if (s[i] == '\\' && i + 3 < s.size() &&
            s[i + 1] >= '0' && s[i + 1] <= '7' &&
            s[i + 2] >= '0' && s[i + 2] <= '7' &&
            s[i + 3] >= '0' && s[i + 3] <= '7') {
            int v = (s[i + 1] - '0') * 64 + (s[i + 2] - '0') * 8 + (s[i + 3] - '0');
            if (v <= 0xff) {
                out.push_back(static_cast<char>(v));
                i += 4;
                continue;
            }
        }
        out.push_back(s[i++]);
    }
    return out;
}

static std::vector<std::string> split_path(const std::string &p) {
    std::vector<std::string> v;
    size_t i = 0;
    while (i < p.size()) {
        while (i < p.size() && p[i] == '/') ++i;
        size_t b = i;
        while (i < p.size() && p[i] != '/') ++i;
        if (i > b && p.compare(b, i - b, ".") != 0) v.emplace_back(p, b, i - b);
    }
    return v;
}

static bool parse_line(const std::string &line, Mount &m) {
    std::vector<std::string> f;
    for (size_t i = 0; i < line.size();) {
        while (i < line.size() && line[i] == ' ') ++i;
        size_t b = i;
        while (i < line.size() && line[i] != ' ') ++i;
        if (i > b) f.emplace_back(line, b, i - b);
    }
    /* Роздільник ШУКАЄМО: необов'язкових полів нуль або кілька, і їхній
       набір ядру дозволено розширювати. З кінця рахувати теж не можна —
       останнє поле складає драйвер ФС, і пробіли в ньому не екрановані. */
    size_t sep = 6;
    while (sep < f.size() && f[sep] != "-") ++sep;
    if (sep >= f.size() || f.size() < sep + 4) return false;

    m.id = std::atoi(f[0].c_str());
    m.parent = std::atoi(f[1].c_str());
    m.dev = f[2];
    m.root = unescape(f[3]);
    m.point = unescape(f[4]);
    m.opts = f[5];
    m.tags.assign(f.begin() + 6, f.begin() + sep);
    m.fstype = unescape(f[sep + 1]);
    m.source = unescape(f[sep + 2]);
    m.sbopts = f[sep + 3];
    for (size_t k = sep + 4; k < f.size(); ++k) m.sbopts += " " + f[k];
    m.comps = split_path(m.point);
    return true;
}

struct Tree {
    std::vector<Mount> all;
    std::unordered_map<int, Mount *> by_id;
    Mount outside;  // вигаданий вузол: те, чого у файлі немає
};

static void build(Tree &t) {
    t.outside.id = -1;
    t.outside.point = "?";
    t.outside.root = "/";
    t.outside.fstype = t.outside.source = "?";

    for (auto &m : t.all) t.by_id[m.id] = &m;

    for (auto &m : t.all) {
        auto it = t.by_id.find(m.parent);
        Mount *p = (it == t.by_id.end()) ? nullptr : it->second;
        if (p == &m) p = nullptr;  // вершина дерева: батько — сам собі
        if (p && (m.comps.size() < p->comps.size() ||
                  !std::equal(p->comps.begin(), p->comps.end(), m.comps.begin()))) {
            std::fprintf(stderr, "монтування %d: точка «%s» не лежить під «%s»\n",
                         m.id, m.point.c_str(), p->point.c_str());
            p = nullptr;
        }
        if (!p) {  // сирота: у chroot батьківський рядок просто не виводиться
            m.rel = m.comps;
            t.outside.kids.push_back(&m);
            continue;
        }
        m.rel.assign(m.comps.begin() + p->comps.size(), m.comps.end());
        p->kids.push_back(&m);
    }
}

/* Спуск крізь стос монтувань у цій самій позиції: поки в поточному
   монтуванні на позиції pos є дитина — переходимо в неї, а позиція
   стає її коренем. Саме цей цикл і робить ядро на кожній складовій. */
static void descend(Mount *&cur, std::vector<std::string> &pos) {
    for (;;) {
        Mount *next = nullptr;
        for (Mount *k : cur->kids)
            if (k->rel == pos) next = k;  // збігів кілька — бере останній рядок
        if (!next) return;
        cur = next;
        pos.clear();
    }
}

static Mount *resolve(Tree &t, const std::string &path, std::vector<std::string> &pos) {
    Mount *cur = &t.outside;
    pos.clear();
    descend(cur, pos);
    for (const std::string &c : split_path(path)) {
        pos.push_back(c);
        descend(cur, pos);
    }
    return cur;
}

static std::string inside(const Mount *m, const std::vector<std::string> &pos) {
    std::string s = (m->root == "/") ? "" : m->root;
    if (s.size() > 1 && s.back() == '/') s.pop_back();
    for (const auto &c : pos) { s += '/'; s += c; }
    return s.empty() ? "/" : s;
}

static void dump(Tree &t, Mount *m, int depth) {
    std::vector<std::string> pos;
    Mount *r = resolve(t, m->point, pos);
    std::string note = (r == m) ? "" : "   <- точка веде в " + std::to_string(r->id);
    std::string extra = (m->root == "/") ? "" : ", корінь " + m->root;
    std::printf("%*s[%d] %s  (%s, %s%s)%s\n", depth * 2, "", m->id, m->point.c_str(),
                m->fstype.c_str(), m->source.c_str(), extra.c_str(), note.c_str());
    for (Mount *k : m->kids) dump(t, k, depth + 1);
}

static std::string slurp(const char *path) {
    int fd = ::open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) { std::perror(path); std::exit(1); }
    std::vector<char> buf(1u << 16);
    std::string data;
    for (;;) {
        ssize_t n = ::read(fd, buf.data(), buf.size());
        if (n < 0) {
            if (errno == EINTR) continue;
            std::perror("read");
            std::exit(1);
        }
        if (n == 0) break;
        data.append(buf.data(), static_cast<size_t>(n));
    }
    ::close(fd);
    return data;
}

int main(int argc, char **argv) {
    const char *src = std::getenv("MOUNTINFO");
    if (!src) src = "/proc/self/mountinfo";

    Tree t;
    std::string data = slurp(src);
    for (size_t b = 0; b < data.size();) {
        size_t e = data.find('\n', b);
        if (e == std::string::npos) e = data.size();
        if (e > b) {
            std::string line(data, b, e - b);
            Mount m;
            if (parse_line(line, m)) t.all.push_back(std::move(m));
            else std::fprintf(stderr, "не розібрано: %s\n", line.c_str());
        }
        b = e + 1;
    }
    build(t);  // покажчики беремо ЛИШЕ тут: t.all уже не росте

    if (argc < 2) {
        for (Mount *m : t.outside.kids) dump(t, m, 0);
        return 0;
    }
    for (int i = 1; i < argc; ++i) {
        /* Символьні посилання й ".." розкриваємо ЗАЗДАЛЕГІДЬ: /var/run
           і /run — різні шляхи, а монтування за ними те саме. */
        char real[PATH_MAX];
        const char *q = realpath(argv[i], real) ? real : argv[i];
        std::vector<std::string> pos;
        Mount *m = resolve(t, q, pos);
        if (m->id < 0) {
            std::printf("%s -> монтування у файлі відсутнє\n", q);
            continue;
        }
        std::printf("%s -> [%d] %s, %s %s, усередині ФС: %s\n", q, m->id,
                    m->point.c_str(), m->fstype.c_str(), m->source.c_str(),
                    inside(m, pos).c_str());
    }
    return 0;
}
```

```go
// mountwhich.go — той самий алгоритм. Потрібен Go 1.21+ (пакет slices).
// go build -o mountwhich mountwhich.go
package main

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"slices"
	"strconv"
	"strings"
)

type Mount struct {
	ID, Parent  int
	Dev         string
	Root, Point string
	Opts        string
	Tags        []string // shared:12, master:7, unbindable…
	FsType      string
	Source      string
	SbOpts      string
	comps, rel  []string
	kids        []*Mount
}

func isOctal(c byte) bool { return c >= '0' && c <= '7' }

// Один прохід зліва направо. Послідовність замін тут була б помилкою:
// той порядок, що знімає \134 першим, псує імена зі справжнім слешем.
func unescape(s string) string {
	if !strings.Contains(s, `\`) {
		return s
	}
	var b strings.Builder
	b.Grow(len(s))
	for i := 0; i < len(s); {
		if s[i] == '\\' && i+3 < len(s) &&
			isOctal(s[i+1]) && isOctal(s[i+2]) && isOctal(s[i+3]) {
			v := int(s[i+1]-'0')<<6 | int(s[i+2]-'0')<<3 | int(s[i+3]-'0')
			if v <= 0xff {
				b.WriteByte(byte(v))
				i += 4
				continue
			}
		}
		b.WriteByte(s[i])
		i++
	}
	return b.String()
}

func splitPath(p string) []string {
	out := make([]string, 0, 8)
	for _, c := range strings.Split(p, "/") {
		if c != "" && c != "." {
			out = append(out, c)
		}
	}
	return out
}

// strings.Fields безпечний саме тому, що справжні пробільні всередині
// полів ядро вже екранувало — інакше різати рядок за пробілами не можна.
func parseLine(line string) (*Mount, error) {
	f := strings.Fields(line)
	sep := 6
	for sep < len(f) && f[sep] != "-" {
		sep++
	}
	if sep >= len(f) || len(f) < sep+4 {
		return nil, fmt.Errorf("немає роздільника «-» або замало полів")
	}
	id, err := strconv.Atoi(f[0])
	if err != nil {
		return nil, err
	}
	parent, err := strconv.Atoi(f[1])
	if err != nil {
		return nil, err
	}
	m := &Mount{
		ID: id, Parent: parent, Dev: f[2],
		Root:   unescape(f[3]),
		Point:  unescape(f[4]),
		Opts:   f[5],
		Tags:   slices.Clone(f[6:sep]),
		FsType: unescape(f[sep+1]),
		Source: unescape(f[sep+2]),
		SbOpts: strings.Join(f[sep+3:], " "),
	}
	m.comps = splitPath(m.Point)
	return m, nil
}

type Tree struct {
	byID    map[int]*Mount
	outside *Mount // вигаданий вузол: те, чого у файлі немає
}

func isPrefix(p, c []string) bool {
	return len(c) >= len(p) && slices.Equal(p, c[:len(p)])
}

func build(ms []*Mount) *Tree {
	t := &Tree{
		byID:    make(map[int]*Mount, len(ms)),
		outside: &Mount{ID: -1, Point: "?", Root: "/", FsType: "?", Source: "?"},
	}
	for _, m := range ms {
		t.byID[m.ID] = m
	}
	for _, m := range ms {
		p := t.byID[m.Parent]
		if p == m {
			p = nil // вершина дерева: батько — сам собі
		}
		if p != nil && !isPrefix(p.comps, m.comps) {
			fmt.Fprintf(os.Stderr, "монтування %d: точка %q не лежить під %q\n",
				m.ID, m.Point, p.Point)
			p = nil
		}
		if p == nil { // сирота: у chroot батьківський рядок не виводиться
			m.rel = m.comps
			t.outside.kids = append(t.outside.kids, m)
			continue
		}
		m.rel = m.comps[len(p.comps):]
		p.kids = append(p.kids, m)
	}
	return t
}

// Спуск крізь стос монтувань у цій самій позиції.
func descend(cur *Mount, pos []string) (*Mount, []string) {
	for {
		var next *Mount
		for _, k := range cur.kids {
			if slices.Equal(k.rel, pos) {
				next = k // збігів кілька — перемагає останній рядок
			}
		}
		if next == nil {
			return cur, pos
		}
		cur, pos = next, nil
	}
}

func (t *Tree) Resolve(path string) (*Mount, []string) {
	cur, pos := descend(t.outside, nil)
	for _, c := range splitPath(path) {
		pos = append(pos, c)
		cur, pos = descend(cur, pos)
	}
	return cur, pos
}

func inside(m *Mount, pos []string) string {
	base := strings.TrimSuffix(m.Root, "/")
	if len(pos) == 0 {
		if base == "" {
			return "/"
		}
		return base
	}
	return base + "/" + strings.Join(pos, "/")
}

func (t *Tree) dump(m *Mount, depth int) {
	note := ""
	if r, _ := t.Resolve(m.Point); r != m {
		note = fmt.Sprintf("   <- точка веде в %d", r.ID)
	}
	extra := ""
	if m.Root != "/" {
		extra = ", корінь " + m.Root
	}
	fmt.Printf("%*s[%d] %s  (%s, %s%s)%s\n", depth*2, "", m.ID, m.Point,
		m.FsType, m.Source, extra, note)
	for _, k := range m.kids {
		t.dump(k, depth+1)
	}
}

func slurp(path string) []byte {
	f, err := os.Open(path)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	defer f.Close()
	var data []byte
	buf := make([]byte, 1<<16)
	for {
		n, err := f.Read(buf)
		data = append(data, buf[:n]...)
		if err == io.EOF {
			break
		}
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		if n == 0 {
			break
		}
	}
	return data
}

func main() {
	src := os.Getenv("MOUNTINFO")
	if src == "" {
		src = "/proc/self/mountinfo"
	}
	var ms []*Mount
	for _, line := range strings.Split(string(slurp(src)), "\n") {
		if strings.TrimSpace(line) == "" {
			continue
		}
		m, err := parseLine(line)
		if err != nil {
			fmt.Fprintf(os.Stderr, "не розібрано (%v): %s\n", err, line)
			continue
		}
		ms = append(ms, m)
	}
	t := build(ms)

	if len(os.Args) < 2 {
		for _, m := range t.outside.kids {
			t.dump(m, 0)
		}
		return
	}
	for _, arg := range os.Args[1:] {
		// Символьні посилання й ".." розкриваємо заздалегідь.
		q, err := filepath.Abs(arg)
		if err != nil {
			q = arg
		}
		if r, err := filepath.EvalSymlinks(q); err == nil {
			q = r
		}
		m, pos := t.Resolve(q)
		if m.ID < 0 {
			fmt.Printf("%s -> монтування у файлі відсутнє\n", q)
			continue
		}
		fmt.Printf("%s -> [%d] %s, %s %s, усередині ФС: %s\n",
			q, m.ID, m.Point, m.FsType, m.Source, inside(m, pos))
	}
}
```

:::

## Що воно виводить

Знімок, який зібрано навмисно з усіх пасток одразу: прив'язка з непорожнім коренем монтування, накрите монтування, недосяжний рядок і точка з екранованим пробілом.

```
28 1 8:2 / / rw,relatime shared:1 - ext4 /dev/sda2 rw
23 28 0:22 / /proc rw,nosuid,nodev,noexec,relatime shared:14 - proc proc rw
31 28 8:3 / /home rw,relatime shared:12 - ext4 /dev/sda3 rw
52 28 8:3 /ann/pub /srv/pub ro,relatime shared:12 - ext4 /dev/sda3 rw
44 28 8:17 / /mnt/usb rw,nosuid,nodev - vfat /dev/sdb1 rw,fmask=0022
70 44 0:36 / /mnt/usb/photos rw,relatime - tmpfs tmpfs rw
61 44 0:35 / /mnt/usb rw,relatime - tmpfs tmpfs rw
83 28 0:37 / /media/My\040Files rw,relatime - vfat /dev/sdc1 rw
```

```
[28] /  (ext4, /dev/sda2)
  [23] /proc  (proc, proc)
  [31] /home  (ext4, /dev/sda3)
  [52] /srv/pub  (ext4, /dev/sda3, корінь /ann/pub)
  [44] /mnt/usb  (vfat, /dev/sdb1)   <- точка веде в 61
    [70] /mnt/usb/photos  (tmpfs, tmpfs)   <- точка веде в 61
    [61] /mnt/usb  (tmpfs, tmpfs)
  [83] /media/My Files  (vfat, /dev/sdc1)

/home/ann/docs         -> [31] /home, ext4 /dev/sda3, усередині ФС: /ann/docs
/srv/pub/x             -> [52] /srv/pub, ext4 /dev/sda3, усередині ФС: /ann/pub/x
/mnt/usb/photos        -> [61] /mnt/usb, tmpfs tmpfs, усередині ФС: /photos
/media/My Files/a.txt  -> [83] /media/My Files, vfat /dev/sdc1, усередині ФС: /a.txt
/etc/passwd            -> [28] /, ext4 /dev/sda2, усередині ФС: /etc/passwd
```

Рядок `/srv/pub/x` показує, навіщо взагалі повертати шлях усередині ФС: файл, який користувач бачить як `/srv/pub/x`, на диску `sda3` лежить за іменем `/ann/pub/x`. Без цього перетворення ані порівняти два шляхи, ані звернутися до тієї ж ФС іншим монтуванням неможливо. А позначка «точка веде в 61» на рядках 44 і 70 — це та сама перевірка, що й для будь-якого шляху, просто застосована до власної точки монтування.

## Як переконатися, що відповідь правильна

Найнадійніший суддя — саме ядро. `statx(2)` уміє віддавати ідентифікатор монтування, у якому лежить файл, і робить це власним розбором шляху, а не нашим:

```c
/* cc -O2 -o mntid mntid.c ; потрібне ядро 5.8+ */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>

int main(int argc, char **argv) {
    struct statx sx;
    if (argc < 2) { fputs("вжиток: mntid <шлях>\n", stderr); return 2; }
    if (statx(AT_FDCWD, argv[1], 0, STATX_MNT_ID, &sx) < 0) { perror("statx"); return 1; }
    if (!(sx.stx_mask & STATX_MNT_ID)) { fputs("ядро не віддало mnt_id\n", stderr); return 1; }
    printf("%s -> монтування %llu\n", argv[1], (unsigned long long)sx.stx_mnt_id);
    return 0;
}
```

Число, яке віддасть `statx`, мусить збігтися з тим, що надрукував наш обхід, — на будь-якому шляху й за будь-якої розкладки накладених монтувань. Це і є перевірка на живій машині: змонтуйте `tmpfs` двічі в ту саму теку, спитайте обидві програми і звірте. Наївний найдовший збіг на цьому тесті розійдеться з ядром одразу.

Той самий `statx` пояснює й межу самої задачі. Поле `STATX_MNT_ID` (Linux 5.8) віддає **той самий** ідентифікатор, що стоїть першим стовпчиком у `mountinfo`, і його ядро **перевикористовує** після зняття монтування. Тому запам'ятовувати ці числа надовго не можна: те саме число через хвилину може називати геть інше монтування. Для випадків, де потрібна стала назва, з Linux 6.8 є `STATX_MNT_ID_UNIQUE` — 64-бітний ідентифікатор, який ядро обіцяє не повторювати, доки система працює. У `mountinfo` його немає взагалі; за ним ідуть до `statmount(2)`, що з'явився в тому самому 6.8 разом із `listmount(2)` саме тому, що розбирати весь `mountinfo` заради відомостей про одне монтування — дорого й незручно.

## Скільки це коштує

```
розбір     O(B)        B — байтів у файлі; один прохід, без регулярних виразів
збірка     O(n)        n — рядків; таблиця «ідентифікатор → монтування»
запит      O(k · c)    k — складників шляху, c — дітей у вузлі дорогою
пам'ять    O(B)
```

Множник `c` виглядає загрозливо лише на папері: діти розкидані по всьому дереву, і на одному шляху їх трапляється кілька, а не сотні. Якщо ж запитів багато, дітей індексують таблицею за ключем «ідентифікатор батька + відносна точка», і запит стає `O(k)`. Куди дорожча позначка «точка веде в інше монтування» в друку дерева: вона робить по одному повному пошуку на кожен рядок, тобто `O(n · k · c)` — для звіту прийнятно, для гарячого циклу ні.

## Чого цей код не може

Головна межа не в алгоритмі, а в тому, як `/proc` віддає текст. Ядро тримає замок на дереві монтувань **у межах одного `read(2)`**, і за один виклик віддає стільки записів, скільки влізло у свій внутрішній буфер — а він починається з однієї сторінки (на x86-64 це 4096 байтів) і в цьому місці не росте. Скільки б ви не просили, більшого шматка не буде.

**Умова.** Хост із контейнерами: 400 монтувань, середній рядок ≈ 150 байтів.

```
обсяг файлу       = 400 · 150 Б     ≈ 60 000 Б
за один read(2)   ≤ 4096 Б          ≈ 27 рядків
викликів read(2)  = 60 000 / 4096   ≈ 15
```

П'ятнадцять разів замок беруть і відпускають. Якщо між ними хтось монтує чи знімає — прочитане може виявитися знімком, якого не існувало жодної миті: частина рядків із «до», частина з «після», а якийсь рядок пропущений або задубльований, бо ядро відлічує записи за порядковим номером. На спокійній машині це не проявиться ніколи, на хості контейнерів — проявиться.

Ловити зміни допомагає братній файл: `/proc/[pid]/mounts` з ядра 2.6.15 можна тримати відкритим і чекати на ньому `poll(2)` — монтування чи зняття будить очікувача (з ядра 2.6.30 — подією `POLLPRI`). Прочитали `mountinfo`, побачили подію — прочитали ще раз. Це не робить читання цілісним, але дає знати, що результат уже застарів.

Решта меж дрібніші, але про них теж треба пам'ятати. Шлях мусить приходити вже розкритим: символьне посилання наш обхід не розкриває й розкрити не може, бо про вміст файлової системи він не знає нічого — тому [посилання](book:unix-linux/hard-and-symbolic-links) знімає `realpath`, і з тієї ж причини `..` мусить зникнути до виклику. І ще: усе прочитане описує дерево того процесу, який читав. Інший [простір імен монтувань](book:unix-linux/namespaces) — інший файл, інші відповіді, і зчитати чужий можна лише через `/proc/<pid>/mountinfo`, маючи на це право.
