int flags;               // магія · суцільність · підматриця · глибина · канали
int dims;                // кількість вимірів
int rows, cols;          // при dims > 2 обидва дорівнюють −1
uchar* data;             // перший байт ЦЬОГО заголовка
const uchar* datastart;  // помічники для locateROI / adjustROI
const uchar* dataend;
const uchar* datalimit;
MatAllocator* allocator; // індивідуальний алокатор або 0
UMatData* u;             // керівний блок; 0 — заголовок нічим не володіє
MatSize size;
MatStep step;
