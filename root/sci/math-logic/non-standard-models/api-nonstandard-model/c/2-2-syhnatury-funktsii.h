/* Конструктори та ініціалізація */
NonStandardInt ns_create_standard(int64_t val);
NonStandardInt ns_create_inf(size_t degree, int64_t coeff);

/* Предикати та порівняння */
bool ns_is_standard(const NonStandardInt* num);
int ns_compare(const NonStandardInt* a, const NonStandardInt* b);

/* Арифметичні операції */
NonStandardInt ns_add(const NonStandardInt* a, const NonStandardInt* b);
NonStandardInt ns_multiply(const NonStandardInt* a, const NonStandardInt* b);

/* Друк */
void ns_print(const NonStandardInt* num);
