// Еквівалент розгортання range-based for компілятором:
auto&& __range = data;
auto __begin = __range.begin();
auto __end = __range.end(); // КЕШУЄТЬСЯ ІТЕРАТОР КІНЦЯ!

for (; __begin != __end; ++__begin) {
    int item = *__begin;
    if (item == 2) {
        data.push_back(99); // push_back інвалідує __begin та __end!
    }
}
