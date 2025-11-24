#ifndef LIBBILL_H
#define LIBBILL_H

#include <stddef.h>

/**
 * @file libbill.h
 * @brief Fast billing calculation engine
 * 
 * Computes total costs from DRG/ICD codes using table-driven configuration.
 * Optimized for high-throughput invoice generation.
 * 
 * Thread-safe: Yes (immutable config tables)
 * GIL: Not required during calculation
 */

/* Error codes */
#define BILL_SUCCESS           0
#define BILL_ERR_NULL_INPUT   -1
#define BILL_ERR_INVALID_CODE -2
#define BILL_ERR_NO_CONFIG    -3
#define BILL_ERR_OVERFLOW     -4

/* Line item */
typedef struct {
    char code[16];          /* ICD/DRG/CPT code */
    char description[128];  /* Service description */
    int quantity;           /* Units */
    long amount_cents;      /* Cost in cents */
} bill_line_item_t;

/* Invoice result */
typedef struct {
    bill_line_item_t *items;
    size_t item_count;
    long subtotal_cents;
    long tax_cents;
    long total_cents;
} bill_invoice_t;

/* Price configuration */
typedef struct bill_config bill_config_t;

/**
 * @brief Load billing configuration from JSON
 * 
 * JSON format:
 * {
 *   "icd_prices": {"I21.0": 150000, ...},
 *   "drg_prices": {"470": 500000, ...},
 *   "cpt_prices": {"99213": 12000, ...},
 *   "tax_rate": 0.0
 * }
 * 
 * Amounts in cents.
 * 
 * @param json_config JSON configuration string
 * @return New config, or NULL on error
 */
bill_config_t* bill_config_load(const char *json_config);

/**
 * @brief Destroy billing configuration
 * 
 * @param config Config to destroy
 */
void bill_config_destroy(bill_config_t *config);

/**
 * @brief Calculate invoice from codes
 * 
 * @param config Billing configuration
 * @param codes Array of ICD/DRG/CPT codes
 * @param code_count Number of codes
 * @param quantities Array of quantities for each code
 * @param invoice Output invoice (caller must free items array)
 * @param error_msg Output buffer for error message (256 bytes), can be NULL
 * @return BILL_SUCCESS on success, negative error code on failure
 */
int bill_calculate(
    bill_config_t *config,
    const char **codes,
    size_t code_count,
    const int *quantities,
    bill_invoice_t *invoice,
    char *error_msg
);

/**
 * @brief Free invoice line items
 * 
 * @param invoice Invoice with items to free
 */
void bill_invoice_free(bill_invoice_t *invoice);

/**
 * @brief Get price for code
 * 
 * @param config Billing configuration
 * @param code ICD/DRG/CPT code
 * @param price_cents Output: price in cents
 * @return BILL_SUCCESS on success, negative error code on failure
 */
int bill_get_price(bill_config_t *config, const char *code, long *price_cents);

/**
 * @brief Get error message for error code
 * 
 * @param error_code Error code from billing functions
 * @return Human-readable error message
 */
const char* bill_error_string(int error_code);

#endif /* LIBBILL_H */
