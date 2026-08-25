# 📋 Контракт `_InputArray` і `_OutputArray`: види, прапорці, методи, винятки

Це повний перелік того, що обидва проксі OpenCV насправді дозволяють: з якого типу C++ народжується кожен вид `KindFlag`, які прапорці ставить на нього конструктор, який метод для якого виду працює — і які поєднання «вид × метод» кидають виняток замість відповіді. Потрібен цей перелік тому, що компілятор жодного з цих правил не перевіряє: усі вони живуть у одному цілому числі й спрацьовують уже під час роботи програми.

Усі імена, значення й сигнатури звірено з гілкою `4.x`: оголошення — `modules/core/include/opencv2/core/mat.hpp`, конструктори — `modules/core/include/opencv2/core/mat.inl.hpp`, поведінка — `modules/core/src/matrix_wrap.cpp`.

## 1 · Три класи, три поля

```cpp
class CV_EXPORTS _InputArray            { /* … */ };
class CV_EXPORTS _OutputArray      : public _InputArray  { /* … */ };
class CV_EXPORTS _InputOutputArray : public _OutputArray { /* … */ };
```

Спадкування тут не оздоба, а частина контракту: `_OutputArray` має **всі** методи читання свого предка. Усередині функції, оголошеної як `void f(OutputArray dst)`, цілком законні виклики `dst.kind()`, `dst.isUMat()`, `dst.size()`, `dst.getMat()` — саме на цьому тримається звичайна для бібліотеки перевірка «а куди мене просять писати».

Полів на всі три класи — три, і всі оголошені в базовому:

```cpp
protected:
    int  flags;   // тег: вид джерела, тип елемента, права доступу, заборони
    void* obj;    // адреса справжнього об'єкта, без будь-якого володіння
    Size sz;      // розмір — лише для видів, де він відомий на етапі компіляції
```

`_OutputArray` не додає жодного поля, тільки методи запису. `_InputOutputArray` не додає навіть методів — лише конструктори, які ставлять `ACCESS_RW` замість `ACCESS_READ` чи `ACCESS_WRITE`. Віртуальних функцій у ієрархії немає, тож усі три об'єкти однакові за розміром: `int` із доповненням, покажчик і `Size` — двадцять чотири байти на типовій 64-бітній платформі.

Публічні імена, які ви бачите в сигнатурах бібліотеки, — псевдоніми посилань:

```cpp
typedef const _InputArray&        InputArray;
typedef InputArray                InputArrayOfArrays;
typedef const _OutputArray&       OutputArray;
typedef OutputArray               OutputArrayOfArrays;
typedef const _InputOutputArray&  InputOutputArray;
typedef InputOutputArray          InputOutputArrayOfArrays;
```

`InputArrayOfArrays` — **не окремий тип**, а буквально той самий `const _InputArray&`. Різниця суто документаційна: вона підказує читачеві, що функція очікує набір зображень, і нічого не забороняє. Тому передати в такий параметр один `Mat` компілятор дозволить, і функція його прийме — але розбере не як одне зображення, а як стос рядків (див. §7).

Поле `sz` заповнюють лише ті конструктори, яким розмір відомий із типу:

| Конструктор | `sz` |
|---|---|
| `Matx<T, m, n>` | `Size(n, m)` |
| `const T* vec, int n` | `Size(n, 1)` |
| `const double& val` | `Size(1, 1)` |
| `std::array<T, N>` | `Size(1, N)` |
| `std::array<Mat, N>` | `Size(1, N)` |
| решта (`Mat`, `UMat`, вектори, GPU-типи) | `Size()`, тобто `0×0` |

Для «решти» метод `size()` не дивиться в `sz`, а йде за покажчиком `obj` і питає справжній об'єкт. Тобто нульовий `sz` не означає порожнього масиву — він означає «розмір не кешовано».

## 2 · Розкладка поля `flags`

Одне ціле число несе чотири незалежні відповіді, розкладені по різних розрядах.

| Група | Біти | Маска | Що каже |
|---|---|---|---|
| код типу елемента | 0…11 | `0x00000FFF` | глибина (біти 0…2) і кількість каналів мінус один (біти 3…11) — звичайний для бібліотеки код на кшталт `CV_8UC3` |
| вид джерела | 16…20 | `KIND_MASK = 31 << 16` = `0x001F0000` | одне зі значень `KindFlag` |
| права доступу | 24…25 | `ACCESS_MASK = ACCESS_RW = 3 << 24` | `ACCESS_READ`, `ACCESS_WRITE` або обидва |
| швидкий доступ | 26 | `ACCESS_FAST = 1 << 26` | поза `ACCESS_MASK`; жоден конструктор проксі його не ставить |
| заборона розміру | 30 | `FIXED_SIZE = 0x4000 << 16` = `0x40000000` | `create` не має права змінити розмір |
| заборона типу | 31 | `FIXED_TYPE = 0x8000 << 16` = `0x80000000` | `create` не має права змінити тип |

