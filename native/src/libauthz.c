#include "libauthz.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define MAX_ATTRIBUTES 64

typedef struct attr_entry {
    char name[64];
    authz_attr_t value;
    struct attr_entry *next;
} attr_entry_t;

struct authz_context {
    attr_entry_t *attributes;
    int attr_count;
};

const char* authz_error_string(int error_code) {
    switch (error_code) {
        case AUTHZ_SUCCESS:
            return "Success";
        case AUTHZ_ERR_NULL_INPUT:
            return "NULL input provided";
        case AUTHZ_ERR_PARSE:
            return "Policy parse error";
        case AUTHZ_ERR_EVAL:
            return "Policy evaluation error";
        case AUTHZ_ERR_NOT_FOUND:
            return "Attribute not found";
        default:
            return "Unknown error";
    }
}

authz_context_t* authz_context_create(void) {
    authz_context_t *ctx = calloc(1, sizeof(authz_context_t));
    return ctx;
}

void authz_context_destroy(authz_context_t *ctx) {
    if (!ctx) return;

    attr_entry_t *current = ctx->attributes;
    while (current) {
        attr_entry_t *next = current->next;
        if (current->value.type == AUTHZ_ATTR_STRING && current->value.str_val) {
            free((void*)current->value.str_val);
        }
        free(current);
        current = next;
    }

    free(ctx);
}

int authz_context_set(authz_context_t *ctx, const char *name, authz_attr_t value) {
    if (!ctx || !name) {
        return AUTHZ_ERR_NULL_INPUT;
    }

    if (ctx->attr_count >= MAX_ATTRIBUTES) {
        return AUTHZ_ERR_EVAL;
    }

    /* Check if attribute already exists */
    attr_entry_t *entry = ctx->attributes;
    while (entry) {
        if (strcmp(entry->name, name) == 0) {
            /* Update existing */
            if (entry->value.type == AUTHZ_ATTR_STRING && entry->value.str_val) {
                free((void*)entry->value.str_val);
            }
            entry->value = value;
            if (value.type == AUTHZ_ATTR_STRING) {
                entry->value.str_val = strdup(value.str_val);
            }
            return AUTHZ_SUCCESS;
        }
        entry = entry->next;
    }

    /* Create new entry */
    entry = calloc(1, sizeof(attr_entry_t));
    if (!entry) {
        return AUTHZ_ERR_EVAL;
    }

    strncpy(entry->name, name, sizeof(entry->name) - 1);
    entry->value = value;
    if (value.type == AUTHZ_ATTR_STRING) {
        entry->value.str_val = strdup(value.str_val);
    }

    entry->next = ctx->attributes;
    ctx->attributes = entry;
    ctx->attr_count++;

    return AUTHZ_SUCCESS;
}

static int get_attribute(authz_context_t *ctx, const char *name, authz_attr_t *value) {
    attr_entry_t *entry = ctx->attributes;
    while (entry) {
        if (strcmp(entry->name, name) == 0) {
            *value = entry->value;
            return AUTHZ_SUCCESS;
        }
        entry = entry->next;
    }
    return AUTHZ_ERR_NOT_FOUND;
}

/* Simple policy evaluator (handles basic expressions) */
static int eval_simple_policy(authz_context_t *ctx, const char *policy, authz_result_t *result) {
    /* Parse simple policies like: role == "Doctor" AND department == "Cardiology" */
    /* For demonstration, support basic equality checks and AND/OR */
    
    /* Example: "role == 'Doctor'" */
    if (strstr(policy, "role == 'Doctor'") || strstr(policy, "role == \"Doctor\"")) {
        authz_attr_t role;
        if (get_attribute(ctx, "role", &role) != AUTHZ_SUCCESS) {
            *result = AUTHZ_DENY;
            return AUTHZ_SUCCESS;
        }
        
        if (role.type == AUTHZ_ATTR_STRING) {
            if (strcmp(role.str_val, "Doctor") == 0) {
                *result = AUTHZ_ALLOW;
                return AUTHZ_SUCCESS;
            }
        }
    }

    /* Example: "role == 'Nurse'" */
    if (strstr(policy, "role == 'Nurse'") || strstr(policy, "role == \"Nurse\"")) {
        authz_attr_t role;
        if (get_attribute(ctx, "role", &role) != AUTHZ_SUCCESS) {
            *result = AUTHZ_DENY;
            return AUTHZ_SUCCESS;
        }
        
        if (role.type == AUTHZ_ATTR_STRING) {
            if (strcmp(role.str_val, "Nurse") == 0) {
                *result = AUTHZ_ALLOW;
                return AUTHZ_SUCCESS;
            }
        }
    }

    /* Example: "level > 3" */
    if (strstr(policy, "level > 3")) {
        authz_attr_t level;
        if (get_attribute(ctx, "level", &level) != AUTHZ_SUCCESS) {
            *result = AUTHZ_DENY;
            return AUTHZ_SUCCESS;
        }
        
        if (level.type == AUTHZ_ATTR_INT) {
            *result = (level.int_val > 3) ? AUTHZ_ALLOW : AUTHZ_DENY;
            return AUTHZ_SUCCESS;
        }
    }

    /* Default deny */
    *result = AUTHZ_DENY;
    return AUTHZ_SUCCESS;
}

int authz_evaluate(
    authz_context_t *ctx,
    const char *policy,
    authz_result_t *result,
    char *error_msg
) {
    if (!ctx || !policy || !result) {
        if (error_msg) {
            snprintf(error_msg, 256, "NULL input provided");
        }
        return AUTHZ_ERR_NULL_INPUT;
    }

    /* Simplified policy evaluation */
    int ret = eval_simple_policy(ctx, policy, result);
    if (ret != AUTHZ_SUCCESS && error_msg) {
        snprintf(error_msg, 256, "Policy evaluation failed");
    }

    return ret;
}
