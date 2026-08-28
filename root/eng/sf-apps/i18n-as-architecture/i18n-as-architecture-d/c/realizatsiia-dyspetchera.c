#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define MAX_I18N_OBSERVERS 16

typedef void (*i18n_change_callback_t)(void *user_data, const char *new_locale);

typedef struct {
    i18n_change_callback_t callback;
    void *user_data;
} i18n_observer_entry_t;

typedef struct {
    const char *current_locale;
    const void *active_catalog;
    const void *active_font;
    i18n_observer_entry_t observers[MAX_I18N_OBSERVERS];
    size_t observer_count;
} i18n_context_manager_t;

static i18n_context_manager_t g_i18n_ctx;

bool i18n_register_observer(i18n_change_callback_t cb, void *user_data) {
    if (!cb || g_i18n_ctx.observer_count >= MAX_I18N_OBSERVERS) return false;
    
    g_i18n_ctx.observers[g_i18n_ctx.observer_count].callback = cb;
    g_i18n_ctx.observers[g_i18n_ctx.observer_count].user_data = user_data;
    g_i18n_ctx.observer_count++;
    return true;
}

void i18n_set_locale(const char *locale_tag, const void *catalog, const void *font) {
    if (!locale_tag) return;
    
    g_i18n_ctx.current_locale = locale_tag;
    g_i18n_ctx.active_catalog = catalog;
    g_i18n_ctx.active_font    = font;
    
    for (size_t i = 0; i < g_i18n_ctx.observer_count; ++i) {
        if (g_i18n_ctx.observers[i].callback) {
            g_i18n_ctx.observers[i].callback(g_i18n_ctx.observers[i].user_data, locale_tag);
        }
    }
}
