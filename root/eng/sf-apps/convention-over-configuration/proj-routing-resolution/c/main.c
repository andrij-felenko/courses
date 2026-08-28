#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_CHILDREN 16
#define MAX_PARAMS 8
#define MAX_STR_LEN 64
#define MAX_SEGMENTS 16

typedef enum {
    NODE_STATIC,
    NODE_PARAM
} NodeType;

typedef void (*RouteHandler)(const char* params[][2], size_t param_count);

typedef struct RouteNode {
    char name[MAX_STR_LEN];
    NodeType type;
    RouteHandler handler;
    struct RouteNode* children[MAX_CHILDREN];
    size_t child_count;
} RouteNode;

RouteNode* create_node(const char* name, NodeType type, RouteHandler handler) {
    RouteNode* node = (RouteNode*)calloc(1, sizeof(RouteNode));
    if (!node) return NULL;
    strncpy(node->name, name, MAX_STR_LEN - 1);
    node->type = type;
    node->handler = handler;
    return node;
}

void add_child(RouteNode* parent, RouteNode* child) {
    if (parent && child && parent->child_count < MAX_CHILDREN) {
        parent->children[parent->child_count++] = child;
    }
}

void free_tree(RouteNode* root) {
    if (!root) return;
    for (size_t i = 0; i < root->child_count; ++i) {
        free_tree(root->children[i]);
    }
    free(root);
}

size_t tokenize_path(const char* path, char segments[MAX_SEGMENTS][MAX_STR_LEN]) {
    size_t count = 0;
    const char* p = path;
    while (*p == '/') p++;

    while (*p && count < MAX_SEGMENTS) {
        const char* start = p;
        while (*p && *p != '/') p++;
        size_t len = (size_t)(p - start);
        if (len > 0 && len < MAX_STR_LEN) {
            strncpy(segments[count], start, len);
            segments[count][len] = '\0';
            count++;
        }
        while (*p == '/') p++;
    }
    return count;
}

bool match_recursive(RouteNode* current, char segments[MAX_SEGMENTS][MAX_STR_LEN],
                     size_t seg_idx, size_t total_segs,
                     const char* params[][2], size_t* param_count) {
    if (seg_idx == total_segs) {
        if (current->handler != NULL) {
            current->handler(params, *param_count);
            return true;
        }
        return false;
    }

    const char* current_seg = segments[seg_idx];

    // 1. Пріоритет: точний статичний збіг
    for (size_t i = 0; i < current->child_count; ++i) {
        RouteNode* child = current->children[i];
        if (child->type == NODE_STATIC && strcmp(child->name, current_seg) == 0) {
            if (match_recursive(child, segments, seg_idx + 1, total_segs, params, param_count)) {
                return true;
            }
        }
    }

    // 2. Пріоритет: динамічний параметр [param]
    for (size_t i = 0; i < current->child_count; ++i) {
        RouteNode* child = current->children[i];
        if (child->type == NODE_PARAM) {
            size_t p_idx = *param_count;
            if (p_idx < MAX_PARAMS) {
                params[p_idx][0] = child->name;
                params[p_idx][1] = current_seg;
                *param_count = p_idx + 1;

                if (match_recursive(child, segments, seg_idx + 1, total_segs, params, param_count)) {
                    return true;
                }
                *param_count = p_idx; // Відкат стану у разі глухого кута
            }
        }
    }

    return false;
}

void handle_system_settings(const char* params[][2], size_t count) {
    printf("-> [Handler] Статичний маршрут: Налаштування системи\n");
    (void)params; (void)count;
}

void handle_user_profile(const char* params[][2], size_t count) {
    printf("-> [Handler] Динамічний маршрут: Профіль користувача\n");
    for (size_t i = 0; i < count; ++i) {
        printf("   Параметр [%s] = %s\n", params[i][0], params[i][1]);
    }
}

void handle_user_post(const char* params[][2], size_t count) {
    printf("-> [Handler] Динамічний маршрут: Пост користувача\n");
    for (size_t i = 0; i < count; ++i) {
        printf("   Параметр [%s] = %s\n", params[i][0], params[i][1]);
    }
}

int main(void) {
    RouteNode* root = create_node("", NODE_STATIC, NULL);
    RouteNode* api = create_node("api", NODE_STATIC, NULL);
    RouteNode* users = create_node("users", NODE_STATIC, NULL);
    RouteNode* settings = create_node("settings", NODE_STATIC, handle_system_settings);
    RouteNode* user_id = create_node("userId", NODE_PARAM, NULL);
    RouteNode* profile = create_node("profile", NODE_STATIC, handle_user_profile);
    RouteNode* posts = create_node("posts", NODE_STATIC, NULL);
    RouteNode* post_id = create_node("postId", NODE_PARAM, handle_user_post);

    add_child(root, api);
    add_child(api, users);
    add_child(users, settings);
    add_child(users, user_id);
    add_child(user_id, profile);
    add_child(user_id, posts);
    add_child(posts, post_id);

    const char* test_urls[] = {
        "/api/users/settings",
        "/api/users/1024/profile",
        "/api/users/42/posts/999",
        "/api/users/unknown/invalid/path"
    };

    char segments[MAX_SEGMENTS][MAX_STR_LEN];
    const char* params[MAX_PARAMS][2];

    for (size_t t = 0; t < 4; ++t) {
        printf("=== Запит: %s ===\n", test_urls[t]);
        size_t seg_count = tokenize_path(test_urls[t], segments);
        size_t param_count = 0;

        if (!match_recursive(root, segments, 0, seg_count, params, &param_count)) {
            printf("-> Помилка 404: Відповідного маршруту не знайдено\n");
        }
        printf("\n");
    }

    free_tree(root);
    return 0;
}
