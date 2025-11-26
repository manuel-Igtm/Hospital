#include "libhl7val.h"
#include <string.h>
#include <ctype.h>
#include <stdio.h>

const char* hl7val_error_string(int error_code) {
    switch (error_code) {
        case HL7VAL_SUCCESS:
            return "Success";
        case HL7VAL_ERR_NULL_INPUT:
            return "NULL input provided";
        case HL7VAL_ERR_TOO_LARGE:
            return "Segment exceeds maximum size";
        case HL7VAL_ERR_INVALID_FMT:
            return "Invalid HL7 segment format";
        case HL7VAL_ERR_FIELD_COUNT:
            return "Invalid field count for segment type";
        case HL7VAL_ERR_DATATYPE:
            return "Invalid datatype in field";
        default:
            return "Unknown error";
    }
}

int hl7val_validate_segment(const char *segment, size_t segment_len, char *error_msg) {
    /* Input validation */
    if (!segment) {
        if (error_msg) {
            snprintf(error_msg, 256, "Segment is NULL");
        }
        return HL7VAL_ERR_NULL_INPUT;
    }

    /* Size check */
    if (segment_len > HL7VAL_MAX_SEGMENT_SIZE) {
        if (error_msg) {
            snprintf(error_msg, 256, "Segment length %zu exceeds maximum %d",
                     segment_len, HL7VAL_MAX_SEGMENT_SIZE);
        }
        return HL7VAL_ERR_TOO_LARGE;
    }

    /* Minimum length check (segment ID + delimiter + at least one field) */
    if (segment_len < 5) {
        if (error_msg) {
            snprintf(error_msg, 256, "Segment too short (minimum 5 characters)");
        }
        return HL7VAL_ERR_INVALID_FMT;
    }

    /* Validate segment ID (3 uppercase alphanumeric characters) */
    for (int i = 0; i < 3; i++) {
        if (!isupper(segment[i]) && !isdigit(segment[i])) {
            if (error_msg) {
                snprintf(error_msg, 256, "Invalid segment ID at position %d", i);
            }
            return HL7VAL_ERR_INVALID_FMT;
        }
    }

    /* Check for field delimiter */
    char delimiter = segment[3];
    if (delimiter != '|') {
        if (error_msg) {
            snprintf(error_msg, 256, "Invalid field delimiter (expected '|', got '%c')", delimiter);
        }
        return HL7VAL_ERR_INVALID_FMT;
    }

    /* Count fields */
    int field_count = 1;
    for (size_t i = 3; i < segment_len; i++) {
        if (segment[i] == delimiter) {
            field_count++;
        }
    }

    /* For MSH segment, the field separator itself is MSH-1, so add 1 */
    char seg_type[4] = {segment[0], segment[1], segment[2], '\0'};
    if (strcmp(seg_type, "MSH") == 0) {
        field_count++;  /* MSH-1 is the field separator character */
    }
    
    /* Basic field count validation for common segments */
    int min_fields = 0;
    if (strcmp(seg_type, "MSH") == 0) {
        min_fields = 12;  /* MSH requires at least 12 fields */
    } else if (strcmp(seg_type, "PID") == 0) {
        min_fields = 5;   /* PID requires at least 5 fields */
    } else if (strcmp(seg_type, "OBR") == 0) {
        min_fields = 4;   /* OBR requires at least 4 fields */
    } else if (strcmp(seg_type, "OBX") == 0) {
        min_fields = 5;   /* OBX requires at least 5 fields */
    } else {
        min_fields = 1;   /* Generic segments need at least 1 field */
    }

    if (field_count < min_fields) {
        if (error_msg) {
            snprintf(error_msg, 256, "Segment %s has %d fields, requires at least %d",
                     seg_type, field_count, min_fields);
        }
        return HL7VAL_ERR_FIELD_COUNT;
    }

    if (field_count > HL7VAL_MAX_FIELDS) {
        if (error_msg) {
            snprintf(error_msg, 256, "Segment has %d fields, exceeds maximum %d",
                     field_count, HL7VAL_MAX_FIELDS);
        }
        return HL7VAL_ERR_FIELD_COUNT;
    }

    return HL7VAL_SUCCESS;
}

int hl7val_extract_field(const char *segment, int field_num, char *output, size_t output_size) {
    if (!segment || !output) {
        return HL7VAL_ERR_NULL_INPUT;
    }

    if (field_num < 1) {
        return HL7VAL_ERR_INVALID_FMT;
    }

    /* Skip segment ID and delimiter */
    const char *ptr = segment + 4;
    int current_field = 1;
    const char *field_start = ptr;

    /* Find the requested field */
    while (*ptr != '\0' && current_field < field_num) {
        if (*ptr == '|') {
            current_field++;
            field_start = ptr + 1;
        }
        ptr++;
    }

    if (current_field != field_num) {
        return HL7VAL_ERR_FIELD_COUNT;
    }

    /* Find end of field */
    const char *field_end = field_start;
    while (*field_end != '\0' && *field_end != '|') {
        field_end++;
    }

    /* Copy field value */
    size_t field_len = field_end - field_start;
    if (field_len >= output_size) {
        return HL7VAL_ERR_TOO_LARGE;
    }

    memcpy(output, field_start, field_len);
    output[field_len] = '\0';

    return HL7VAL_SUCCESS;
}
