// Танкове змішування: одна ручка → дві швидкості моторів (−100..+100 кожна).
struct Motors { int left, right; };

Motors tankMix() {
    int drive = readAxis(vertical);     // вперед/назад: спільна складова
    int turn  = readAxis(horizontal);   // ліворуч/праворуч: різницева складова

    int left  = drive + turn;           // праворуч → лівий мотор швидше
    int right = drive - turn;           // ... а правий повільніше

    left  = constrain(left,  -100, 100);
    right = constrain(right, -100, 100);
    return { left, right };
}
