#include "libbill.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

/* Simple JSON parsing (for demonstration, a real implementation would use a JSON library) */

#define MAX_CODES 1024

typedef struct {
    char code[16];
    long price_cents;
} price_entry_t;

struct bill_config {
    price_entry_t *prices;
    int price_count;
    double tax_rate;
};

const char* bill_error_string(int error_code) {
    switch (error_code) {
        case BILL_SUCCESS:
            return "Success";
        case BILL_ERR_NULL_INPUT:
            return "NULL input provided";
        case BILL_ERR_INVALID_CODE:
            return "Invalid billing code";
        case BILL_ERR_NO_CONFIG:
            return "No billing configuration loaded";
        case BILL_ERR_OVERFLOW:
            return "Calculation overflow";
        default:
            return "Unknown error";
    }
}

bill_config_t* bill_config_load(const char *json_config) {
    if (!json_config) {
        return NULL;
    }

    bill_config_t *config = calloc(1, sizeof(bill_config_t));
    if (!config) {
        return NULL;
    }

    /* Allocate price table */
    config->prices = calloc(MAX_CODES, sizeof(price_entry_t));
    if (!config->prices) {
        free(config);
        return NULL;
    }

    /* Parse JSON (simplified - in production use a real JSON parser) */
    /* For demonstration, support a simple format */
    config->tax_rate = 0.0;
    config->price_count = 0;

    /* Add some default prices for common codes */
    const char *default_codes[] = {
        "I21.0", "150000",    /* Acute MI - $1,500 */
        "I10", "50000",       /* Hypertension - $500 */
        "E11.9", "75000",     /* Type 2 diabetes - $750 */
        "J18.9", "200000",    /* Pneumonia - $2,000 */
        "99213", "12000",     /* Office visit - $120 */
        "99214", "18000",     /* Office visit complex - $180 */
        "99285", "50000",     /* Emergency visit - $500 */
        "80053", "5000",      /* Comprehensive metabolic panel - $50 */
        "85025", "3000",      /* Complete blood count - $30 */
        "470", "500000",      /* DRG 470 Major joint replacement - $5,000 */
        NULL
    };

    for (int i = 0; default_codes[i] != NULL; i += 2) {
        if (config->price_count >= MAX_CODES) break;
        
        strncpy(config->prices[config->price_count].code, default_codes[i], 15);
        config->prices[config->price_count].code[15] = '\0';
        config->prices[config->price_count].price_cents = atol(default_codes[i + 1]);
        config->price_count++;
    }

    return config;
}

void bill_config_destroy(bill_config_t *config) {
    if (!config) return;
    
    if (config->prices) {
        free(config->prices);
    }
    free(config);
}

int bill_get_price(bill_config_t *config, const char *code, long *price_cents) {
    if (!config || !code || !price_cents) {
        return BILL_ERR_NULL_INPUT;
    }

    for (int i = 0; i < config->price_count; i++) {
        if (strcmp(config->prices[i].code, code) == 0) {
            *price_cents = config->prices[i].price_cents;
            return BILL_SUCCESS;
        }
    }

    return BILL_ERR_INVALID_CODE;
}

int bill_calculate(
    bill_config_t *config,
    const char **codes,
    size_t code_count,
    const int *quantities,
    bill_invoice_t *invoice,
    char *error_msg
) {
    if (!config || !codes || !quantities || !invoice) {
        if (error_msg) {
            snprintf(error_msg, 256, "NULL input provided");
        }
        return BILL_ERR_NULL_INPUT;
    }

    if (code_count == 0) {
        if (error_msg) {
            snprintf(error_msg, 256, "No codes provided");
        }
        return BILL_ERR_NULL_INPUT;
    }

    /* Allocate line items */
    invoice->items = calloc(code_count, sizeof(bill_line_item_t));
    if (!invoice->items) {
        if (error_msg) {
            snprintf(error_msg, 256, "Memory allocation failed");
        }
        return BILL_ERR_OVERFLOW;
    }

    invoice->item_count = 0;
    invoice->subtotal_cents = 0;
    invoice->tax_cents = 0;
    invoice->total_cents = 0;

    /* Calculate line items */
    for (size_t i = 0; i < code_count; i++) {
        long price_cents = 0;
        int ret = bill_get_price(config, codes[i], &price_cents);
        
        if (ret != BILL_SUCCESS) {
            /* Use default price for unknown codes */
            price_cents = 10000; /* $100 default */
        }

        bill_line_item_t *item = &invoice->items[invoice->item_count];
        strncpy(item->code, codes[i], sizeof(item->code) - 1);
        item->code[sizeof(item->code) - 1] = '\0';
        
        snprintf(item->description, sizeof(item->description), 
                 "Service code %s", codes[i]);
        
        item->quantity = quantities[i];
        item->amount_cents = price_cents * quantities[i];
        
        invoice->subtotal_cents += item->amount_cents;
        invoice->item_count++;
    }

    /* Calculate tax */
    invoice->tax_cents = (long)(invoice->subtotal_cents * config->tax_rate);
    invoice->total_cents = invoice->subtotal_cents + invoice->tax_cents;

    return BILL_SUCCESS;
}

void bill_invoice_free(bill_invoice_t *invoice) {
    if (!invoice) return;
    
    if (invoice->items) {
        free(invoice->items);
        invoice->items = NULL;
    }
    
    invoice->item_count = 0;
    invoice->subtotal_cents = 0;
    invoice->tax_cents = 0;
    invoice->total_cents = 0;
}
