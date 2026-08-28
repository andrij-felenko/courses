/* c */
#include <stdbool.h>

/**
 * @brief Ініціалізація коефіцієнтів WMM із текстового файлу моделі (WMM.COF)
 * @param model_file_path Шлях до файлу коефіцієнтів
 * @return true у разі успішного завантаження
 */
bool wmm_init(const char* model_file_path);

/**
 * @brief Обчислення векторних елементів поля для заданих координат
 * @param in Вхідні географічні координати й час
 * @param out Вихідні компоненти поля та кути I/D
 * @param sv Вихідна секулярна варіація (може бути NULL)
 * @return 0 при успіху, від'ємний код помилки при збої
 */
int wmm_calculate(
    const wmm_input_t* in,
    wmm_elements_t* out,
    wmm_secular_variation_t* sv
);
