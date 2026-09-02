#include "luks2_json.h"
#include "luks2_hdr.h"

#include <errno.h>
#include <inttypes.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>

#include <json-c/json.h>

#define MAX_AREAS 64

struct area {
    uint64_t offset;
    uint64_t size;
    char     slot[16];
};

struct ctx {
    FILE                     *out;
    struct luks2_json_report *rep;
    uint64_t                  hdr_size;
    uint64_t                  keyslots_size;
    struct area               areas[MAX_AREAS];
    size_t                    narea;
};

static void report(struct ctx *c, int is_error, const char *fmt, ...)
{
    va_list ap;

    fputs(is_error ? "  ✖ " : "  ⚠ ", c->out);
    va_start(ap, fmt);
    vfprintf(c->out, fmt, ap);
    va_end(ap);
    fputc('\n', c->out);

    if (is_error)
        c->rep->errors++;
    else
        c->rep->warnings++;
}

#define ERR(c, ...)  report((c), 1, __VA_ARGS__)
#define WARN(c, ...) report((c), 0, __VA_ARGS__)

static struct json_object *field(struct json_object *o, const char *key)
{
    struct json_object *v = NULL;

    if (o == NULL || !json_object_is_type(o, json_type_object))
        return NULL;
    if (!json_object_object_get_ex(o, key, &v))
        return NULL;
    return v;
}

static struct json_object *typed(struct json_object *o, const char *key,
                                 enum json_type type)
{
    struct json_object *v = field(o, key);

    return (v != NULL && json_object_is_type(v, type)) ? v : NULL;
}

static const char *str_field(struct json_object *o, const char *key)
{
    struct json_object *v = typed(o, key, json_type_string);

    return v ? json_object_get_string(v) : NULL;
}

static int int_field(struct json_object *o, const char *key, int64_t *out)
{
    struct json_object *v = typed(o, key, json_type_int);

    if (v == NULL)
        return 0;
    *out = json_object_get_int64(v);
    return 1;
}

/* Зсуви й розміри LUKS2 тримає рядками — 64 біти не влазять у double JSON. */
static int dec_field(struct json_object *o, const char *key, uint64_t *out)
{
    const char *s = str_field(o, key);
    char *end = NULL;
    unsigned long long v;

    if (s == NULL || *s == '\0')
        return 0;
    errno = 0;
    v = strtoull(s, &end, 10);
    if (errno != 0 || end == s || *end != '\0')
        return 0;
    *out = (uint64_t)v;
    return 1;
}

static int in_list(const char *value, const char *const *list)
{
    size_t i;

    for (i = 0; list[i] != NULL; i++)
        if (strcmp(value, list[i]) == 0)
            return 1;
    return 0;
}

static int dict_has(struct json_object *dict, const char *id)
{
    struct json_object *v = NULL;

    return dict != NULL && json_object_object_get_ex(dict, id, &v);
}

/* Кожен елемент масиву посилань мусить існувати ключем у цільовому словнику. */
static void check_refs(struct ctx *c, struct json_object *from,
                       const char *from_dict, const char *from_id,
                       const char *arr_name,
                       struct json_object *to_dict, const char *to_name)
{
    struct json_object *arr = typed(from, arr_name, json_type_array);
    size_t n, i;

    if (arr == NULL) {
        ERR(c, "%s[\"%s\"]: немає обов'язкового масиву %s", from_dict, from_id, arr_name);
        return;
    }
    n = json_object_array_length(arr);
    if (n == 0)
        WARN(c, "%s[\"%s\"].%s порожній", from_dict, from_id, arr_name);

    for (i = 0; i < n; i++) {
        struct json_object *e = json_object_array_get_idx(arr, i);
        const char *ref;

        if (!json_object_is_type(e, json_type_string)) {
            ERR(c, "%s[\"%s\"].%s[%zu]: посилання мусить бути рядком",
                from_dict, from_id, arr_name, i);
            continue;
        }
        ref = json_object_get_string(e);
        if (!dict_has(to_dict, ref))
            ERR(c, "%s[\"%s\"].%s: висяче посилання на %s[\"%s\"]",
                from_dict, from_id, arr_name, to_name, ref);
    }
}