```cpp
enum KindFlag {
    KIND_SHIFT = 16,
    FIXED_TYPE = 0x8000 << KIND_SHIFT,
    FIXED_SIZE = 0x4000 << KIND_SHIFT,
    KIND_MASK  = 31 << KIND_SHIFT,
    /* … значення видів … */
};

enum AccessFlag { ACCESS_READ=1<<24, ACCESS_WRITE=1<<25,
    ACCESS_RW=3<<24, ACCESS_MASK=ACCESS_RW, ACCESS_FAST=1<<26 };
```

Три наслідки, на які варто зважати.

**Константи видів уже зсунуті.** `_InputArray::MAT` дорівнює не одиниці, а `0x00010000`. Порівнювати `kind()` треба саме з цими константами, а не з номерами.

**`FIXED_TYPE` — знаковий біт.** Поле `flags` оголошене як `int`, тож будь-який проксі із забороною типу має **від'ємне** значення `flags`. У налагоджувачі це виглядає лякливо (щось на зразок `-2147090429`), хоча означає лише «тип чіпати не можна».

**Біти 12…15, 21…23 і 27…29 не зайняті.** Це не місце для власних прапорців: `init()` приймає готове число, і будь-яке зайве значення там просто поїде в `flags` без перевірки.

Кодування типу елемента — те саме, що в самому `Mat`; глибину, кількість каналів і крок рядка розібрано в темі про [формати пікселів](topic:sf-visual/pixel-formats).

## 3 · Види `KindFlag`: з чого будується кожен

| `KindFlag` | № | Значення | З якого типу C++ народжується |
|---|---|---|---|
| `NONE` | 0 | `0x00000000` | `_OutputArray()`, `_InputOutputArray()`, `noArray()` |
| `MAT` | 1 | `0x00010000` | `Mat`, `Mat_<T>` |
| `MATX` | 2 | `0x00020000` | `Matx<T,m,n>`, а через нього `Vec`, `Point_`, `Scalar`; ще `double`, пара «`const T* vec, int n`», `std::array<T,N>` |
| `STD_VECTOR` | 3 | `0x00030000` | `std::vector<T>` для арифметичних `T`, `Point`, `Vec`, `Rect`… |
| `STD_VECTOR_VECTOR` | 4 | `0x00040000` | `std::vector<std::vector<T>>` |
| `STD_VECTOR_MAT` | 5 | `0x00050000` | `std::vector<Mat>`, `std::vector<Mat_<T>>` |
| *(6)* | 6 | — | діра: знятий `EXPR` (`MatExpr`) |
| `OPENGL_BUFFER` | 7 | `0x00070000` | `ogl::Buffer` |
| `CUDA_HOST_MEM` | 8 | `0x00080000` | `cuda::HostMem` |
| `CUDA_GPU_MAT` | 9 | `0x00090000` | `cuda::GpuMat`, `cudev::GpuMat_<T>` |
| `UMAT` | 10 | `0x000A0000` | `UMat` |
| `STD_VECTOR_UMAT` | 11 | `0x000B0000` | `std::vector<UMat>` |
| `STD_BOOL_VECTOR` | 12 | `0x000C0000` | `std::vector<bool>` — **лише як вхід** |
| `STD_VECTOR_CUDA_GPU_MAT` | 13 | `0x000D0000` | `std::vector<cuda::GpuMat>` |
| *(14)* | 14 | — | діра: знятий `STD_ARRAY` |
| `STD_ARRAY_MAT` | 15 | `0x000F0000` | `std::array<Mat, N>` |
| `CUDA_GPU_MATND` | 16 | `0x00100000` | `cuda::GpuMatND` |

Дві діри — не помилка нумерації. Значення 6 (`EXPR`, проксі над відкладеним матричним виразом) і 14 (`STD_ARRAY`, окремий вид для `std::array<T,N>`) прибрано, але номери лишилися зайнятими до версії 5.0 — щоб уже зібрані бінарники не почали читати старий тег як новий вид. У самому `kind()` від них лишилися сторожі для налагоджувальної збірки:

```cpp
_InputArray::KindFlag _InputArray::kind() const
{
    KindFlag k = flags & KIND_MASK;
#if CV_VERSION_MAJOR < 5
    CV_DbgAssert(k != EXPR);
    CV_DbgAssert(k != STD_ARRAY);
#endif
    return k;
}
```

