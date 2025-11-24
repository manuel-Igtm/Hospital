#include "libcutils.h"
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <openssl/err.h>
#include <string.h>
#include <stdio.h>

/* Simple XXH3 implementation (simplified for demonstration) */
static uint64_t xxh3_simple(const uint8_t *data, size_t len) {
    uint64_t hash = 0x9E3779B97F4A7C15ULL;
    for (size_t i = 0; i < len; i++) {
        hash ^= data[i];
        hash *= 0x100000001B3ULL;
    }
    return hash;
}

const char* cutils_error_string(int error_code) {
    switch (error_code) {
        case CUTILS_SUCCESS:
            return "Success";
        case CUTILS_ERR_NULL_INPUT:
            return "NULL input provided";
        case CUTILS_ERR_INVALID_SIZE:
            return "Invalid size parameter";
        case CUTILS_ERR_CRYPTO:
            return "Cryptographic operation failed";
        case CUTILS_ERR_BUFFER_SIZE:
            return "Buffer size insufficient";
        default:
            return "Unknown error";
    }
}

int cutils_aes_gcm_encrypt(
    const uint8_t *plaintext,
    size_t plaintext_len,
    const uint8_t *key,
    uint8_t *output,
    size_t *output_len
) {
    if (!plaintext || !key || !output || !output_len) {
        return CUTILS_ERR_NULL_INPUT;
    }

    if (*output_len < plaintext_len + CUTILS_AES_IV_SIZE + CUTILS_AES_TAG_SIZE) {
        return CUTILS_ERR_BUFFER_SIZE;
    }

    EVP_CIPHER_CTX *ctx = NULL;
    int len = 0;
    int ciphertext_len = 0;
    int ret = CUTILS_ERR_CRYPTO;

    /* Generate random IV */
    uint8_t iv[CUTILS_AES_IV_SIZE];
    if (RAND_bytes(iv, CUTILS_AES_IV_SIZE) != 1) {
        goto cleanup;
    }

    /* Copy IV to output */
    memcpy(output, iv, CUTILS_AES_IV_SIZE);

    /* Create and initialize context */
    ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        goto cleanup;
    }

    /* Initialize encryption */
    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) != 1) {
        goto cleanup;
    }

    /* Set IV length */
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, CUTILS_AES_IV_SIZE, NULL) != 1) {
        goto cleanup;
    }

    /* Initialize key and IV */
    if (EVP_EncryptInit_ex(ctx, NULL, NULL, key, iv) != 1) {
        goto cleanup;
    }

    /* Encrypt plaintext */
    if (EVP_EncryptUpdate(ctx, output + CUTILS_AES_IV_SIZE, &len, plaintext, plaintext_len) != 1) {
        goto cleanup;
    }
    ciphertext_len = len;

    /* Finalize encryption */
    if (EVP_EncryptFinal_ex(ctx, output + CUTILS_AES_IV_SIZE + len, &len) != 1) {
        goto cleanup;
    }
    ciphertext_len += len;

    /* Get authentication tag */
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, CUTILS_AES_TAG_SIZE,
                            output + CUTILS_AES_IV_SIZE + ciphertext_len) != 1) {
        goto cleanup;
    }

    *output_len = CUTILS_AES_IV_SIZE + ciphertext_len + CUTILS_AES_TAG_SIZE;
    ret = CUTILS_SUCCESS;

cleanup:
    if (ctx) {
        EVP_CIPHER_CTX_free(ctx);
    }
    return ret;
}