/* Область смуг не має заходити у службову зону обох заголовків і в чужу область. */
static void add_area(struct ctx *c, const char *slot, uint64_t offset, uint64_t size)
{
    uint64_t meta_end = 2 * c->hdr_size;
    size_t i;

    if (offset % 4096 != 0)
        ERR(c, "keyslots[\"%s\"].area.offset=%" PRIu64 " не вирівняно на 4096", slot, offset);
    if (offset < meta_end)
        ERR(c, "keyslots[\"%s\"].area починається в зоні заголовків [0..%" PRIu64 ")",
            slot, meta_end);

    for (i = 0; i < c->narea; i++)
        if (offset < c->areas[i].offset + c->areas[i].size &&
            c->areas[i].offset < offset + size)
            ERR(c, "області шпарин \"%s\" і \"%s\" перекриваються", slot, c->areas[i].slot);

    if (c->narea < MAX_AREAS) {
        c->areas[c->narea].offset = offset;
        c->areas[c->narea].size = size;
        snprintf(c->areas[c->narea].slot, sizeof(c->areas[c->narea].slot), "%s", slot);
        c->narea++;
    }
}

static void check_kdf(struct ctx *c, const char *id, struct json_object *kdf)
{
    const char *type;
    const char *salt;
    int64_t v;

    if (kdf == NULL) {
        ERR(c, "keyslots[\"%s\"]: немає об'єкта kdf", id);
        return;
    }
    type = str_field(kdf, "type");
    if (type == NULL) {
        ERR(c, "keyslots[\"%s\"].kdf: немає поля type", id);
        return;
    }
    salt = str_field(kdf, "salt");
    if (salt == NULL || strlen(salt) < 22)      /* 16 байтів у base64 — 24 символи */
        ERR(c, "keyslots[\"%s\"].kdf.salt: сіль коротша за 16 байтів", id);

    if (strcmp(type, "argon2id") == 0 || strcmp(type, "argon2i") == 0) {
        if (!int_field(kdf, "time", &v) || v < 1)
            ERR(c, "keyslots[\"%s\"].kdf.time: немає або менше за 1", id);
        if (!int_field(kdf, "memory", &v) || v < 32)
            ERR(c, "keyslots[\"%s\"].kdf.memory: немає або нижче мінімуму Argon2", id);
        else if (v < 65536)
            WARN(c, "keyslots[\"%s\"].kdf.memory=%" PRId64 " КіБ — це слабше за типові 1 ГіБ", id, v);
        if (!int_field(kdf, "cpus", &v) || v < 1)
            ERR(c, "keyslots[\"%s\"].kdf.cpus: немає або менше за 1", id);
    } else if (strcmp(type, "pbkdf2") == 0) {
        if (!int_field(kdf, "iterations", &v) || v < 1000)
            ERR(c, "keyslots[\"%s\"].kdf.iterations: немає або надто мало", id);
        if (str_field(kdf, "hash") == NULL)
            ERR(c, "keyslots[\"%s\"].kdf.hash: немає геш-функції PBKDF2", id);
    } else {
        ERR(c, "keyslots[\"%s\"].kdf.type=\"%s\": формат такого KDF не знає", id, type);
    }
}

static void check_keyslot(struct ctx *c, const char *id, struct json_object *ks,
                          struct json_object *keyslots)
{
    static const char *const modes[] = { "reencrypt", "encrypt", "decrypt", NULL };
    static const char *const dirs[] = { "forward", "backward", NULL };
    static const char *const resil[] = { "journal", "checksum", "none",
                                         "datashift", "datashift-journal",
                                         "datashift-checksum", NULL };
    const char *type = str_field(ks, "type");
    struct json_object *af, *ar;
    int64_t key_size = 0, priority = 0, stripes = 0, area_key = 0, ref = 0;
    uint64_t offset = 0, size = 0;
    const char *s;
    char refid[24];

    if (type == NULL) {
        ERR(c, "keyslots[\"%s\"]: немає поля type", id);
        return;
    }