Окремо варто помітити, що `std::array<T, N>` тепер потрапляє **не** у власний вид, а в `MATX` — тобто поводиться як матриця сталого розміру з усіма її заборонами.

## 4 · Прапорці, які ставить конструктор

Конструктори — неявні (не `explicit`), по одному на кожен підтримуваний тип, і кожен лише запам'ятовує адресу. Різниця між ними — рівно в тому, яке число піде в `flags`.

**Вхідний бік.** `ACCESS_READ` тут стоїть завжди, тому в таблиці показано лише те, що додається понад нього:

| Аргумент | Прапорці `_InputArray` |
|---|---|
| `const Mat&` | `MAT` |
| `const Mat_<T>&` | `FIXED_TYPE + MAT + тип(T)` |
| `const UMat&` | `UMAT` |
| `const std::vector<T>&` | `FIXED_TYPE + STD_VECTOR + тип(T)` |
| `const std::vector<bool>&` | `FIXED_TYPE + STD_BOOL_VECTOR + CV_8U` |
| `const std::vector<std::vector<T>>&` | `FIXED_TYPE + STD_VECTOR_VECTOR + тип(T)` |
| `const std::vector<Mat>&` | `STD_VECTOR_MAT` |
| `const std::vector<Mat_<T>>&` | `FIXED_TYPE + STD_VECTOR_MAT + тип(T)` |
| `const std::vector<UMat>&` | `STD_VECTOR_UMAT` |
| `const Matx<T,m,n>&` | `FIXED_TYPE + FIXED_SIZE + MATX + тип(T)`, `sz = Size(n,m)` |
| `const T* vec, int n` | `FIXED_TYPE + FIXED_SIZE + MATX + тип(T)`, `sz = Size(n,1)` |
| `const double&` | `FIXED_TYPE + FIXED_SIZE + MATX + CV_64F`, `sz = Size(1,1)` |
| `const std::array<T,N>&` | `FIXED_TYPE + FIXED_SIZE + MATX + тип(T)`, `sz = Size(1,N)` |
| `const std::array<Mat,N>&` | `STD_ARRAY_MAT`, `sz = Size(1,N)` |
| `const cuda::GpuMat&` | `CUDA_GPU_MAT` |
| `const std::vector<cuda::GpuMat>&` | `STD_VECTOR_CUDA_GPU_MAT` |
| `const cuda::GpuMatND&` | `CUDA_GPU_MATND` |
| `const cuda::HostMem&` | `CUDA_HOST_MEM` |
| `const ogl::Buffer&` | `OPENGL_BUFFER` |

**Вихідний бік.** Тут `ACCESS_WRITE` (а для `_InputOutputArray` — `ACCESS_RW`), і саме тут ховається найнесподіваніше правило бібліотеки: **константність аргументу перетворюється на заборону**. Кожен вихідний конструктор має два перевантаження — на змінне посилання й на константне, — і константне додає `FIXED_SIZE`:

| Аргумент | `_OutputArray(T&)` | `_OutputArray(const T&)` |
|---|---|---|
| `Mat` | `MAT` | `FIXED_TYPE + FIXED_SIZE + MAT` |
| `Mat_<T>` | `FIXED_TYPE + MAT + тип(T)` | `FIXED_TYPE + FIXED_SIZE + MAT + тип(T)` |
| `UMat` | `UMAT` | `FIXED_TYPE + FIXED_SIZE + UMAT` |
| `std::vector<T>` | `FIXED_TYPE + STD_VECTOR + тип(T)` | `FIXED_TYPE + FIXED_SIZE + STD_VECTOR + тип(T)` |
| `std::vector<Mat>` | `STD_VECTOR_MAT` | `FIXED_SIZE + STD_VECTOR_MAT` |
| `std::vector<Mat_<T>>` | `FIXED_TYPE + STD_VECTOR_MAT + тип(T)` | `FIXED_TYPE + FIXED_SIZE + STD_VECTOR_MAT + тип(T)` |
| `std::vector<UMat>` | `STD_VECTOR_UMAT` | `FIXED_SIZE + STD_VECTOR_UMAT` |
| `Matx<T,m,n>` | `FIXED_TYPE + FIXED_SIZE + MATX + тип(T)` | те саме |
| `T* vec, int n` | `FIXED_TYPE + FIXED_SIZE + MATX + тип(T)` | те саме |
| `std::array<T,N>` | `FIXED_TYPE + FIXED_SIZE + MATX + тип(T)` | те саме |
| `std::array<Mat,N>` | `STD_ARRAY_MAT` | `FIXED_SIZE + STD_ARRAY_MAT` |
| `cuda::GpuMat` | `CUDA_GPU_MAT` | `FIXED_TYPE + FIXED_SIZE + CUDA_GPU_MAT` |
| `cuda::GpuMatND` | `CUDA_GPU_MATND` | — |
| `std::vector<cuda::GpuMat>` | `STD_VECTOR_CUDA_GPU_MAT` | — |
| `cuda::HostMem` | `CUDA_HOST_MEM` | `FIXED_TYPE + FIXED_SIZE + CUDA_HOST_MEM` |
| `ogl::Buffer` | `OPENGL_BUFFER` | `FIXED_TYPE + FIXED_SIZE + OPENGL_BUFFER` |
| `std::vector<bool>` | `= delete` | `= delete` |
| *(нічого)* | `NONE` | — |

