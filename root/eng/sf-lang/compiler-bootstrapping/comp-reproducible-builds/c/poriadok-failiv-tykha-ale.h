// НЕДЕТЕРМІНОВАНО: обробляємо у «сирому» порядку файлової системи.
DIR *d = opendir("src");
struct dirent *e;
while ((e = readdir(d)) != NULL)      // порядок НЕ визначений стандартом
    add_to_archive(e->d_name);        // → архів у кожного свій

// ДЕТЕРМІНОВАНО: спершу зібрати список, відсортувати, тоді обробляти.
collect_names(names, "src");
qsort(names, n, sizeof(char*), cmp_str);   // однаковий порядок скрізь
for (size_t i = 0; i < n; i++)
    add_to_archive(names[i]);          // → архів у всіх однаковий
