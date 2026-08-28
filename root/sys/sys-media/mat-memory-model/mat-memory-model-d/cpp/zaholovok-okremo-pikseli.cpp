class Mat {
public:
    int flags;          // сигнатура, тип елемента, прапорець суцільності
    int dims;           // кількість вимірів (для зображення — 2)
    int rows, cols;      // висота й ширина (лише коли dims == 2)
    uchar* data;         // ← перший байт ЦЬОГО зображення
    const uchar* datastart;  // початок усього виділеного блоку
    const uchar* dataend;    // за останнім використаним байтом
    const uchar* datalimit;  // за останнім байтом блоку
    MatAllocator* allocator; // хто виділяв (0 — стандартний)
    UMatData* u;             // ← керівний блок із лічильником
    MatSize size;
    MatStep step;            // step[0] — байтів на рядок, step[1] — на піксель
};
