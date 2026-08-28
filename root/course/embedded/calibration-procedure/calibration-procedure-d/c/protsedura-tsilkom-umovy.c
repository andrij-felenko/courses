#define CAL_MAGIC 0xCA10B00Fu   // мітка «тут лежить чинне калібрування»

typedef struct {
    uint32_t magic;             // == CAL_MAGIC, якщо коефіцієнти записані
    float    k;
    float    b;
} cal_store_t;

// старт: підняти калібрування з NVS; якщо мітки немає — давач некалібрований
bool cal_load(cal_t *out)
{
    cal_store_t s;
    if (!nvs_read("cal", &s, sizeof s) || s.magic != CAL_MAGIC)
        return false;           // нема чинних коефіцієнтів → треба калібрувати
    out->k = s.k;
    out->b = s.b;
    return true;
}

// кінець калібрування: зберегти коефіцієнти назавжди
bool cal_save(const cal_t *c)
{
    cal_store_t s = { .magic = CAL_MAGIC, .k = c->k, .b = c->b };
    return nvs_write("cal", &s, sizeof s);
}
