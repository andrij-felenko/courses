// У C++17: Використання node handle
std::map<int, std::string> src = {{1, "one"}, {2, "two"}};
std::map<int, std::string> dst;

auto node = src.extract(1); // Вузол вилучено! Ітератори src інвалідовано.
// АЛЕ: Покажчики &node.mapped() та посилання на дані всередині вузла 
// залишаються повністю ДІЙСНИМИ!

node.key() = 10; // C++17 дозволяє змінювати ключ вилученого вузла!
dst.insert(std::move(node)); // Вузол вбудовано у нове дерево без alloc/free!
