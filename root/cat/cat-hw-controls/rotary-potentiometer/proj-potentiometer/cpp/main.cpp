int lastAccepted = -1000;            // останнє значення, яке ми «визнали» (свідомо поза діапазоном)
const int DEADBAND = 4;              // поріг у одиницях АЦП: менша зміна — це спокій

// Повертає true й оновлює *out, ЛИШЕ якщо значення реально змінилося.
bool potChanged(int fresh, int *out) {
  if (abs(fresh - lastAccepted) >= DEADBAND) {   // відійшло далі за поріг — це справжня зміна
    lastAccepted = fresh;
    *out = fresh;
    return true;
  }
  return false;                                  // у межах порогу — мовчимо
}