    if (strcmp(type, "reencrypt") == 0) {
        s = str_field(ks, "mode");
        if (s == NULL || !in_list(s, modes))
            ERR(c, "keyslots[\"%s\"].mode: немає або невідомий режим міграції", id);
        s = str_field(ks, "direction");
        if (s == NULL || !in_list(s, dirs))
            ERR(c, "keyslots[\"%s\"].direction: немає або не forward/backward", id);
        s = str_field(ks, "resilience");
        if (s == NULL || !in_list(s, resil))
            ERR(c, "keyslots[\"%s\"].resilience: немає або невідомий механізм", id);
        if (!int_field(ks, "keyslot", &ref)) {
            ERR(c, "keyslots[\"%s\"].keyslot: немає посилання на слот нового ключа", id);
        } else {
            snprintf(refid, sizeof(refid), "%" PRId64, ref);
            if (!dict_has(keyslots, refid))
                ERR(c, "keyslots[\"%s\"].keyslot=%s: такої шпарини немає", id, refid);
        }
        return;
    }

    if (strcmp(type, "luks2") != 0) {
        WARN(c, "keyslots[\"%s\"].type=\"%s\": невідомий тип шпарини", id, type);
        return;
    }

    if (!int_field(ks, "key_size", &key_size) || key_size <= 0)
        ERR(c, "keyslots[\"%s\"].key_size: немає або не додатне", id);
    if (!int_field(ks, "priority", &priority))
        ERR(c, "keyslots[\"%s\"].priority: немає поля", id);
    else if (priority < 0 || priority > 2)
        WARN(c, "keyslots[\"%s\"].priority=%" PRId64 " поза 0..2", id, priority);

    af = typed(ks, "af", json_type_object);
    if (af == NULL) {
        ERR(c, "keyslots[\"%s\"]: немає об'єкта af", id);
    } else {
        s = str_field(af, "type");
        if (s == NULL || strcmp(s, "luks1") != 0)
            ERR(c, "keyslots[\"%s\"].af.type: стандарт знає лише \"luks1\"", id);
        if (!int_field(af, "stripes", &stripes) || stripes <= 0)
            ERR(c, "keyslots[\"%s\"].af.stripes: немає або не додатне", id);
        if (str_field(af, "hash") == NULL)
            ERR(c, "keyslots[\"%s\"].af.hash: немає геш-функції дифузії", id);
    }

    ar = typed(ks, "area", json_type_object);
    if (ar == NULL) {
        ERR(c, "keyslots[\"%s\"]: немає об'єкта area", id);
        goto kdf;
    }
    s = str_field(ar, "type");
    if (s == NULL || strcmp(s, "raw") != 0)
        ERR(c, "keyslots[\"%s\"].area.type: очікується \"raw\"", id);
    if (str_field(ar, "encryption") == NULL)
        ERR(c, "keyslots[\"%s\"].area.encryption: немає специфікації шифру", id);
    if (!int_field(ar, "key_size", &area_key) || area_key <= 0)
        ERR(c, "keyslots[\"%s\"].area.key_size: немає або не додатне", id);
    if (!dec_field(ar, "offset", &offset) || !dec_field(ar, "size", &size)) {
        ERR(c, "keyslots[\"%s\"].area: offset/size мусять бути десятковими рядками", id);
        goto kdf;
    }
    if (stripes > 0 && key_size > 0 &&
        size < (uint64_t)stripes * (uint64_t)key_size)
        ERR(c, "keyslots[\"%s\"].area.size=%" PRIu64 " менше за stripes·key_size=%" PRIu64,
            id, size, (uint64_t)stripes * (uint64_t)key_size);
    add_area(c, id, offset, size);

kdf:
    check_kdf(c, id, typed(ks, "kdf", json_type_object));
}

