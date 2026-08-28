// ХИБНО: защіпуємо, не глянувши на ready — ловимо сміття з неготової шини.
case S_READ:
    c.reg_write = true;                 // ← увімкнули запис БЕЗУМОВНО
    c.reg_dst   = cu->dst;
    dp->reg[cu->dst] = dp->data_bus;    // data_bus ще не оновлена!
    cu->stage = S_DONE;
    break;

// ПРАВИЛЬНО: тримаємо read і чекаємо; защіпуємо ЛИШЕ коли ready=1.
case S_READ:
    c.mem_read = true;
    if (!dp->mem_ready) break;          // ← петля чекання: ще не готово — стоїмо
    c.reg_write = true;
    c.reg_dst   = cu->dst;
    dp->reg[cu->dst] = dp->data_bus;
    cu->stage = S_DONE;
    break;
