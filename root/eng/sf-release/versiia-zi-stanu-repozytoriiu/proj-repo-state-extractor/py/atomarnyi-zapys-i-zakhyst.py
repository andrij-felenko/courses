def write_header_atomically(header_path, content):
    # Якщо файл уже існує на диску і його вміст збігається — зберігаємо старий mtime
    if os.path.exists(header_path):
        with open(header_path, "r", encoding="utf-8") as existing:
            if existing.read() == content:
                return False # Файл не змінювався, перезбірка залежних одиниць не потрібна

    tmp_path = header_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Атомарна заміна файлу в межах однієї файлової системи
    os.replace(tmp_path, header_path)
    return True
