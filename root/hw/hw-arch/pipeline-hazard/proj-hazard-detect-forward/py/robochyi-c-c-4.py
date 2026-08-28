# Один такт конвеєра. Порядок дій усередині — критичний.
def tick(c: Cpu) -> None:
    # --- 1. ДЕТЕКЦІЯ: чи треба гальмувати цього такту? ---
    stall = load_use_stall(c)

    # --- 2. ВИКОНАННЯ (стадія ВК працює над тим, що в ID/EX) ---
    ex = replace(c.reg[1])             # копія: рахуємо над нею
    if ex.valid:
        # проброс: обидва входи ALU беремо через наглядача
        a = forward(c, ex.rs1)
        b = forward(c, ex.rs2) if ex.op in (OP_ADD, OP_SUB) else ex.imm
        if ex.op == OP_ADD:
            ex.val = a + b; ex.wen = (ex.rd != 0)
        elif ex.op == OP_SUB:
            ex.val = a - b; ex.wen = (ex.rd != 0)
        elif ex.op == OP_LOAD:
            # адресу порахували; значення дочитаємо у стадії ПМ
            ex.val = a + ex.imm; ex.wen = False
        elif ex.op == OP_BRANCH:
            # умова: стрибаємо, якщо джерело ненульове
            if a != 0:
                c.take_branch = True
                c.branch_pc = ex.imm
            ex.wen = False
        else:
            ex.wen = False

    # --- 3. ДОСТУП ДО ПАМ'ЯТІ (стадія ПМ працює над тим, що в EX/MEM) ---
    mem = replace(c.reg[2])
    if mem.valid and mem.op == OP_LOAD:
        mem.val = mem_read(mem.val)    # тепер значення справді є
        mem.wen = (mem.rd != 0)        # завантаження пише — якщо не в R0

    # --- 4. ЗАПИС (стадія ЗП працює над тим, що в MEM/WB) ---
    wb = c.reg[3]
    if wb.valid and wb.wen and wb.rd != 0:
        c.regfile[wb.rd] = wb.val      # єдине місце, де регістровий файл змінюється

    # --- 5. ЗСУВ: посунути конвеєр на такт (від пізніх стадій до ранніх) ---
    c.reg[3] = mem                     # ПМ → MEM/WB (завжди)
    c.reg[2] = ex                      # ВК → EX/MEM: САМЕ завантаження йде далі
                                       # по своє значення — його чіпати не можна

    if stall:
        # СТОП рівно на такт. Ранні стадії ТРИМАЄМО: команда-споживач
        # лишається у reg[0], pc не рушає (fetch не кличемо). А в ID/EX,
        # звідки споживач НЕ пройшов у ВК, впускаємо бульбашку — це вона
        # поїде у ВК наступного такту, а не реальна команда.
        c.reg[1] = bubble()            # порожній прохід замість споживача
        # reg[0] і pc НЕ чіпаємо — споживач і решта застрягли на такт
    else:
        c.reg[1] = c.reg[0]            # ID → ID/EX
        c.reg[0] = fetch(c)            # вибірка нової команди за pc

    # --- 6. ЗМИВ: якщо ВК підняла «перехід узято» — стерти наперед вибране ---
    if c.take_branch:
        c.reg[0] = bubble()            # стерти те, що вибрали за переходом…
        c.reg[1] = bubble()            # …на обох ранніх стадіях
        c.pc = c.branch_pc             # і вибирати з правильної адреси
        c.take_branch = False
