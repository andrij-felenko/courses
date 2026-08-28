char buf[] = "abc";
char other[] = "xyz";

const char* p = buf;        // мішень незмінна, стрілку можна перевести
p = other;                  // ✓
*p = 'X';                   // ✗

char* const q = buf;        // стрілка прибита, мішень мінлива
q = other;                  // ✗
*q = 'X';                   // ✓

const char* const s = buf;  // прибито обидва
