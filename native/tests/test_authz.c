#include "../include/libauthz.h"
#include <stdio.h>
#include <string.h>
#include <assert.h>

void test_context_creation() {
    authz_context_t *ctx = authz_context_create();
    assert(ctx != NULL);
    authz_context_destroy(ctx);
    printf("✓ test_context_creation passed\n");
}

void test_set_attributes() {
    authz_context_t *ctx = authz_context_create();
    assert(ctx != NULL);
    
    authz_attr_t role = {.type = AUTHZ_ATTR_STRING, .str_val = "Doctor"};
    int result = authz_context_set(ctx, "role", role);
    assert(result == AUTHZ_SUCCESS);
    
    authz_attr_t level = {.type = AUTHZ_ATTR_INT, .int_val = 5};
    result = authz_context_set(ctx, "level", level);
    assert(result == AUTHZ_SUCCESS);
    
    authz_context_destroy(ctx);
    printf("✓ test_set_attributes passed\n");
}

void test_policy_evaluation_allow() {
    authz_context_t *ctx = authz_context_create();
    assert(ctx != NULL);
    
    authz_attr_t role = {.type = AUTHZ_ATTR_STRING, .str_val = "Doctor"};
    authz_context_set(ctx, "role", role);
    
    authz_result_t result;
    char error[256];
    int ret = authz_evaluate(ctx, "role == 'Doctor'", &result, error);
    assert(ret == AUTHZ_SUCCESS);
    assert(result == AUTHZ_ALLOW);
    
    authz_context_destroy(ctx);
    printf("✓ test_policy_evaluation_allow passed\n");
}

void test_policy_evaluation_deny() {
    authz_context_t *ctx = authz_context_create();
    assert(ctx != NULL);
    
    authz_attr_t role = {.type = AUTHZ_ATTR_STRING, .str_val = "Nurse"};
    authz_context_set(ctx, "role", role);
    
    authz_result_t result;
    char error[256];
    int ret = authz_evaluate(ctx, "role == 'Doctor'", &result, error);
    assert(ret == AUTHZ_SUCCESS);
    assert(result == AUTHZ_DENY);
    
    authz_context_destroy(ctx);
    printf("✓ test_policy_evaluation_deny passed\n");
}

int main() {
    printf("Running authz tests...\n");
    
    test_context_creation();
    test_set_attributes();
    test_policy_evaluation_allow();
    test_policy_evaluation_deny();
    
    printf("\nAll tests passed! ✓\n");
    return 0;
}
