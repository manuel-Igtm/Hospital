#ifndef LIBHL7VAL_H
#define LIBHL7VAL_H

#include <stddef.h>

/**
 * @file libhl7val.h
 * @brief HL7 v2 message validation library
 * 
 * Validates HL7 v2 segments for basic structural correctness:
 * - Length constraints
 * - Field count validation
 * - Basic datatype checks
 * 
 * Thread-safe: Yes
 * GIL: Not required during validation
 */

/* Error codes */
#define HL7VAL_SUCCESS           0
#define HL7VAL_ERR_NULL_INPUT   -1
#define HL7VAL_ERR_TOO_LARGE    -2
#define HL7VAL_ERR_INVALID_FMT  -3
#define HL7VAL_ERR_FIELD_COUNT  -4
#define HL7VAL_ERR_DATATYPE     -5

/* Constants */
#define HL7VAL_MAX_SEGMENT_SIZE 65536
#define HL7VAL_MAX_FIELDS       256

/**
 * @brief Validate an HL7 v2 segment
 * 
 * Checks:
 * - Segment is non-null and within size limits
 * - Starts with valid 3-character segment ID
 * - Has proper field delimiter structure
 * - Field count matches expectations for segment type
 * 
 * @param segment Null-terminated HL7 segment string (e.g., "MSH|^~\\&|...")
 * @param segment_len Length of segment (for bounds checking)
 * @param error_msg Output buffer for error message (min 256 bytes), can be NULL
 * @return HL7VAL_SUCCESS on success, negative error code on failure
 */
int hl7val_validate_segment(const char *segment, size_t segment_len, char *error_msg);

/**
 * @brief Extract field from HL7 segment
 * 
 * @param segment Null-terminated HL7 segment
 * @param field_num Field number (1-based)
 * @param output Output buffer for field value
 * @param output_size Size of output buffer
 * @return HL7VAL_SUCCESS on success, negative error code on failure
 */
int hl7val_extract_field(const char *segment, int field_num, char *output, size_t output_size);

/**
 * @brief Get error message for error code
 * 
 * @param error_code Error code from validation functions
 * @return Human-readable error message
 */
const char* hl7val_error_string(int error_code);

#endif /* LIBHL7VAL_H */