Логіка позаду цієї таблиці послідовна: якщо ви віддали під приймач константний об'єкт, то бібліотека не може вважати, що має право його перевиділити, — отже, вона зобов'язується не міняти ані розмір, ані (де тип відомий) тип. `std::vector<Mat>` і `std::vector<UMat>` дістають самий лише `FIXED_SIZE`: тип елемента в них нічим не закріплений, бо кожен `Mat` усередині має власний.

Найпідступніше в цьому те, що заборона з'являється **мовчки**. Взяли параметр як `const cv::Mat&` і передали далі в `cv::resize` — компілятор задоволений, а виклик упаде під час роботи. Саме на цей випадок розраховано текст помилки: «probably due to misused `const` modifier». Яке перевантаження вибере компілятор і чому константність аргументу нікуди не зникає, розібрано в темах про [добір перевантажень](topic:sys-plang-cpp/overload-resolution) і [константну коректність](topic:sys-plang-cpp/const-correctness).

Два конструктори явно видалені:

```cpp
_OutputArray(std::vector<bool>& vec) = delete;               // not supported
_OutputArray(std::vector<std::vector<bool> >&) = delete;     // not supported
_InputOutputArray(std::vector<bool>& vec) = delete;          // not supported
```

Причина суто мовна: `std::vector<bool>` — упакований набір бітів, у ньому немає масиву байтів, куди можна писати. На вході він працює (через копіювання в новий `Mat`), на виході — заборонений на етапі компіляції. Це єдина заборона з усього контракту, яку компілятор таки ловить.

## 5 · Методи `_InputArray`

```cpp
Mat  getMat(int idx=-1) const;
Mat  getMat_(int idx=-1) const;
UMat getUMat(int idx=-1) const;
void getMatVector(std::vector<Mat>& mv) const;
void getUMatVector(std::vector<UMat>& umv) const;
void getGpuMatVector(std::vector<cuda::GpuMat>& gpumv) const;
cuda::GpuMat   getGpuMat() const;
cuda::GpuMatND getGpuMatND() const;
ogl::Buffer    getOGlBuffer() const;

int   getFlags() const;
void* getObj() const;
Size  getSz() const;

_InputArray::KindFlag kind() const;
int    dims(int i=-1) const;
int    cols(int i=-1) const;
int    rows(int i=-1) const;
Size   size(int i=-1) const;
int    sizend(int* sz, int i=-1) const;
bool   sameSize(const _InputArray& arr) const;
size_t total(int i=-1) const;
int    type(int i=-1) const;
int    depth(int i=-1) const;
int    channels(int i=-1) const;
bool   isContinuous(int i=-1) const;
bool   isSubmatrix(int i=-1) const;
bool   empty() const;
bool   empty(int i) const;
void   copyTo(const _OutputArray& arr) const;
void   copyTo(const _OutputArray& arr, const _InputArray& mask) const;
size_t offset(int i=-1) const;
size_t step(int i=-1) const;
bool isMat() const;        bool isUMat() const;
bool isMatVector() const;  bool isUMatVector() const;
bool isMatx() const;       bool isVector() const;
bool isGpuMat() const;     bool isGpuMatVector() const;
bool isGpuMatND() const;
```

Параметр `i` скрізь означає «індекс усередині набору»: для `STD_VECTOR_MAT`, `STD_VECTOR_UMAT`, `STD_VECTOR_VECTOR` і `STD_ARRAY_MAT` це номер елемента, для решти видів має бути `-1`. Для одиничних видів (`MAT`, `UMAT`, `MATX`) більшість методів починається з `CV_Assert(i < 0)`.

Предикати `is*` — однорядкові порівняння тега, крім одного:

```cpp
inline bool _InputArray::isMat() const { return kind() == _InputArray::MAT; }
inline bool _InputArray::isVector() const { return kind() == _InputArray::STD_VECTOR ||
                                                   kind() == _InputArray::STD_BOOL_VECTOR ||
                                                   (kind() == _InputArray::MATX && (sz.width <= 1 || sz.height <= 1)); }
```

