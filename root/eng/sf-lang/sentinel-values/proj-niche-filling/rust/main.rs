use std::mem::size_of;
use std::num::NonZeroU32;

fn main() {
    // 1. Звичайний Option<u32>: 4 байти payload + 1 байт тег + 3 байти padding = 8 байтів
    println!("sizeof(Option<u32>):          {} байтів", size_of::<Option<u32>>()); // 8

    // 2. Option<NonZeroU32>: 0 кодує None -> рівно 4 байти (0% оверхеду!)
    println!("sizeof(Option<NonZeroU32>):  {} байти",  size_of::<Option<NonZeroU32>>()); // 4

    // 3. Option<&i32>: null вказівник кодує None -> рівно 8 байтів
    println!("sizeof(Option<&i32>):        {} байтів", size_of::<Option<&i32>>()); // 8

    // 4. Багатошарове вкладення в тип bool завдяки 254 вільним нішам:
    // Option<bool> використовує нішу 2 для None -> 1 байт!
    println!("sizeof(Option<bool>):        {} байт",   size_of::<Option<bool>>()); // 1
    // Option<Option<bool>> використовує нішу 3 для зовнішнього None -> все ще 1 байт!
    println!("sizeof(Option<Option<bool>>): {} байт",  size_of::<Option<Option<bool>>>()); // 1
}
