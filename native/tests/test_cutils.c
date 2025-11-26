#include "../include/libcutils.h"
#include <stdio.h>
#include <string.h>
#include <assert.h>

void test_aes_gcm_encryption() {
    uint8_t key[CUTILS_AES_KEY_SIZE] = {0};
    const char *plaintext = "Hello, Healthcare!";
    uint8_t ciphertext[256];
    uint8_t decrypted[256];
    size_t ct_len = sizeof(ciphertext);
    size_t pt_len = sizeof(decrypted);
    
    /* Generate a key */
    assert(cutils_generate_token(key) == CUTILS_SUCCESS);
    
    /* Encrypt */
    assert(cutils_aes_gcm_encrypt(
        (uint8_t*)plaintext, strlen(plaintext),
        key, ciphertext, &ct_len
    ) == CUTILS_SUCCESS);
    assert(ct_len > strlen(plaintext));
    
    /* Decrypt */
    assert(cutils_aes_gcm_decrypt(
        ciphertext, ct_len,
        key, decrypted, &pt_len
    ) == CUTILS_SUCCESS);
    assert(pt_len == strlen(plaintext));
    assert(memcmp(plaintext, decrypted, pt_len) == 0);
    
    printf("✓ test_aes_gcm_encryption passed\n");
}

void test_sha256() {
    const char *data = "test data";
    uint8_t hash[CUTILS_SHA256_SIZE];
    
    assert(cutils_sha256((uint8_t*)data, strlen(data), hash) == CUTILS_SUCCESS);
    
    /* Hash should be deterministic */
    uint8_t hash2[CUTILS_SHA256_SIZE];
    assert(cutils_sha256((uint8_t*)data, strlen(data), hash2) == CUTILS_SUCCESS);
    assert(memcmp(hash, hash2, CUTILS_SHA256_SIZE) == 0);
    
    printf("✓ test_sha256 passed\n");
}

void test_hex_encoding() {
    uint8_t data[] = {0xDE, 0xAD, 0xBE, 0xEF};
    char hex[32];
    
    assert(cutils_hex_encode(data, sizeof(data), hex) == CUTILS_SUCCESS);
    assert(strcmp(hex, "deadbeef") == 0);
    
    /* Decode back */
    uint8_t decoded[16];
    size_t decoded_len;
    assert(cutils_hex_decode(hex, decoded, &decoded_len) == CUTILS_SUCCESS);
    assert(decoded_len == sizeof(data));
    assert(memcmp(data, decoded, decoded_len) == 0);
    
    printf("✓ test_hex_encoding passed\n");
}

void test_token_generation() {
    uint8_t token1[CUTILS_TOKEN_SIZE];
    uint8_t token2[CUTILS_TOKEN_SIZE];
    
    assert(cutils_generate_token(token1) == CUTILS_SUCCESS);
    assert(cutils_generate_token(token2) == CUTILS_SUCCESS);
    
    /* Tokens should be different (statistically) */
    assert(memcmp(token1, token2, CUTILS_TOKEN_SIZE) != 0);
    
    printf("✓ test_token_generation passed\n");
}

int main() {
    printf("Running crypto utils tests...\n");
    
    test_aes_gcm_encryption();
    test_sha256();
    test_hex_encoding();
    test_token_generation();
    
    printf("\nAll tests passed! ✓\n");
    return 0;
}