Тобто `isVector()` каже не «це `std::vector`», а «це послідовність»: `Matx<double,3,1>` чи `std::array<Point2f,4>` теж дадуть `true`, бо один із вимірів дорівнює одиниці. Функції бібліотеки, які приймають набір точок, спираються саме на це.

Ще дві відповіді відрізняються від очікуваних:

- `type()` для `NONE` повертає `-1`, а не кидає виняток;
- `empty()` для `MATX` завжди `false` — розмір зашито в тип, порожнім такий масив бути не може.

## 6 · Методи `_OutputArray`

```cpp
enum DepthMask {
    DEPTH_MASK_8U = 1 << CV_8U,   DEPTH_MASK_8S  = 1 << CV_8S,
    DEPTH_MASK_16U = 1 << CV_16U, DEPTH_MASK_16S = 1 << CV_16S,
    DEPTH_MASK_32S = 1 << CV_32S, DEPTH_MASK_32F = 1 << CV_32F,
    DEPTH_MASK_64F = 1 << CV_64F, DEPTH_MASK_16F = 1 << CV_16F,
    DEPTH_MASK_ALL = (DEPTH_MASK_64F<<1)-1,
    DEPTH_MASK_ALL_BUT_8S = DEPTH_MASK_ALL & ~DEPTH_MASK_8S,
    DEPTH_MASK_ALL_16F = (DEPTH_MASK_16F<<1)-1,
    DEPTH_MASK_FLT = DEPTH_MASK_32F + DEPTH_MASK_64F
};

void create(Size sz, int type, int i=-1, bool allowTransposed=false,
            DepthMask fixedDepthMask=static_cast<DepthMask>(0)) const;
void create(int rows, int cols, int type, int i=-1, bool allowTransposed=false,
            DepthMask fixedDepthMask=static_cast<DepthMask>(0)) const;
void create(int dims, const int* size, int type, int i=-1, bool allowTransposed=false,
            DepthMask fixedDepthMask=static_cast<DepthMask>(0)) const;
void createSameSize(const _InputArray& arr, int mtype) const;

void release() const;
void clear() const;
void setTo(const _InputArray& value, const _InputArray& mask = _InputArray()) const;

bool needed() const;
bool fixedSize() const;
bool fixedType() const;

Mat&  getMatRef(int i=-1) const;
UMat& getUMatRef(int i=-1) const;
cuda::GpuMat&   getGpuMatRef() const;
cuda::GpuMatND& getGpuMatNDRef() const;
std::vector<cuda::GpuMat>& getGpuMatVecRef() const;
ogl::Buffer&    getOGlBufferRef() const;
cuda::HostMem&  getHostMemRef() const;

void assign(const Mat& m) const;   void assign(const std::vector<Mat>& v) const;
void assign(const UMat& u) const;  void assign(const std::vector<UMat>& v) const;
void move(Mat& m) const;           void move(UMat& u) const;
```

Три перевантаження `create` зводяться до третього; перші два лише впаковують розмір у масив. Параметр `allowTransposed` дозволяє прийняти вже виділений буфер, у якого переставлені рядки й стовпці (це рятує від зайвого виділення в матричних розкладах). `fixedDepthMask` — набір глибин, які функція згодна прийняти замість запитаної: якщо приймач має заборону типу, але його глибина є в масці й кількість каналів збігається, `create` мовчки бере тип приймача замість свого.

Опитувальні методи — однорядкові:

```cpp
bool _OutputArray::needed() const     { return kind() != NONE; }
bool _OutputArray::fixedSize() const  { return (flags & FIXED_SIZE) == FIXED_SIZE; }
bool _OutputArray::fixedType() const  { return (flags & FIXED_TYPE) == FIXED_TYPE; }
```

`createSameSize` — обгортка на два рядки, яка бере кількість вимірів і розміри з іншого проксі:

```cpp
void _OutputArray::createSameSize(const _InputArray& arr, int mtype) const
{
    int arrsz[CV_MAX_DIM], d = arr.sizend(arrsz);
    create(d, arrsz, mtype);
}
```

`assign` і `move` різняться саме тим, чим і мають: `assign` копіює, `move` віддає буфер без копіювання — але **лише** коли це можливо. Обидва вміють рівно три види, `MAT`, `UMAT` і `MATX`; для решти кидають `CV_Error(Error::StsNotImplemented, "")` з порожнім повідомленням.

