// виробник: зайняти → записати → опублікувати
let seq = cursor.fetch_add(1, Ordering::Relaxed) + 1;
slots[(seq & mask) as usize] = event;        // маска замість ділення
published.store(seq, Ordering::Release);     // бар'єр: запис у комірку видно ДО публікації

// споживач: прочитати все опубліковане — одним пакетом
let avail = published.load(Ordering::Acquire);
while next <= avail {
    handle(&slots[(next & mask) as usize]);
    next += 1;
}
