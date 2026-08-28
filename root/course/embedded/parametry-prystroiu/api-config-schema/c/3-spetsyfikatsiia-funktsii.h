/**
 * @brief Повна ініціалізація конфігураційного сховища при старті ядра.
 * 
 * Послідовність дій:
 * 1. Читає службові заголовки Slot A та Slot B;
 * 2. Перевіряє магічні байти та цілісність контрольних сум CRC-32;
 * 3. Обирає сектор із найбільшим значенням sequence_number;
 * 4. Якщо версія схеми у Flash старіша за CURRENT_SCHEMA_VER, викликає ланцюжок міграторів;
 * 5. Якщо жоден сектор не є валідним — завантажує заводські дефолти у RAM та ініціалізує Flash;
 * 6. Копіює активний стан у захищену RAM-структуру g_active_config.
 * 
 * @return CFG_OK у разі успіху або відповідний код помилки CFG_ERR_*.
 */
cfg_status_t cfg_manager_init(void);

/**
 * @brief Читання значення цілочисельного параметра за числовим ключем.
 * 
 * @param key_id  Ідентифікатор параметра з таблиці дескрипторів.
 * @param out_val Вказівник на змінну для запису результату.
 * @return CFG_OK або CFG_ERR_NOT_FOUND, якщо ідентифікатор не зареєстрований.
 */
cfg_status_t cfg_get_uint32(uint16_t key_id, uint32_t *out_val);

/**
 * @brief Читання рядкового параметра у виділений користувацький буфер.
 * 
 * @param key_id  Ідентифікатор параметра.
 * @param out_buf Вказівник на цільовий масив символів.
 * @param buf_len Розмір буфера (зобов'язаний вміщувати рядок разом із нуль-термінатором).
 * @return CFG_OK або CFG_ERR_BUFFER_TOO_SMALL.
 */
cfg_status_t cfg_get_string(uint16_t key_id, char *out_buf, size_t buf_len);

/**
 * @brief Попередня валідація кандидата конфігурації без застосування.
 * 
 * Виконує повний прохід по словнику дескрипторів, перевіряє межі кожного поля,
 * контролює спроби перезапису Read-Only параметрів та виконує матрицю
 * крос-параметричних правил узгодженості.
 * 
 * @param candidate_payload Вказівник на буфер з новою структурою параметрів.
 * @param len               Розмір буфера у байтах.
 * @return CFG_OK або код виявленого порушення валідації.
 */
cfg_status_t cfg_validate_candidate(const void *candidate_payload, size_t len);

/**
 * @brief Активація випробувального режиму (Trial Run).
 * 
 * Зберігає кандидата у випробувальний буфер оперативної пам'яті, запускає
 * незалежний таймер випробувального терміну (тривалістю trial_timeout_s)
 * та перемикає робочі покажчики підсистем на нові параметри.
 * 
 * @param candidate_payload Буфер перевіреного кандидата.
 * @param len               Розмір буфера.
 * @param trial_timeout_s   Час очікування підтвердження зв'язку в секундах (зазвичай 60 с).
 * @return CFG_OK або CFG_ERR_TRIAL_ACTIVE, якщо попередній Trial ще не завершено.
 */
cfg_status_t cfg_apply_trial(const void *candidate_payload, size_t len, uint32_t trial_timeout_s);

/**
 * @brief Атомарна фіксація випробуваної конфігурації (Commit).
 * 
 * Викликається після успішного мережевого рукостискання (TLS/MQTT Handshake).
 * Атомарно записує кандидата у вільний сектор Flash Ping-Pong із новим номером
 * генерації sequence_number, скидає прапорець Trial та зупиняє захисний таймер.
 * 
 * @return CFG_OK або CFG_ERR_FLASH_WRITE.
 */
cfg_status_t cfg_confirm_commit(void);

/**
 * @brief Аварійний відкат до попередньої стабільної конфігурації (Rollback).
 * 
 * Миттєво відкидає кандидата з RAM, відновлює активний робочий профіль
 * із гарантовано цілісного слота Flash та ініціює перезапуск мережевого стека.
 * 
 * @return CFG_OK.
 */
cfg_status_t cfg_abort_rollback(void);

/**
 * @brief Тип покажчика на функцію покрокової міграції між версіями схеми.
 */
typedef cfg_status_t (*cfg_migrator_fn)(const void *old_payload, size_t old_len,
                                        void *new_payload, size_t new_len);

/**
 * @brief Реєстрація функції міграції між версіями from_ver та to_ver.
 */
cfg_status_t cfg_register_migrator(uint16_t from_ver, uint16_t to_ver, cfg_migrator_fn migrator);