```cpp
void _OutputArray::move(Mat& m) const
{
    if (fixedSize())
    {
        assign(m);          // ← заборона розміру мовчки перетворює переміщення на копію
        return;
    }
    int k = kind();
    if (k == UMAT)      { m.copyTo(*(UMat*)obj); m.release(); }
    else if (k == MAT)  { *(Mat*)obj = std::move(m); }
    else if (k == MATX) { m.copyTo(getMat()); m.release(); }
    else CV_Error(Error::StsNotImplemented, "");
}
```

Перший рядок пояснює цілу категорію «загадкових» просідань: приймач, переданий як константне посилання, має `FIXED_SIZE`, і кожне `move` у ньому — насправді повне копіювання пікселів. Ані попередження, ані винятку.

`release()` починається з `CV_Assert(!fixedSize())` — отже, звільнити приймач, що прийшов константним, неможливо взагалі. `clear()` для `MAT` вимагає того самого й робить `resize(0)`, а для всіх інших видів просто кличе `release()`.

## 7 · `_InputOutputArray` і `noArray()`

`_InputOutputArray` не додає нічого, крім конструкторів із `ACCESS_RW`:

```cpp
inline _InputOutputArray::_InputOutputArray() { init(0+ACCESS_RW, 0); }
inline _InputOutputArray::_InputOutputArray(Mat& m) { init(+MAT+ACCESS_RW, &m); }
inline _InputOutputArray::_InputOutputArray(const Mat& m)
{ init(FIXED_TYPE + FIXED_SIZE + MAT + ACCESS_RW, &m); }
```

Порожній проксі — один на всю програму:

```cpp
static _InputOutputArray _none;
InputOutputArray noArray() { return _none; }
```

Це статичний об'єкт із `flags == ACCESS_RW`, тобто `kind() == NONE`, і саме тому він безпечний для спільного вжитку: `needed()` для нього — `false`, функція пропускає весь блок обчислень і ніколи не пише в `_none`. Порядок у функції обов'язковий саме такий: спершу `needed()`, потім `create()`. Якщо переплутати, `create` дійде до окремої гілки й кине зрозумілий виняток — `"create() called for the missing output array"`.

## 8 · Що для якого виду працює

`getMat()` дає різні речі різною ціною — і саме тут видно, що вид джерела вирішує не лише тип, а й обсяг роботи:

| Вид | Що робить `getMat()` |
|---|---|
| `MAT` | копія заголовка, лічильник посилань +1, нуль скопійованих пікселів |
| `MATX` | `Mat(sz, flags, obj)` — заголовок **прямо над полями** `Matx`; запис у нього пише в об'єкт викликача |
| `STD_VECTOR`, `STD_VECTOR_VECTOR` | `Mat(1, v->size(), t, v->data())` — заголовок `1×N` над буфером вектора, без володіння |
| `STD_BOOL_VECTOR` | виділення пам'яті + поелементне перетворення бітів у байти — **єдиний вид із копіюванням** |
| `STD_VECTOR_MAT`, `STD_ARRAY_MAT`, `STD_VECTOR_UMAT` | елемент за індексом `i` (для `UMat` — через відображення) |
| `UMAT` | відображення буфера прискорювача в адресний простір процесора: очікування черги команд, на дискретній карті — ще й шина |
| `CUDA_HOST_MEM` | `createMatHeader()`, `CV_Assert(i < 0)` |
| `NONE` | порожній `Mat()` |
| `CUDA_GPU_MAT`, `CUDA_GPU_MATND`, `OPENGL_BUFFER` | **виняток** |