int cutils_aes_gcm_decrypt(
    const uint8_t *ciphertext,
    size_t ciphertext_len,
    const uint8_t *key,
    uint8_t *output,
    size_t *output_len
) {
    if (!ciphertext || !key || !output || !output_len) {
        return CUTILS_ERR_NULL_INPUT;
    }

    if (ciphertext_len < CUTILS_AES_IV_SIZE + CUTILS_AES_TAG_SIZE) {
        return CUTILS_ERR_INVALID_SIZE;
    }

    EVP_CIPHER_CTX *ctx = NULL;
    int len = 0;
    int plaintext_len = 0;
    int ret = CUTILS_ERR_CRYPTO;

    /* Extract IV */
    const uint8_t *iv = ciphertext;
    const uint8_t *ct = ciphertext + CUTILS_AES_IV_SIZE;
    size_t ct_len = ciphertext_len - CUTILS_AES_IV_SIZE - CUTILS_AES_TAG_SIZE;
    const uint8_t *tag = ct + ct_len;

    if (*output_len < ct_len) {
        return CUTILS_ERR_BUFFER_SIZE;
    }

    /* Create and initialize context */
    ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        goto cleanup;
    }

    /* Initialize decryption */
    if (EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) != 1) {
        goto cleanup;
    }

    /* Set IV length */
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, CUTILS_AES_IV_SIZE, NULL) != 1) {
        goto cleanup;
    }

    /* Initialize key and IV */
    if (EVP_DecryptInit_ex(ctx, NULL, NULL, key, iv) != 1) {
        goto cleanup;
    }

    /* Decrypt ciphertext */
    if (EVP_DecryptUpdate(ctx, output, &len, ct, ct_len) != 1) {
        goto cleanup;
    }
    plaintext_len = len;

    /* Set expected tag */
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, CUTILS_AES_TAG_SIZE, (void*)tag) != 1) {
        goto cleanup;
    }

    /* Finalize decryption (verifies tag) */
    if (EVP_DecryptFinal_ex(ctx, output + len, &len) != 1) {
        goto cleanup;
    }
    plaintext_len += len;

    *output_len = plaintext_len;
    ret = CUTILS_SUCCESS;

cleanup:
    if (ctx) {
        EVP_CIPHER_CTX_free(ctx);
    }
    return ret;
}

int cutils_sha256(const uint8_t *data, size_t data_len, uint8_t *output) {
    if (!data || !output) {
        return CUTILS_ERR_NULL_INPUT;
    }

    SHA256_CTX ctx;
    if (SHA256_Init(&ctx) != 1) {
        return CUTILS_ERR_CRYPTO;
    }

    if (SHA256_Update(&ctx, data, data_len) != 1) {
        return CUTILS_ERR_CRYPTO;
    }

    if (SHA256_Final(output, &ctx) != 1) {
        return CUTILS_ERR_CRYPTO;
    }

    return CUTILS_SUCCESS;
}

uint64_t cutils_xxh3(const uint8_t *data, size_t data_len) {
    if (!data) {
        return 0;
    }
    return xxh3_simple(data, data_len);
}

int cutils_generate_token(uint8_t *output) {
    if (!output) {
        return CUTILS_ERR_NULL_INPUT;
    }

    if (RAND_bytes(output, CUTILS_TOKEN_SIZE) != 1) {
        return CUTILS_ERR_CRYPTO;
    }

    return CUTILS_SUCCESS;
}

int cutils_hex_encode(const uint8_t *data, size_t data_len, char *output) {
    if (!data || !output) {
        return CUTILS_ERR_NULL_INPUT;
    }

    const char hex_chars[] = "0123456789abcdef";
    for (size_t i = 0; i < data_len; i++) {
        output[i * 2] = hex_chars[data[i] >> 4];
        output[i * 2 + 1] = hex_chars[data[i] & 0x0F];
    }
    output[data_len * 2] = '\0';

    return CUTILS_SUCCESS;
}

int cutils_hex_decode(const char *hex, uint8_t *output, size_t *output_len) {
    if (!hex || !output || !output_len) {
        return CUTILS_ERR_NULL_INPUT;
    }

    size_t hex_len = strlen(hex);
    if (hex_len % 2 != 0) {
        return CUTILS_ERR_INVALID_SIZE;
    }

    *output_len = hex_len / 2;
    for (size_t i = 0; i < *output_len; i++) {
        char high = hex[i * 2];
        char low = hex[i * 2 + 1];

        uint8_t val = 0;
        if (high >= '0' && high <= '9') val = (high - '0') << 4;
        else if (high >= 'a' && high <= 'f') val = (high - 'a' + 10) << 4;
        else if (high >= 'A' && high <= 'F') val = (high - 'A' + 10) << 4;
        else return CUTILS_ERR_INVALID_SIZE;

        if (low >= '0' && low <= '9') val |= (low - '0');
        else if (low >= 'a' && low <= 'f') val |= (low - 'a' + 10);
        else if (low >= 'A' && low <= 'F') val |= (low - 'A' + 10);
        else return CUTILS_ERR_INVALID_SIZE;

        output[i] = val;
    }

    return CUTILS_SUCCESS;
}
