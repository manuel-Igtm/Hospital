#include "../include/libhl7val.h"
#include <stdio.h>
#include <string.h>
#undef NDEBUG  /* Ensure assert() is active even in release builds */
#include <assert.h>

void test_valid_msh_segment() {
    const char *seg = "MSH|^~\\&|SendingApp|SendingFac|ReceivingApp|ReceivingFac|20231124120000||ADT^A01|MSG00001|P|2.5";
    char error[256];
    int result = hl7val_validate_segment(seg, strlen(seg), error);
    assert(result == HL7VAL_SUCCESS);
    printf("✓ test_valid_msh_segment passed\n");
}

void test_invalid_segment_id() {
    const char *seg = "AB|field1|field2";
    char error[256];
    int result = hl7val_validate_segment(seg, strlen(seg), error);
    assert(result == HL7VAL_ERR_INVALID_FMT);
    printf("✓ test_invalid_segment_id passed\n");
}

void test_too_short() {
    const char *seg = "MSH";
    char error[256];
    int result = hl7val_validate_segment(seg, strlen(seg), error);
    assert(result == HL7VAL_ERR_INVALID_FMT);
    printf("✓ test_too_short passed\n");
}

void test_null_input() {
    char error[256];
    int result = hl7val_validate_segment(NULL, 0, error);
    assert(result == HL7VAL_ERR_NULL_INPUT);
    printf("✓ test_null_input passed\n");
}

void test_field_extraction() {
    const char *seg = "PID|1|12345|JONES^JOHN^Q||19800101|M";
    char output[128];
    
    int result = hl7val_extract_field(seg, 2, output, sizeof(output));
    assert(result == HL7VAL_SUCCESS);
    assert(strcmp(output, "12345") == 0);
    
    result = hl7val_extract_field(seg, 3, output, sizeof(output));
    assert(result == HL7VAL_SUCCESS);
    assert(strcmp(output, "JONES^JOHN^Q") == 0);
    
    printf("✓ test_field_extraction passed\n");
}

int main() {
    printf("Running HL7 validation tests...\n");
    
    test_valid_msh_segment();
    test_invalid_segment_id();
    test_too_short();
    test_null_input();
    test_field_extraction();
    
    printf("\nAll tests passed! ✓\n");
    return 0;
}
