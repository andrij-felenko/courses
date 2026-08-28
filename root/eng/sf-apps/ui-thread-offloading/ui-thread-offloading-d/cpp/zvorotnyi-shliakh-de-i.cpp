std::atomic<uint64_t> generation{0};     // читає фон, пише потік інтерфейсу

void onQueryChanged(std::string text) {
    const uint64_t my = generation.fetch_add(1) + 1;
    pool.submit([this, text = std::move(text), my] {
        auto rows = search(text);                       // фоновий потік
        postToUiThread([this, rows = std::move(rows), my] {
            if (my != generation.load()) return;         // застаріла відповідь
            renderRows(rows);                            // тут ми знову власник дерева
        });
    });
}