Заголовок над чужим буфером нічим не володіє й нічого не тримає при житті — механіку цього розібрано в темі про [види без копії](topic:sys-media/mat-views-no-copy), а лічильник посилань, який працює лише для першого рядка таблиці, — у темі про [пам'ять `Mat`](topic:sys-media/mat-memory-model).

Решта методів отримання:

| Метод | Працює для | Інакше |
|---|---|---|
| `getUMat()` | `UMAT`, `STD_VECTOR_UMAT`, `MAT` (через `Mat::getUMat`) | падає назад на `getMat(i).getUMat(...)` — тобто успадковує помилки `getMat` |
| `getMatVector()` | `MAT`, `MATX`, `STD_VECTOR`, `STD_VECTOR_VECTOR`, `STD_VECTOR_MAT`, `STD_ARRAY_MAT`, `STD_VECTOR_UMAT`, `NONE` | `"Unknown/unsupported array type"` |
| `getGpuMat()` | `CUDA_GPU_MAT`, `CUDA_HOST_MEM`, `NONE` | див. §9 |
| `copyTo()` | `NONE`, `MAT`, `MATX`, `STD_VECTOR`, `STD_BOOL_VECTOR`, `UMAT`, `CUDA_GPU_MAT` | `CV_Error` із порожнім повідомленням |

Один рядок звідси вартий окремої уваги. `getMatVector()` для виду `MAT` **розбирає одне зображення на рядки**:

```cpp
const Mat& m = *(const Mat*)obj;
int n = (int)m.size[0];
mv.resize(n);
for( i = 0; i < n; i++ )
    mv[i] = m.dims == 2 ? Mat(1, m.cols, m.type(), (void*)m.ptr(i)) :
        Mat(m.dims-1, &m.size[1], m.type(), (void*)m.ptr(i), &m.step[1]);
```

Тобто передати `Mat` розміром 480×640 у параметр `InputArrayOfArrays` — законно, і функція побачить чотириста вісімдесят однорядкових зображень. Жодної помилки не буде; буде дивний результат.

Що дозволяє `create()` для кожного виду:

| Вид | `create()` |
|---|---|
| `MAT`, `UMAT` | повне перевиділення, якщо немає заборон; при збігу розміру й типу — ранній вихід без роботи |
| `MATX` | нічого не виділяє; лише звіряє тип і розмір із зашитими в тип, `CV_CheckLE(d, 2, "")` |
| `STD_VECTOR`, `STD_VECTOR_VECTOR` | `resize` вектора; лише `1×N` або `N×1` — двовимірна матриця у вектор не влізе |
| `STD_VECTOR_MAT`, `STD_VECTOR_UMAT`, `STD_ARRAY_MAT` | з `i < 0` — змінює довжину набору, з `i ≥ 0` — виділяє `i`-й елемент |
| `NONE` | виняток `StsNullPtr` |

І кому дозволено віддати посилання на сам об'єкт:

| Метод | Умова |
|---|---|
| `getMatRef(-1)` | `CV_Assert(k == MAT)` |
| `getMatRef(i ≥ 0)` | `CV_Assert(k == STD_VECTOR_MAT \|\| k == STD_ARRAY_MAT)` |
| `getUMatRef(-1)` | `CV_Assert(k == UMAT)` |
| `getUMatRef(i ≥ 0)` | `CV_Assert(k == STD_VECTOR_UMAT)` |
| `getGpuMatRef()` | `CV_Assert(k == CUDA_GPU_MAT)` |

## 9 · Винятки: повна таблиця

Усе нижче кидає `cv::Exception` — і `CV_Assert`, і `CV_Error` роблять це однаково, тож ловити треба [звичайним `catch`](topic:sys-plang-cpp/exceptions-mechanism), а не сподіватися на код повернення.

| Виклик | Вид | Повідомлення |
|---|---|---|
| `getMat()` | `CUDA_GPU_MAT` | `"You should explicitly call download method for cuda::GpuMat object"` |
| `getMat()` | `CUDA_GPU_MATND` | `"You should explicitly call download method for cuda::GpuMatND object"` |
| `getMat()` | `OPENGL_BUFFER` | `"You should explicitly call mapHost/unmapHost methods for ogl::Buffer object"` |
| `getMat(i ≥ 0)` | `CUDA_HOST_MEM` | `CV_Assert( i < 0 )` |
| `getGpuMat()` | `OPENGL_BUFFER` | `"You should explicitly call mapDevice/unmapDevice methods for ogl::Buffer object"` |
| `getGpuMat()` | усе, крім `CUDA_GPU_MAT`, `CUDA_HOST_MEM`, `NONE` | `"getGpuMat is available only for cuda::GpuMat and cuda::HostMem"` |
| будь-який CUDA-виклик | збірка без `HAVE_CUDA` | `"CUDA support is not enabled in this OpenCV build (missing HAVE_CUDA)"` |
| `release()` для `OPENGL_BUFFER` | збірка без `HAVE_OPENGL` | `"OpenGL support is not enabled in this OpenCV build (missing HAVE_OPENGL)"` |
| `create()` | `NONE` | `StsNullPtr`, `"create() called for the missing output array"` |
| `create()` | `MAT` з `FIXED_TYPE` й іншим типом | `"Can't reallocate Mat with locked type (probably due to misused 'const' modifier)"` |
| `create()` | `MAT` з `FIXED_SIZE` й іншим розміром | `"Can't reallocate Mat with locked size (probably due to misused 'const' modifier)"` |
| `create()` | порожній `MAT` із `FIXED_TYPE + FIXED_SIZE` | `"Can't reallocate empty Mat with locked layout (probably due to misused 'const' modifier)"` |
| `create()` | `MATX` з іншим типом чи розміром | `CV_Assert` / `CV_CheckEQ` без тексту |
| `create()` | `MATX`, запит більш ніж двох вимірів | `CV_CheckLE(d, 2, "")` |
| `create()` | `STD_VECTOR` з `FIXED_SIZE` | `CV_Assert(!fixedSize())` |
| `create()` | `STD_VECTOR`, запит двовимірної матриці | `CV_Assert(d == 2 && (sizes[0] == 1 \|\| sizes[1] == 1 \|\| sizes[0]*sizes[1] == 0))` |
| `create()` | `STD_VECTOR` з іншим типом елемента | `CV_Assert( mtype == type0 \|\| … )` |
| `create()` | невідомий вид | `"Unknown/unsupported array type"` |
| `release()`, `clear()` для `MAT` | будь-який вид із `FIXED_SIZE` | `CV_Assert(!fixedSize())` |
| `assign()`, `move()` | усе, крім `MAT`, `UMAT`, `MATX` | `StsNotImplemented`, порожнє повідомлення |
| `getMatRef()`, `getUMatRef()`, `getGpuMatRef()` | невідповідний вид | `CV_Assert` без тексту (див. §8) |
| `size(i ≥ 0)` | `MAT`, `UMAT`, `MATX` | `CV_Assert( i < 0 )` |
| `type()` | порожній `STD_VECTOR_UMAT` без `FIXED_TYPE` | `CV_Assert((flags & FIXED_TYPE) != 0)` |
| `empty()`, `type()` | невідомий вид | `"Unknown/unsupported array type"` |

Найчастіші з них у робочому коді — три рядки про `const`. Усі вони означають одне: аргумент приймача був константним, конструктор поставив `FIXED_SIZE`, а функція спробувала виділити пам'ять.

## 10 · Мінімальний коректний виклик

Порядок дій, якого дотримується вся бібліотека, — рівно такий:

```cpp
void scaleAndMask(cv::InputArray _src, cv::OutputArray _dst,
                  cv::OutputArray _mask, double k)
{
    // 1. Заборонене відсіюємо явно — до першого дотику до пам'яті.
    CV_Assert(!_src.empty());
    CV_Assert(_src.kind() != cv::_InputArray::CUDA_GPU_MAT);

    // 2. Вхід беремо ДО create: вхід і вихід можуть виявитися тим самим об'єктом.
    cv::Mat src = _src.getMat();

    // 3. Виділяємо приймач. Розмір збігається — виклик нічого не робить.
    _dst.create(src.size(), src.type());
    cv::Mat dst = _dst.getMat();

    src.convertTo(dst, src.type(), k);

    // 4. Необов'язковий вихід — лише якщо його справді просили.
    if (_mask.needed())
    {
        _mask.create(src.size(), CV_8UC1);
        cv::Mat mask = _mask.getMat();
        cv::compare(dst, 0, mask, cv::CMP_GT);
    }
}
```

Виклик без маски виглядає так:

```cpp
cv::Mat out;
scaleAndMask(frame, out, cv::noArray(), 1.5);
```

Коли поведінка все-таки розходиться з очікуваною, найкоротший шлях до причини — надрукувати `flags` розкладеними на частини:

```cpp
std::string describe(const cv::_InputArray& a)
{
    static const char* names[] = {
        "NONE","MAT","MATX","STD_VECTOR","STD_VECTOR_VECTOR","STD_VECTOR_MAT",
        "<removed EXPR>","OPENGL_BUFFER","CUDA_HOST_MEM","CUDA_GPU_MAT","UMAT",
        "STD_VECTOR_UMAT","STD_BOOL_VECTOR","STD_VECTOR_CUDA_GPU_MAT",
        "<removed STD_ARRAY>","STD_ARRAY_MAT","CUDA_GPU_MATND" };

    const int f = a.getFlags();
    std::string s = names[(f & cv::_InputArray::KIND_MASK) >> cv::_InputArray::KIND_SHIFT];

    if (f & cv::ACCESS_READ)   s += " READ";
    if (f & cv::ACCESS_WRITE)  s += " WRITE";
    if (f & cv::_InputArray::FIXED_TYPE) s += " FIXED_TYPE";
    if (f & cv::_InputArray::FIXED_SIZE) s += " FIXED_SIZE";
    return s;
}
```

Для `cv::Mat m; describe(cv::_OutputArray(m));` це дасть `MAT WRITE`, а для того самого `m`, схопленого як `const cv::Mat&`, — `MAT WRITE FIXED_TYPE FIXED_SIZE`. Один рядок виводу відрізняє робочий виклик від того, що впаде на першому ж кадрі іншого розміру.

Прапорці `ACCESS_READ` / `ACCESS_WRITE` у цьому виводі мають ще й цілком практичну вагу: для `UMAT` вони вирішують, чи взагалі тягнути пікселі з пам'яті прискорювача на хост, — ціну цих перетинів розібрано в темі про [бекенди й прискорення](topic:sys-media/opencv-backends).
