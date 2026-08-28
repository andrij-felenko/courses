/* storage_adapter_posix.c — POSIX-реалізація портативного адаптера мовою C */
#include "storage_adapter.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char base_dir[256];
} posix_ctx_t;

static storage_err_t posix_write(storage_adapter_t *self, const char *key, const void *buf, size_t len) {
    if (!self || !self->ctx || !key || !buf) return STORAGE_ERR_INVALID_PARAM;
    posix_ctx_t *ctx = (posix_ctx_t *)self->ctx;

    char path[512];
    snprintf(path, sizeof(path), "%s/%s", ctx->base_dir, key);

    FILE *f = fopen(path, "wb");
    if (!f) return STORAGE_ERR_IO;

    size_t written = fwrite(buf, 1, len, f);
    fflush(f);
    fclose(f);

    return (written == len) ? STORAGE_OK : STORAGE_ERR_IO;
}

static storage_err_t posix_read(storage_adapter_t *self, const char *key, void *buf, size_t max_len, size_t *out_len) {
    if (!self || !self->ctx || !key || !buf || !out_len) return STORAGE_ERR_INVALID_PARAM;
    posix_ctx_t *ctx = (posix_ctx_t *)self->ctx;

    char path[512];
    snprintf(path, sizeof(path), "%s/%s", ctx->base_dir, key);

    FILE *f = fopen(path, "rb");
    if (!f) return STORAGE_ERR_NOT_FOUND;

    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);

    if ((size_t)size > max_len) {
        fclose(f);
        return STORAGE_ERR_IO;
    }

    size_t read_bytes = fread(buf, 1, size, f);
    fclose(f);
    *out_len = read_bytes;

    return STORAGE_OK;
}

static storage_err_t posix_delete(storage_adapter_t *self, const char *key) {
    if (!self || !self->ctx || !key) return STORAGE_ERR_INVALID_PARAM;
    posix_ctx_t *ctx = (posix_ctx_t *)self->ctx;

    char path[512];
    snprintf(path, sizeof(path), "%s/%s", ctx->base_dir, key);

    if (remove(path) == 0) return STORAGE_OK;
    return STORAGE_ERR_NOT_FOUND;
}

static void posix_destroy(storage_adapter_t *self) {
    if (self) {
        if (self->ctx) free(self->ctx);
        free(self);
    }
}

static const struct storage_adapter_ops posix_ops = {
    .write_object = posix_write,
    .read_object = posix_read,
    .delete_object = posix_delete,
    .destroy = posix_destroy
};

storage_adapter_t *storage_adapter_create_posix(const char *base_dir) {
    storage_adapter_t *adapter = (storage_adapter_t *)malloc(sizeof(storage_adapter_t));
    if (!adapter) return NULL;

    posix_ctx_t *ctx = (posix_ctx_t *)malloc(sizeof(posix_ctx_t));
    if (!ctx) {
        free(adapter);
        return NULL;
    }

    strncpy(ctx->base_dir, base_dir, sizeof(ctx->base_dir) - 1);
    ctx->base_dir[sizeof(ctx->base_dir) - 1] = '\0';

    adapter->ops = &posix_ops;
    adapter->ctx = ctx;

    return adapter;
}
