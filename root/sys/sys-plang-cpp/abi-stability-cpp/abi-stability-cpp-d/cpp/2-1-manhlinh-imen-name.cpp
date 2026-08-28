namespace Engine {
    class Widget {
    public:
        void render(int width, double scale);
    };
}
// Манглене ім'я в Itanium ABI: _ZN6Engine6Widget6renderEid
// Розбір: _Z (префікс C++)
//         N (вкладене ім'я)
//         6Engine 6Widget 6render (простір імен, клас, функція)
//         E (кінець списку імен)
//         i (int) d (double) (типи аргументів)
