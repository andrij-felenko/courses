#include <memory>
#include <string>
#include <vector>

struct Node;
using NodeP = std::shared_ptr<const Node>;   // const у самому типі: вузол не міняють ніколи

// Скільки байтів вузлів народилося. Модель живе на одному потоці — на потоці
// інтерфейсу, — тож звичайний лічильник, без атомарності.
inline thread_local std::size_t g_born = 0;

struct Node {
    const std::string        id;      // стабільний; переживає всі версії документа
    const std::string        text;
    const std::vector<NodeP> kids;
    const std::size_t        own;     // вага САМОГО вузла
    const std::size_t        bytes;   // вага піддерева: own + сума bytes дітей

    Node(std::string i, std::string t, std::vector<NodeP> k)
        : id(std::move(i)), text(std::move(t)), kids(std::move(k)),
          own(sizeof(Node) + 24 /* керувальний блок shared_ptr */
              + id.capacity() + text.capacity() + kids.size() * sizeof(NodeP)),
          bytes(own + sumKids(kids))
    {
        g_born += own;
    }

    static std::size_t sumKids(const std::vector<NodeP>& v) {
        std::size_t s = 0;
        for (const auto& k : v) s += k->bytes;   // діти вже знають свою вагу — це O(1) на дитину
        return s;
    }
};

inline NodeP mk(std::string id, std::string text, std::vector<NodeP> kids = {}) {
    return std::make_shared<const Node>(std::move(id), std::move(text), std::move(kids));
}

// Замінити вузол із заданим id. Нові вузли — ЛИШЕ на дорозі від кореня до цілі;
// бічні піддерева нова версія бере тим самим вказівником, вони спільні.
NodeP replaceById(const NodeP& n, const std::string& id, const NodeP& repl) {
    if (n->id == id) return repl;
    for (std::size_t i = 0; i < n->kids.size(); ++i) {
        NodeP nk = replaceById(n->kids[i], id, repl);
        if (nk != n->kids[i]) {                    // ціль знайшлася в цій гілці
            std::vector<NodeP> kids = n->kids;     // копія масиву ВКАЗІВНИКІВ, не піддерев
            kids[i] = std::move(nk);
            return mk(n->id, n->text, std::move(kids));
        }
    }
    return n;                                      // тут цілі немає — вузол лишається спільним
}

// Вилучити вузол; заразом кажемо, скільки байтів пішло з дерева.
NodeP removeById(const NodeP& n, const std::string& id, std::size_t& removed) {
    for (std::size_t i = 0; i < n->kids.size(); ++i) {
        if (n->kids[i]->id == id) {
            removed += n->kids[i]->bytes;          // ← O(1): вага піддерева вже порахована
            std::vector<NodeP> kids = n->kids;
            kids.erase(kids.begin() + i);
            return mk(n->id, n->text, std::move(kids));
        }
        NodeP nk = removeById(n->kids[i], id, removed);
        if (nk != n->kids[i]) {
            std::vector<NodeP> kids = n->kids;
            kids[i] = std::move(nk);
            return mk(n->id, n->text, std::move(kids));
        }
    }
    return n;
}