static void check_segment(struct ctx *c, const char *id, struct json_object *seg)
{
    static const int sector_sizes[] = { 512, 1024, 2048, 4096 };
    const char *type = str_field(seg, "type");
    struct json_object *integ;
    uint64_t offset = 0, size = 0, meta_end;
    int64_t sector = 0;
    const char *s;
    size_t i;
    int dynamic = 0, ok = 0;

    if (type == NULL) {
        ERR(c, "segments[\"%s\"]: немає поля type", id);
        return;
    }
    if (strcmp(type, "crypt") != 0 && strcmp(type, "linear") != 0) {
        WARN(c, "segments[\"%s\"].type=\"%s\": невідомий тип сегмента", id, type);
        return;
    }
    if (!dec_field(seg, "offset", &offset)) {
        ERR(c, "segments[\"%s\"].offset: немає або не десятковий рядок", id);
        return;
    }
    s = str_field(seg, "size");
    if (s == NULL) {
        ERR(c, "segments[\"%s\"].size: немає поля", id);
    } else if (strcmp(s, "dynamic") == 0) {
        dynamic = 1;
    } else if (!dec_field(seg, "size", &size)) {
        ERR(c, "segments[\"%s\"].size: ні \"dynamic\", ні десятковий рядок", id);
    }

    meta_end = 2 * c->hdr_size;
    if (offset < meta_end)
        ERR(c, "segments[\"%s\"].offset=%" PRIu64 " заходить у зону заголовків", id, offset);
    else if (offset < meta_end + c->keyslots_size)
        WARN(c, "segments[\"%s\"].offset=%" PRIu64 " менший за межу зони шпарин %" PRIu64,
             id, offset, meta_end + c->keyslots_size);

    for (i = 0; i < c->narea; i++)
        if (offset < c->areas[i].offset + c->areas[i].size &&
            (dynamic || size == 0 || c->areas[i].offset < offset + size))
            ERR(c, "segments[\"%s\"] перекриває область шпарини \"%s\"", id, c->areas[i].slot);

    if (strcmp(type, "linear") == 0)
        return;

    if (dec_field(seg, "iv_tweak", &offset) == 0)
        ERR(c, "segments[\"%s\"].iv_tweak: немає або не десятковий рядок", id);
    if (str_field(seg, "encryption") == NULL)
        ERR(c, "segments[\"%s\"].encryption: немає специфікації шифру ядра", id);
    if (!int_field(seg, "sector_size", &sector)) {
        ERR(c, "segments[\"%s\"].sector_size: немає поля", id);
    } else {
        for (i = 0; i < sizeof(sector_sizes) / sizeof(sector_sizes[0]); i++)
            if (sector == sector_sizes[i])
                ok = 1;
        if (!ok)
            ERR(c, "segments[\"%s\"].sector_size=%" PRId64 ": дозволені 512/1024/2048/4096",
                id, sector);
    }

    integ = typed(seg, "integrity", json_type_object);
    if (integ != NULL) {
        if (str_field(integ, "type") == NULL)
            ERR(c, "segments[\"%s\"].integrity.type: немає типу автентифікації", id);
        if (!int_field(integ, "sector_size", &sector))
            WARN(c, "segments[\"%s\"].integrity.sector_size: немає, ядро візьме 512", id);
    }
}

static void check_digest(struct ctx *c, const char *id, struct json_object *dg,
                         struct json_object *keyslots, struct json_object *segments)
{
    const char *type = str_field(dg, "type");
    int64_t v;

    if (type == NULL) {
        ERR(c, "digests[\"%s\"]: немає поля type", id);
        return;
    }
    if (str_field(dg, "salt") == NULL)
        ERR(c, "digests[\"%s\"].salt: немає солі", id);
    if (str_field(dg, "digest") == NULL)
        ERR(c, "digests[\"%s\"].digest: немає контрольного дайджесту", id);
    if (str_field(dg, "hash") == NULL)
        ERR(c, "digests[\"%s\"].hash: немає геш-функції", id);
    if (strcmp(type, "pbkdf2") == 0) {
        if (!int_field(dg, "iterations", &v) || v < 1000)
            ERR(c, "digests[\"%s\"].iterations: немає або надто мало", id);
    } else if (strncmp(type, "argon2", 6) == 0) {
        if (!int_field(dg, "time", &v) || !int_field(dg, "memory", &v) ||
            !int_field(dg, "cpus", &v))
            ERR(c, "digests[\"%s\"]: для Argon2 потрібні time/memory/cpus", id);
    } else {
        WARN(c, "digests[\"%s\"].type=\"%s\": невідомий алгоритм верифікації", id, type);
    }

    check_refs(c, dg, "digests", id, "keyslots", keyslots, "keyslots");
    check_refs(c, dg, "digests", id, "segments", segments, "segments");
}

