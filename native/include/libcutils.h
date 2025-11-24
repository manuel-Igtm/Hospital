#ifndef LIBCUTILS_H
#define LIBCUTILS_H

#include <stddef.h>
#include <stdint.h>

/**
 * @file libcutils.h
 * @brief Cryptographic and utility functions for hospital backend
 * 
 * Provides:
 * - AES-256-GCM encryption/decryption (via OpenSSL)
 * - SHA-256 hashing
 * - XXH3 fast hashing (for non-cryptographic needs)
 * - Random token generation for PII pseudonymization
 * 
 * Thread-safe: Yes (uses thread-local OpenSSL contexts)
 * GIL: Not required during crypto operations
 */

/* Error codes */
#define CUTILS_SUCCESS           0
#define CUTILS_ERR_NULL_INPUT   -1
#define CUTILS_ERR_INVALID_SIZE -2
#define CUTILS_ERR_CRYPTO       -3
#define CUTILS_ERR_BUFFER_SIZE  -4

/* Constants */
#define CUTILS_AES_KEY_SIZE     32  /* AES-256 */
#define CUTILS_AES_IV_SIZE      12  /* GCM recommended IV size */
#define CUTILS_AES_TAG_SIZE     16  /* GCM authentication tag */
#define CUTILS_SHA256_SIZE      32
#define CUTILS_TOKEN_SIZE       32  /* Random token for pseudonymization */

/**
 * @brief Encrypt plaintext using AES-256-GCM
 * 
 * Produces: IV (12 bytes) || ciphertext || tag (16 bytes)
 * 
 * @param plaintext Input plaintext
 * @param plaintext_len Length of plaintext
 * @param key 32-byte encryption key
 * @param output Output buffer (must be >= plaintext_len + 28)
 * @param output_len On input: buffer size, on output: actual encrypted size
 * @return CUTILS_SUCCESS on success, negative error code on failure
 */
int cutils_aes_gcm_encrypt(
    const uint8_t *plaintext,
    size_t plaintext_len,
    const uint8_t *key,
    uint8_t *output,
    size_t *output_len
);

/**
 * @brief Decrypt ciphertext using AES-256-GCM
 * 
 * Expects: IV (12 bytes) || ciphertext || tag (16 bytes)
 * 
 * @param ciphertext Input ciphertext with IV and tag
 * @param ciphertext_len Length of ciphertext (including IV and tag)
 * @param key 32-byte decryption key
 * @param output Output buffer for plaintext (must be >= ciphertext_len - 28)
 * @param output_len On input: buffer size, on output: actual plaintext size
 * @return CUTILS_SUCCESS on success, negative error code on failure
 */
int cutils_aes_gcm_decrypt(
    const uint8_t *ciphertext,
    size_t ciphertext_len,
    const uint8_t *key,
    uint8_t *output,
    size_t *output_len
);

/**
 * @brief Compute SHA-256 hash
 * 
 * @param data Input data
 * @param data_len Length of input
 * @param output Output buffer (must be 32 bytes)
 * @return CUTILS_SUCCESS on success, negative error code on failure
 */
int cutils_sha256(const uint8_t *data, size_t data_len, uint8_t *output);

/**
 * @brief Compute XXH3 64-bit hash (fast, non-cryptographic)
 * 
 * @param data Input data
 * @param data_len Length of input
 * @return 64-bit hash value
 */
uint64_t cutils_xxh3(const uint8_t *data, size_t data_len);

/**
 * @brief Generate cryptographically secure random token
 * 
 * Uses OpenSSL RAND_bytes for CSPRNG
 * 
 * @param output Output buffer (must be 32 bytes)
 * @return CUTILS_SUCCESS on success, negative error code on failure
 */
int cutils_generate_token(uint8_t *output);

/**
 * @brief Encode bytes as hexadecimal string
 * 
 * @param data Input bytes
 * @param data_len Length of input
 * @param output Output buffer (must be >= data_len * 2 + 1)
 * @return CUTILS_SUCCESS on success, negative error code on failure
 */
int cutils_hex_encode(const uint8_t *data, size_t data_len, char *output);

/**
 * @brief Decode hexadecimal string to bytes
 * 
 * @param hex Input hex string
 * @param output Output buffer (must be >= strlen(hex) / 2)
 * @param output_len On output: number of bytes written
 * @return CUTILS_SUCCESS on success, negative error code on failure
 */
int cutils_hex_decode(const char *hex, uint8_t *output, size_t *output_len);

/**
 * @brief Get error message for error code
 * 
 * @param error_code Error code from crypto functions
 * @return Human-readable error message
 */
const char* cutils_error_string(int error_code);

#endif /* LIBCUTILS_H */
