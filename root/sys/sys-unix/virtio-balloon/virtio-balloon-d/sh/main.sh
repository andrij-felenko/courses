# Перевірка поточного розміру пам'яті та лімітів балона
virsh dominfo vm-database | grep -E "(Max memory|Used memory)"

# Зміна фактично виділеної пам'яті (надування або здування балона)
# Зменшуємо пам'ять гостя vm-database до 8 ГБ (8388608 КіБ)
virsh setmem vm-database 8388608 --live

# Увімкнення періодичного збору статистики statsq (кожні 3 секунди)
virsh dommemstat vm-database --period 3

# Перегляд детальної телеметрії пам'яті гостя
virsh dommemstat vm-database