static void check_config(struct ctx *c, struct json_object *cfg)
{
    static const char *const known_flags[] = {
        "allow-discards", "same-cpu-crypt", "submit-from-crypt-cpus",
        "no-read-workqueue", "no-write-workqueue", "no-journal", NULL
    };
    static const char *const known_reqs[] = {
        "online-reencrypt", "online-reencrypt-v2", "online-reencrypt-v3",
        "offline-reencrypt", "direct-key", "integrity", "unbound-keyslots",
        "opal", "opal-hw-only", NULL
    };
    struct json_object *arr;
    uint64_t json_size = 0;
    size_t n, i;

    if (cfg == NULL) {
        ERR(c, "config: немає словника");
        return;
    }
    if (!dec_field(cfg, "json_size", &json_size))
        ERR(c, "config.json_size: немає або не десятковий рядок");
    else if (json_size != c->hdr_size - LUKS2_HDR_TOTAL_SIZE)
        ERR(c, "config.json_size=%" PRIu64 ", а зона тримає %" PRIu64,
            json_size, c->hdr_size - LUKS2_HDR_TOTAL_SIZE);

    if (!dec_field(cfg, "keyslots_size", &c->keyslots_size))
        ERR(c, "config.keyslots_size: немає або не десятковий рядок");
    else if (c->keyslots_size % 4096 != 0)
        ERR(c, "config.keyslots_size=%" PRIu64 " не кратний 4096", c->keyslots_size);

    arr = typed(cfg, "flags", json_type_array);
    if (arr != NULL) {
        n = json_object_array_length(arr);
        for (i = 0; i < n; i++) {
            struct json_object *e = json_object_array_get_idx(arr, i);
            if (!json_object_is_type(e, json_type_string))
                ERR(c, "config.flags[%zu]: не рядок", i);
            else if (!in_list(json_object_get_string(e), known_flags))
                WARN(c, "config.flags: невідомий прапорець \"%s\"", json_object_get_string(e));
        }
    }

    arr = typed(cfg, "requirements", json_type_array);
    if (arr != NULL) {
        n = json_object_array_length(arr);
        for (i = 0; i < n; i++) {
            struct json_object *e = json_object_array_get_idx(arr, i);
            if (!json_object_is_type(e, json_type_string))
                ERR(c, "config.requirements[%zu]: не рядок", i);
            else if (!in_list(json_object_get_string(e), known_reqs))
                /* саме тут libcryptsetup віддає -EINVAL і не чіпає том */
                ERR(c, "config.requirements: невідома вимога \"%s\" — том буде заблоковано",
                    json_object_get_string(e));
        }
    }
}

/* Шпарина, на яку не посилається жоден дайджест, не дає доступу до даних. */
static void check_unbound(struct ctx *c, struct json_object *keyslots,
                          struct json_object *digests, struct json_object *cfg)
{
    struct json_object *reqs = typed(cfg, "requirements", json_type_array);
    size_t nreq = reqs ? json_object_array_length(reqs) : 0;
    size_t i;
    int allowed = 0;

    for (i = 0; i < nreq; i++) {
        struct json_object *e = json_object_array_get_idx(reqs, i);
        if (json_object_is_type(e, json_type_string) &&
            strcmp(json_object_get_string(e), "unbound-keyslots") == 0)
            allowed = 1;
    }

    json_object_object_foreach(keyslots, ks_id, ks_val) {
        int bound = 0;
        (void)ks_val;

        json_object_object_foreach(digests, dg_id, dg_val) {
            struct json_object *arr = typed(dg_val, "keyslots", json_type_array);
            size_t n = arr ? json_object_array_length(arr) : 0;
            size_t k;
            (void)dg_id;

            for (k = 0; k < n; k++) {
                struct json_object *e = json_object_array_get_idx(arr, k);
                if (json_object_is_type(e, json_type_string) &&
                    strcmp(json_object_get_string(e), ks_id) == 0)
                    bound = 1;
            }
        }
        if (!bound && !allowed) {
            const char *type = str_field(ks_val, "type");
            if (type == NULL || strcmp(type, "reencrypt") != 0)
                WARN(c, "keyslots[\"%s\"] не прив'язана до жодного дайджесту", ks_id);
        }
    }
}

static void print_summary(struct ctx *c, struct json_object *keyslots,
                          struct json_object *tokens, struct json_object *segments,
                          struct json_object *digests)
{
    FILE *o = c->out;

    fputs("\nграф метаданих:\n", o);

