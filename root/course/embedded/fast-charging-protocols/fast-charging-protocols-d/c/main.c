// Хоч би скільки ват пропонував протокол (PD/PPS, QC, VOOC),
// фактичну стелю струму диктує температура комірки.
float charge_current_limit(float cell_temp_c, float proto_max_a) {
    float limit;
    if (cell_temp_c < 0.0f)        limit = 0.0f;   // нижче нуля Li-ion не заряджаємо
    else if (cell_temp_c < 10.0f)  limit = 0.5f;   // холодно — лише малий струм
    else if (cell_temp_c < 40.0f)  limit = proto_max_a; // норма — бери все, що дають
    else if (cell_temp_c < 45.0f)  limit = proto_max_a * 0.5f; // гаряче — удвічі менше
    else                           limit = 0.0f;   // перегрів — стоп

    // Ніколи не беремо більше, ніж дозволив контракт із джерелом.
    return (limit < proto_max_a) ? limit : proto_max_a;
}
