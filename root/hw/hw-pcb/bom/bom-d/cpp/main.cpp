// Перевірка одного рядка BOM перед відправленням на виробництво.
// refdes_count — скільки позначень фактично перелічено (R7,R8 → 2);
// qty — заявлена кількість; has_mpn — чи вказано номер деталі; dnp — чи це «не монтувати».
// Повертає 0, якщо рядок чистий, або код проблеми.
int bom_check_row(int refdes_count, int qty, bool has_mpn, bool dnp)
{
    if (refdes_count != qty)
        return 1;                 // кількість не сходиться з переліком позначень
    if (!dnp && !has_mpn)
        return 2;                 // монтуємо, але немає MPN — закупити нічим
    return 0;                     // рядок придатний
}
// bom_check_row(2, 2, true,  false) -> 0   (R7,R8 — два, MPN є: чисто)
// bom_check_row(2, 3, true,  false) -> 1   (перелічено двоє, а написано «3»: розбіжність)
// bom_check_row(1, 1, false, false) -> 2   (монтуємо без MPN: нічого замовити)
