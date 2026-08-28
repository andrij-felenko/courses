use std::collections::HashSet;

fn fetch_before_cached(
    store: &impl Store,
    empty: &mut HashSet<(u64, u64)>, // відомо-порожні партиції (channel_id, bucket)
    channel_id: u64,
    before: u64,
    limit: usize,
) -> Page {
    let mut out = Vec::with_capacity(limit);
    let start = bucket_of(before); // крайнє (найновіше) відро цього запиту

    for bucket in buckets_desc(channel_id, before) {
        if empty.contains(&(channel_id, bucket)) {
            continue; // уже знаємо: тут порожньо — навіть не турбуємо сховище
        }
        let need = limit - out.len();
        let rows = store.query_partition(channel_id, bucket, before, need);
        if rows.is_empty() {
            // Кешувати «порожнє» можна ЛИШЕ там, де фільтр `before` не міг сховати рядки.
            // У крайньому відрі нуль означає «усі повідомлення >= before», а не «відро
            // пусте» — його позначати не можна, інакше наступний запит із більшим
            // before хибно проскочить відро, у якому насправді є що читати.
            if bucket < start {
                empty.insert((channel_id, bucket));
            }
            continue;
        }
        out.extend(rows);
        if out.len() >= limit { break; }
    }

    let next_before = out.last().map(|m| m.id);
    Page { messages: out, next_before }
}
