#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_PATH_LEN 256
#define MAX_ERRORS 16
#define MAX_DEFS 8
#define MAX_PROPS 8
#define MAX_REQUIRED 8

typedef enum {
    JSON_TYPE_NULL,
    JSON_TYPE_BOOL,
    JSON_TYPE_INT,
    JSON_TYPE_NUM,
    JSON_TYPE_STR,
    JSON_TYPE_OBJ,
    JSON_TYPE_ARR
} JsonType;

typedef struct JsonValue JsonValue;
typedef struct JsonMember JsonMember;

struct JsonMember {
    char name[32];
    JsonValue *val;
};

struct JsonValue {
    JsonType type;
    union {
        bool bool_val;
        long int_val;
        double num_val;
        char str_val[64];
        struct {
            JsonMember members[MAX_PROPS];
            size_t count;
        } obj;
        struct {
            JsonValue **items;
            size_t count;
        } arr;
    } as;
};

typedef struct SchemaNode SchemaNode;

typedef struct {
    char name[32];
    SchemaNode *schema;
} PropertyRule;

struct SchemaNode {
    bool has_type;
    JsonType expected_type;

    bool has_min;
    double minimum;

    bool has_max;
    double maximum;

    char required[MAX_REQUIRED][32];
    size_t required_count;

    PropertyRule properties[MAX_PROPS];
    size_t properties_count;

    SchemaNode *ref_target;
};

typedef struct {
    char key[32];
    SchemaNode *node;
} DefEntry;

typedef struct {
    DefEntry defs[MAX_DEFS];
    size_t count;
} SymbolTable;

typedef struct {
    char path[MAX_PATH_LEN];
    char message[128];
} ValidationError;

typedef struct {
    ValidationError errors[MAX_ERRORS];
    size_t error_count;
} ValidationContext;

static void record_error(ValidationContext *ctx, const char *path, const char *msg) {
    if (ctx->error_count < MAX_ERRORS) {
        strncpy(ctx->errors[ctx->error_count].path, path[0] ? path : "/", MAX_PATH_LEN - 1);
        strncpy(ctx->errors[ctx->error_count].message, msg, 127);
        ctx->error_count++;
    }
}

static bool validate_node(const SchemaNode *schema, const JsonValue *val, const char *path, ValidationContext *ctx) {
    if (!schema || !val) return false;

    if (schema->ref_target) {
        return validate_node(schema->ref_target, val, path, ctx);
    }

    if (schema->has_type) {
        if (schema->expected_type == JSON_TYPE_NUM) {
            if (val->type != JSON_TYPE_NUM && val->type != JSON_TYPE_INT) {
                record_error(ctx, path, "Expected number");
                return false;
            }
        } else if (val->type != schema->expected_type) {
            record_error(ctx, path, "Type mismatch");
            return false;
        }
    }

    if (val->type == JSON_TYPE_NUM || val->type == JSON_TYPE_INT) {
        double num = (val->type == JSON_TYPE_INT) ? (double)val->as.int_val : val->as.num_val;
        if (schema->has_min && num < schema->minimum) {
            record_error(ctx, path, "Value below minimum");
            return false;
        }
        if (schema->has_max && num > schema->maximum) {
            record_error(ctx, path, "Value exceeds maximum");
            return false;
        }
    }

    if (val->type == JSON_TYPE_OBJ) {
        for (size_t i = 0; i < schema->required_count; i++) {
            bool found = false;
            for (size_t j = 0; j < val->as.obj.count; j++) {
                if (strcmp(schema->required[i], val->as.obj.members[j].name) == 0) {
                    found = true;
                    break;
                }
            }
            if (!found) {
                char subpath[MAX_PATH_LEN];
                snprintf(subpath, sizeof(subpath), "%s/%s", path, schema->required[i]);
                record_error(ctx, subpath, "Required property is missing");
                return false;
            }
        }

        for (size_t j = 0; j < val->as.obj.count; j++) {
            const char *prop_name = val->as.obj.members[j].name;
            const JsonValue *prop_val = val->as.obj.members[j].val;

            for (size_t i = 0; i < schema->properties_count; i++) {
                if (strcmp(schema->properties[i].name, prop_name) == 0) {
                    char subpath[MAX_PATH_LEN];
                    snprintf(subpath, sizeof(subpath), "%s/%s", path, prop_name);
                    if (!validate_node(schema->properties[i].schema, prop_val, subpath, ctx)) {
                        return false;
                    }
                    break;
                }
            }
        }
    }

    return true;
}

int main(void) {
    SchemaNode coord_schema = {
        .has_type = true,
        .expected_type = JSON_TYPE_OBJ,
        .required_count = 2,
        .required = {"lat", "lon"},
        .properties_count = 2,
        .properties = {
            {"lat", &(SchemaNode){ .has_type = true, .expected_type = JSON_TYPE_NUM, .has_min = true, .minimum = -90.0, .has_max = true, .maximum = 90.0 }},
            {"lon", &(SchemaNode){ .has_type = true, .expected_type = JSON_TYPE_NUM, .has_min = true, .minimum = -180.0, .has_max = true, .maximum = 180.0 }}
        }
    };

    SchemaNode root_schema = {
        .has_type = true,
        .expected_type = JSON_TYPE_OBJ,
        .required_count = 3,
        .required = {"userId", "amount", "location"},
        .properties_count = 3,
        .properties = {
            {"userId", &(SchemaNode){ .has_type = true, .expected_type = JSON_TYPE_INT, .has_min = true, .minimum = 1.0 }},
            {"amount", &(SchemaNode){ .has_type = true, .expected_type = JSON_TYPE_NUM, .has_min = true, .minimum = 0.01 }},
            {"location", &(SchemaNode){ .ref_target = &coord_schema }}
        }
    };

    JsonValue lat_val = { .type = JSON_TYPE_NUM, .as.num_val = 50.4501 };
    JsonValue lon_val = { .type = JSON_TYPE_NUM, .as.num_val = 30.5234 };

    JsonValue loc_obj = {
        .type = JSON_TYPE_OBJ,
        .as.obj = {
            .count = 2,
            .members = {
                {"lat", &lat_val},
                {"lon", &lon_val}
            }
        }
    };

    JsonValue user_id = { .type = JSON_TYPE_INT, .as.int_val = 42 };
    JsonValue amount = { .type = JSON_TYPE_NUM, .as.num_val = 199.99 };

    JsonValue valid_doc = {
        .type = JSON_TYPE_OBJ,
        .as.obj = {
            .count = 3,
            .members = {
                {"userId", &user_id},
                {"amount", &amount},
                {"location", &loc_obj}
            }
        }
    };

    ValidationContext ctx = {0};
    bool is_valid = validate_node(&root_schema, &valid_doc, "", &ctx);

    if (is_valid) {
        printf("Validation successful: Document conforms to schema.\n");
    } else {
        printf("Validation failed with %zu errors:\n", ctx.error_count);
        for (size_t i = 0; i < ctx.error_count; i++) {
            printf(" - [%s]: %s\n", ctx.errors[i].path, ctx.errors[i].message);
        }
    }

    return 0;
}
