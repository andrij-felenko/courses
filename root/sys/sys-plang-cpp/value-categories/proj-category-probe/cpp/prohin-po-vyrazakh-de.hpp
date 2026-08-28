std::string        make();
const std::string  make_const();     // так писати не варто — але подивімося
std::string&       shared();
std::string&&      expiring();

struct Buf { int cells[4]; };
Buf make_buf();

struct Node {
    std::string  name;
    std::string& alias;              // посилальний член
    unsigned     flag : 1;           // бітове поле
    static std::string kind;         // статичний член
};

extern Node n;
extern std::string s, s2;
extern const std::string cs;
extern std::string&& r;              // іменоване посилання на rvalue
extern int arr[4], i;
extern bool cond;
