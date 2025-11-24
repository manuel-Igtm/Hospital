#ifndef LIBAUTHZ_H
#define LIBAUTHZ_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file libauthz.h
 * @brief Attribute-Based Access Control (ABAC) policy evaluation
 * 
 * Evaluates compiled ABAC policies expressed as predicates.
 * Example: "role=='Doctor' AND department==encounter.department"
 * 
 * Thread-safe: Yes
 * GIL: Not required during evaluation
 */

/* Error codes */
#define AUTHZ_SUCCESS           0
#define AUTHZ_ERR_NULL_INPUT   -1
#define AUTHZ_ERR_PARSE        -2
#define AUTHZ_ERR_EVAL         -3
#define AUTHZ_ERR_NOT_FOUND    -4

/* Policy result */
typedef enum {
    AUTHZ_DENY = 0,
    AUTHZ_ALLOW = 1
} authz_result_t;

/* Attribute types */
typedef enum {
    AUTHZ_ATTR_STRING,
    AUTHZ_ATTR_INT,
    AUTHZ_ATTR_BOOL
} authz_attr_type_t;

/* Attribute value */
typedef struct {
    authz_attr_type_t type;
    union {
        const char *str_val;
        int int_val;
        bool bool_val;
    };
} authz_attr_t;

/* Context for policy evaluation */
typedef struct authz_context authz_context_t;

/**
 * @brief Create evaluation context
 * 
 * @return New context, or NULL on error
 */
authz_context_t* authz_context_create(void);

/**
 * @brief Destroy evaluation context
 * 
 * @param ctx Context to destroy
 */
void authz_context_destroy(authz_context_t *ctx);

/**
 * @brief Set attribute in context
 * 
 * @param ctx Context
 * @param name Attribute name (e.g., "role", "department")
 * @param value Attribute value
 * @return AUTHZ_SUCCESS on success, negative error code on failure
 */
int authz_context_set(authz_context_t *ctx, const char *name, authz_attr_t value);

/**
 * @brief Evaluate policy expression
 * 
 * Supports:
 * - Equality: role == "Doctor"
 * - Inequality: level > 3
 * - Boolean ops: AND, OR, NOT
 * - Parentheses for grouping
 * 
 * Example: "role == 'Doctor' AND (department == 'Cardiology' OR clearance > 3)"
 * 
 * @param ctx Context with attributes
 * @param policy Policy expression string
 * @param result Output: AUTHZ_ALLOW or AUTHZ_DENY
 * @param error_msg Output buffer for error message (256 bytes), can be NULL
 * @return AUTHZ_SUCCESS on success, negative error code on failure
 */
int authz_evaluate(
    authz_context_t *ctx,
    const char *policy,
    authz_result_t *result,
    char *error_msg
);

/**
 * @brief Get error message for error code
 * 
 * @param error_code Error code from authz functions
 * @return Human-readable error message
 */
const char* authz_error_string(int error_code);

#endif /* LIBAUTHZ_H */
