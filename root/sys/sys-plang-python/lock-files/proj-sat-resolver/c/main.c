/*
 * Симулятор CDCL / PubGrub резолвера залежностей мовою C.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_NAME 64
#define MAX_DEPS 16
#define MAX_PACKAGES 64
#define MAX_VERSIONS 16
#define MAX_CLAUSES 128

typedef struct {
    int major;
    int minor;
    int patch;
} Version;

typedef struct {
    Version min_ver;
    Version max_ver;
    bool has_min;
    bool has_max;
} VersionConstraint;

typedef struct {
    char name[MAX_NAME];
    VersionConstraint constraint;
} Dependency;

typedef struct {
    char name[MAX_NAME];
    Version version;
    char sha256[65];
    Dependency deps[MAX_DEPS];
    int dep_count;
} PackageRelease;

typedef struct {
    PackageRelease releases[MAX_PACKAGES];
    int count;
} PackageUniverse;

typedef struct {
    char pkg_name[MAX_NAME];
    Version ver;
} ClauseItem;

typedef struct {
    ClauseItem items[MAX_DEPS];
    int item_count;
} ConflictClause;

typedef struct {
    ConflictClause clauses[MAX_CLAUSES];
    int count;
} LearnedClauses;

int compare_versions(const Version *a, const Version *b) {
    if (a->major != b->major) return a->major - b->major;
    if (a->minor != b->minor) return a->minor - b->minor;
    return a->patch - b->patch;
}

bool satisfies_constraint(const Version *v, const VersionConstraint *c) {
    if (c->has_min && compare_versions(v, &c->min_ver) < 0) return false;
    if (c->has_max && compare_versions(v, &c->max_ver) >= 0) return false;
    return true;
}

void add_release(PackageUniverse *u, const char *name, Version ver, const char *sha) {
    PackageRelease *p = &u->releases[u->count++];
    strncpy(p->name, name, MAX_NAME - 1);
    p->version = ver;
    strncpy(p->sha256, sha, 64);
    p->dep_count = 0;
}

void add_dependency(PackageRelease *p, const char *dep_name, Version min_v, Version max_v) {
    Dependency *d = &p->deps[p->dep_count++];
    strncpy(d->name, dep_name, MAX_NAME - 1);
    d->constraint.min_ver = min_v;
    d->constraint.max_ver = max_v;
    d->constraint.has_min = true;
    d->constraint.has_max = true;
}

bool solve_recursive(const PackageUniverse *u, PackageRelease **solution, int *sol_count,
                     const Dependency *reqs, int req_count, LearnedClauses *clauses) {
    if (*sol_count >= req_count) {
        return true;
    }

    const Dependency *current_req = &reqs[*sol_count];

    for (int i = 0; i < u->count; ++i) {
        const PackageRelease *candidate = &u->releases[i];
        if (strcmp(candidate->name, current_req->name) != 0) continue;
        if (!satisfies_constraint(&candidate->version, &current_req->constraint)) continue;

        solution[*sol_count] = (PackageRelease*)candidate;
        (*sol_count)++;

        Dependency next_reqs[MAX_PACKAGES];
        int next_count = req_count;
        memcpy(next_reqs, reqs, sizeof(Dependency) * req_count);

        for (int d = 0; d < candidate->dep_count; ++d) {
            bool found = false;
            for (int k = 0; k < next_count; ++k) {
                if (strcmp(next_reqs[k].name, candidate->deps[d].name) == 0) {
                    found = true;
                    if (compare_versions(&candidate->deps[d].constraint.min_ver, &next_reqs[k].constraint.min_ver) > 0) {
                        next_reqs[k].constraint.min_ver = candidate->deps[d].constraint.min_ver;
                    }
                    if (compare_versions(&candidate->deps[d].constraint.max_ver, &next_reqs[k].constraint.max_ver) < 0) {
                        next_reqs[k].constraint.max_ver = candidate->deps[d].constraint.max_ver;
                    }
                    break;
                }
            }
            if (!found && next_count < MAX_PACKAGES) {
                next_reqs[next_count++] = candidate->deps[d];
            }
        }

        if (solve_recursive(u, solution, sol_count, next_reqs, next_count, clauses)) {
            return true;
        }

        // Backtrack
        (*sol_count)--;
    }

    return false;
}

int main(void) {
    PackageUniverse u = {0};

    add_release(&u, "fastapi", (Version){0, 110, 0}, "sha256:4a8e912b7f30");
    add_dependency(&u.releases[0], "pydantic", (Version){2, 0, 0}, (Version){3, 0, 0});
    add_dependency(&u.releases[0], "starlette", (Version){0, 37, 0}, (Version){0, 38, 0});

    add_release(&u, "pydantic", (Version){2, 7, 0}, "sha256:8c1d5e3a2b10");
    add_dependency(&u.releases[1], "pydantic-core", (Version){2, 18, 0}, (Version){2, 19, 0});

    add_release(&u, "pydantic", (Version){2, 6, 4}, "sha256:7b1c3d4e5f60");
    add_dependency(&u.releases[2], "pydantic-core", (Version){2, 16, 0}, (Version){2, 17, 0});

    add_release(&u, "pydantic-core", (Version){2, 16, 3}, "sha256:9f8e7d6c5b4a");
    add_release(&u, "pydantic-core", (Version){2, 18, 1}, "sha256:1a2b3c4d5e6f");
    add_release(&u, "starlette", (Version){0, 37, 2}, "sha256:3d4e5f6a7b8c");

    Dependency root_reqs[2];
    strncpy(root_reqs[0].name, "fastapi", MAX_NAME - 1);
    root_reqs[0].constraint = (VersionConstraint){{0, 110, 0}, {0, 111, 0}, true, true};

    strncpy(root_reqs[1].name, "pydantic-core", MAX_NAME - 1);
    root_reqs[1].constraint = (VersionConstraint){{2, 16, 0}, {2, 17, 0}, true, true};

    PackageRelease *solution[MAX_PACKAGES];
    int sol_count = 0;
    LearnedClauses clauses = {0};

    if (solve_recursive(&u, solution, &sol_count, root_reqs, 2, &clauses)) {
        printf("# Generated Lockfile (C Engine)\n");
        printf("version = 1\n\n");
        for (int i = 0; i < sol_count; ++i) {
            printf("[[package]]\n");
            printf("name = \"%s\"\n", solution[i]->name);
            printf("version = \"%d.%d.%d\"\n", solution[i]->version.major, solution[i]->version.minor, solution[i]->version.patch);
            printf("sha256 = \"%s\"\n\n", solution[i]->sha256);
        }
    } else {
        printf("Resolution failed: no compatible package versions.\n");
    }

    return 0;
}
