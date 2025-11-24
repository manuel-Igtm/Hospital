#include "../include/libbill.h"
#include <stdio.h>
#include <string.h>
#include <assert.h>

void test_config_load() {
    const char *json = "{\"tax_rate\": 0.0}";
    bill_config_t *config = bill_config_load(json);
    assert(config != NULL);
    bill_config_destroy(config);
    printf("✓ test_config_load passed\n");
}

void test_get_price() {
    bill_config_t *config = bill_config_load("{}");
    assert(config != NULL);
    
    long price;
    int result = bill_get_price(config, "99213", &price);
    assert(result == BILL_SUCCESS);
    assert(price == 12000); /* $120 */
    
    bill_config_destroy(config);
    printf("✓ test_get_price passed\n");
}

void test_calculate_invoice() {
    bill_config_t *config = bill_config_load("{}");
    assert(config != NULL);
    
    const char *codes[] = {"99213", "80053"};
    int quantities[] = {1, 1};
    bill_invoice_t invoice = {0};
    char error[256];
    
    int result = bill_calculate(config, codes, 2, quantities, &invoice, error);
    assert(result == BILL_SUCCESS);
    assert(invoice.item_count == 2);
    assert(invoice.subtotal_cents == 17000); /* $120 + $50 = $170 */
    assert(invoice.total_cents == 17000);     /* No tax */
    
    bill_invoice_free(&invoice);
    bill_config_destroy(config);
    printf("✓ test_calculate_invoice passed\n");
}

void test_multiple_quantities() {
    bill_config_t *config = bill_config_load("{}");
    assert(config != NULL);
    
    const char *codes[] = {"99213"};
    int quantities[] = {3};
    bill_invoice_t invoice = {0};
    char error[256];
    
    int result = bill_calculate(config, codes, 1, quantities, &invoice, error);
    assert(result == BILL_SUCCESS);
    assert(invoice.item_count == 1);
    assert(invoice.subtotal_cents == 36000); /* $120 * 3 = $360 */
    
    bill_invoice_free(&invoice);
    bill_config_destroy(config);
    printf("✓ test_multiple_quantities passed\n");
}

int main() {
    printf("Running billing tests...\n");
    
    test_config_load();
    test_get_price();
    test_calculate_invoice();
    test_multiple_quantities();
    
    printf("\nAll tests passed! ✓\n");
    return 0;
}
