# Перегляд загальної кількості слотів
cat /sys/kernel/debug/swiotlb/io_tlb_nslabs

# Перегляд кількості зайнятих слотів прямо зараз
cat /sys/kernel/debug/swiotlb/io_tlb_used

# Перегляд пікового значення використання
cat /sys/kernel/debug/swiotlb/io_tlb_used_highwater

# Перевірка кількості переповнень пулу
cat /sys/kernel/debug/swiotlb/io_tlb_overflow
