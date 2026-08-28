/* Ручний контроль пам'яті cJSON */
cJSON *root = cJSON_Parse(payload_buffer);
if (!root) {
    return ERR_INVALID_JSON;
}
cJSON *dev_id = cJSON_GetObjectItemCaseSensitive(root, "device_id");
if (!cJSON_IsString(dev_id) || (dev_id->valuestring == NULL)) {
    cJSON_Delete(root); /* Пропуск виклику в складній гілці веде до витоку пам'яті */
    return ERR_MISSING_FIELD;
}
const char *id_str = dev_id->valuestring;
/* ... використання id_str ... */
cJSON_Delete(root);
