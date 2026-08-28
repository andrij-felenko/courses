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
