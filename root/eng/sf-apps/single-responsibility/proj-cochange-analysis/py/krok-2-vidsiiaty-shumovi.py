def cochange(commits, max_files=12):
    """Лічильники: скільки разів мінявся кожен файл і кожна пара разом."""
    file_count = Counter()
    pair_count = Counter()
    for files in commits:
        if len(files) > max_files:            # відсів шумового мега-коміту
            continue
        for f in files:
            file_count[f] += 1
        for a, b in combinations(sorted(files), 2):
            pair_count[(a, b)] += 1
    return file_count, pair_count
