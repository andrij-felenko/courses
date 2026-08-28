// було: кожна ітерація б'є в пам'ять, спільну з сусідами по лінії
for (size_t i = lo; i < hi; ++i)
    if (match(data[i]))
        ++counters[tid];

// стало: сума живе в регістрі, у пам'ять іде один запис на весь цикл
long local = 0;
for (size_t i = lo; i < hi; ++i)
    if (match(data[i]))
        ++local;
counters[tid] += local;
