#pragma once

#include <memory>
#include <string_view>

#include "cJSON.h"

namespace portal::json {

struct DocDeleter {
    void operator()(cJSON *doc) const noexcept { cJSON_Delete(doc); }
};

struct TextDeleter {
    void operator()(char *text) const noexcept { cJSON_free(text); }
};

/* Дерево cJSON під керуванням unique_ptr: жодного ручного cJSON_Delete. */
using Doc = std::unique_ptr<cJSON, DocDeleter>;

/* Рядок, який cJSON виділив у купі під час друку. */
using Text = std::unique_ptr<char, TextDeleter>;

/*
 * Розбір без вимоги завершального нуля: довжину знаємо точно,
 * тож віддаємо її парсеру замість того, щоб псувати вхідний буфер.
 */
[[nodiscard]] inline Doc parse(std::string_view body) noexcept
{
    return Doc{cJSON_ParseWithLength(body.data(), body.size())};
}

[[nodiscard]] inline Text print(const cJSON *doc) noexcept
{
    return Text{cJSON_PrintUnformatted(doc)};
}

/* Значення рядкового поля або порожній вигляд, якщо поля немає. */
[[nodiscard]] inline std::string_view stringField(const cJSON *doc,
                                                  const char *name) noexcept
{
    const cJSON *item = cJSON_GetObjectItemCaseSensitive(doc, name);
    if (!cJSON_IsString(item) || item->valuestring == nullptr) {
        return {};
    }
    return std::string_view{item->valuestring};
}

/* Чи є поле саме рядком — щоб відрізнити «немає» від «не того типу». */
[[nodiscard]] inline bool hasStringField(const cJSON *doc, const char *name) noexcept
{
    return cJSON_IsString(cJSON_GetObjectItemCaseSensitive(doc, name));
}

}  // namespace portal::json
