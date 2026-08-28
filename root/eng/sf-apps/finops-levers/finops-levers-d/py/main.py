# Рахунок за місяць на РОЗДРІБІ: платимо лише за ввімкнені години.
def retail_cost(retail_per_hour, hours_used):
    return retail_per_hour * hours_used

# Рахунок за місяць на ОБІЦЯНЦІ: платимо за ВСІ години місяця,
# байдуже, ввімкнена машина чи ні (знижена ставка × повний строк).
def committed_cost(committed_per_hour, hours_in_month):
    return committed_per_hour * hours_in_month

# Поріг завантаження, за яким обіцянка зрівнюється з роздробом.
# Прирівнюємо рахунки:  retail·H_used = committed·H_month
#   →  H_used / H_month = committed / retail
def breakeven_utilization(committed_per_hour, retail_per_hour):
    return committed_per_hour / retail_per_hour   # частка годин (0..1)