    json_object_object_foreach(keyslots, ks_id, ks) {
        struct json_object *kdf = typed(ks, "kdf", json_type_object);
        struct json_object *ar = typed(ks, "area", json_type_object);
        const char *type = str_field(ks, "type");
        const char *kdf_type = kdf ? str_field(kdf, "type") : NULL;

        fprintf(o, "  keyslot %-3s type=%-9s kdf=%-9s area=%s+%s\n",
                ks_id, type ? type : "?", kdf_type ? kdf_type : "-",
                ar ? (str_field(ar, "offset") ? str_field(ar, "offset") : "?") : "-",
                ar ? (str_field(ar, "size") ? str_field(ar, "size") : "?") : "-");
    }
    json_object_object_foreach(tokens, tk_id, tk) {
        const char *type = str_field(tk, "type");
        fprintf(o, "  token   %-3s type=%s\n", tk_id, type ? type : "?");
    }
    json_object_object_foreach(segments, sg_id, sg) {
        const char *type = str_field(sg, "type");
        const char *enc = str_field(sg, "encryption");
        int64_t sector = 0;

        (void)int_field(sg, "sector_size", &sector);
        fprintf(o, "  segment %-3s type=%-7s offset=%s size=%s enc=%s sector=%" PRId64 "\n",
                sg_id, type ? type : "?",
                str_field(sg, "offset") ? str_field(sg, "offset") : "?",
                str_field(sg, "size") ? str_field(sg, "size") : "?",
                enc ? enc : "-", sector);
    }
    json_object_object_foreach(digests, dg_id, dg) {
        const char *type = str_field(dg, "type");
        fprintf(o, "  digest  %-3s type=%s\n", dg_id, type ? type : "?");
    }
    fputs("\nперевірка інваріантів:\n", o);
}

int luks2_json_check(const char *json, size_t len, uint64_t hdr_size,
                     FILE *out, struct luks2_json_report *rep)
{
    struct ctx c;
    struct json_tokener *tok;
    struct json_object *root, *keyslots, *tokens, *segments, *digests, *cfg;
    enum json_tokener_error jerr;

    memset(&c, 0, sizeof(c));
    c.out = out;
    c.rep = rep;
    c.hdr_size = hdr_size;
    rep->errors = 0;
    rep->warnings = 0;

    if (len > (size_t)INT32_MAX) {
        ERR(&c, "документ JSON завеликий для розбору");
        return rep->errors;
    }

    tok = json_tokener_new();
    if (tok == NULL) {
        ERR(&c, "не вдалося створити парсер json-c");
        return rep->errors;
    }
    root = json_tokener_parse_ex(tok, json, (int)len);
    jerr = json_tokener_get_error(tok);
    json_tokener_free(tok);

    if (root == NULL || jerr != json_tokener_success) {
        ERR(&c, "синтаксис JSON: %s", json_tokener_error_desc(jerr));
        json_object_put(root);
        return rep->errors;
    }
    if (!json_object_is_type(root, json_type_object)) {
        ERR(&c, "корінь метаданих мусить бути об'єктом");
        json_object_put(root);
        return rep->errors;
    }

    keyslots = typed(root, "keyslots", json_type_object);
    tokens   = typed(root, "tokens",   json_type_object);
    segments = typed(root, "segments", json_type_object);
    digests  = typed(root, "digests",  json_type_object);
    cfg      = typed(root, "config",   json_type_object);

    if (!keyslots || !tokens || !segments || !digests || !cfg) {
        ERR(&c, "корінь мусить мати словники keyslots, tokens, segments, digests, config");
        json_object_put(root);
        return rep->errors;
    }

    print_summary(&c, keyslots, tokens, segments, digests);

    check_config(&c, cfg);

    json_object_object_foreach(keyslots, ks_id, ks_val)
        check_keyslot(&c, ks_id, ks_val, keyslots);

    json_object_object_foreach(segments, sg_id, sg_val)
        check_segment(&c, sg_id, sg_val);

    json_object_object_foreach(digests, dg_id, dg_val)
        check_digest(&c, dg_id, dg_val, keyslots, segments);

    json_object_object_foreach(tokens, tk_id, tk_val) {
        if (str_field(tk_val, "type") == NULL)
            ERR(&c, "tokens[\"%s\"]: немає поля type", tk_id);
        check_refs(&c, tk_val, "tokens", tk_id, "keyslots", keyslots, "keyslots");
    }

    check_unbound(&c, keyslots, digests, cfg);

    if (rep->errors == 0 && rep->warnings == 0)
        fputs("  усі інваріанти виконано\n", out);

    json_object_put(root);
    return rep->errors;
}
