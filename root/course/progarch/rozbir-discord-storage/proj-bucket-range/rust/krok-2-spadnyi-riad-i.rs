/// Одне повідомлення (лишили тільки те, що треба сторінці).
struct Message { id: u64 /* Snowflake */ }

/// Абстракція над сховищем: одне звернення = одна партиція (channel_id, bucket).
/// Рядки повертаються спадним message_id, з фільтром message_id < before, ≤ limit.
trait Store {
    fn query_partition(&self, channel_id: u64, bucket: u64, before: u64, limit: usize)
        -> Vec<Message>;
}

/// Номери відер від курсора `before` (включно) НАЗАД до відра створення каналу
/// (теж включно). channel_id — теж Snowflake, тож його відро і є дном.
fn buckets_desc(channel_id: u64, before: u64) -> impl DoubleEndedIterator<Item = u64> {
    let floor = bucket_of(channel_id); // раніше каналу не існувало — глибше не йдемо
    let start = bucket_of(before);     // з якого відра починаємо
    // Якщо курсор старіший за сам канал (start < floor) — діапазон порожній,
    // .rev() дає порожній ітератор, і жодного скану не буде.
    (floor..=start).rev()
}

struct Page { messages: Vec<Message>, next_before: Option<u64> }

fn fetch_before(store: &impl Store, channel_id: u64, before: u64, limit: usize) -> Page {
    let mut out: Vec<Message> = Vec::with_capacity(limit);

    for bucket in buckets_desc(channel_id, before) {
        let need = limit - out.len();
        let rows = store.query_partition(channel_id, bucket, before, need);
        out.extend(rows);
        if out.len() >= limit {
            break; // набрали повний екран — глибше в минуле не лізьмо
        }
    }

    let next_before = out.last().map(|m| m.id); // курсор наступної сторінки
    Page { messages: out, next_before }
}
