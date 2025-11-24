#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "libcutils.h"

static PyObject* py_aes_gcm_encrypt(PyObject* self, PyObject* args) {
    Py_buffer plaintext_buf, key_buf;
    
    if (!PyArg_ParseTuple(args, "y*y*", &plaintext_buf, &key_buf)) {
        return NULL;
    }
    
    if (key_buf.len != CUTILS_AES_KEY_SIZE) {
        PyBuffer_Release(&plaintext_buf);
        PyBuffer_Release(&key_buf);
        PyErr_SetString(PyExc_ValueError, "Key must be 32 bytes");
        return NULL;
    }
    
    size_t output_len = plaintext_buf.len + CUTILS_AES_IV_SIZE + CUTILS_AES_TAG_SIZE;
    uint8_t *output = PyMem_Malloc(output_len);
    if (!output) {
        PyBuffer_Release(&plaintext_buf);
        PyBuffer_Release(&key_buf);
        return PyErr_NoMemory();
    }
    
    Py_BEGIN_ALLOW_THREADS
    int result = cutils_aes_gcm_encrypt(
        plaintext_buf.buf, plaintext_buf.len,
        key_buf.buf, output, &output_len
    );
    Py_END_ALLOW_THREADS
    
    PyBuffer_Release(&plaintext_buf);
    PyBuffer_Release(&key_buf);
    
    if (result != CUTILS_SUCCESS) {
        PyMem_Free(output);
        PyErr_SetString(PyExc_RuntimeError, cutils_error_string(result));
        return NULL;
    }
    
    PyObject *ret = PyBytes_FromStringAndSize((char*)output, output_len);
    PyMem_Free(output);
    return ret;
}

static PyObject* py_aes_gcm_decrypt(PyObject* self, PyObject* args) {
    Py_buffer ciphertext_buf, key_buf;
    
    if (!PyArg_ParseTuple(args, "y*y*", &ciphertext_buf, &key_buf)) {
        return NULL;
    }
    
    if (key_buf.len != CUTILS_AES_KEY_SIZE) {
        PyBuffer_Release(&ciphertext_buf);
        PyBuffer_Release(&key_buf);
        PyErr_SetString(PyExc_ValueError, "Key must be 32 bytes");
        return NULL;
    }
    
    size_t output_len = ciphertext_buf.len;
    uint8_t *output = PyMem_Malloc(output_len);
    if (!output) {
        PyBuffer_Release(&ciphertext_buf);
        PyBuffer_Release(&key_buf);
        return PyErr_NoMemory();
    }
    
    Py_BEGIN_ALLOW_THREADS
    int result = cutils_aes_gcm_decrypt(
        ciphertext_buf.buf, ciphertext_buf.len,
        key_buf.buf, output, &output_len
    );
    Py_END_ALLOW_THREADS
    
    PyBuffer_Release(&ciphertext_buf);
    PyBuffer_Release(&key_buf);
    
    if (result != CUTILS_SUCCESS) {
        PyMem_Free(output);
        PyErr_SetString(PyExc_RuntimeError, cutils_error_string(result));
        return NULL;
    }
    
    PyObject *ret = PyBytes_FromStringAndSize((char*)output, output_len);
    PyMem_Free(output);
    return ret;
}

static PyObject* py_sha256(PyObject* self, PyObject* args) {
    Py_buffer data_buf;
    
    if (!PyArg_ParseTuple(args, "y*", &data_buf)) {
        return NULL;
    }
    
    uint8_t output[CUTILS_SHA256_SIZE];
    
    Py_BEGIN_ALLOW_THREADS
    int result = cutils_sha256(data_buf.buf, data_buf.len, output);
    Py_END_ALLOW_THREADS
    
    PyBuffer_Release(&data_buf);
    
    if (result != CUTILS_SUCCESS) {
        PyErr_SetString(PyExc_RuntimeError, cutils_error_string(result));
        return NULL;
    }
    
    return PyBytes_FromStringAndSize((char*)output, CUTILS_SHA256_SIZE);
}

static PyObject* py_generate_token(PyObject* self, PyObject* args) {
    uint8_t output[CUTILS_TOKEN_SIZE];
    
    Py_BEGIN_ALLOW_THREADS
    int result = cutils_generate_token(output);
    Py_END_ALLOW_THREADS
    
    if (result != CUTILS_SUCCESS) {
        PyErr_SetString(PyExc_RuntimeError, cutils_error_string(result));
        return NULL;
    }
    
    return PyBytes_FromStringAndSize((char*)output, CUTILS_TOKEN_SIZE);
}

static PyObject* py_hex_encode(PyObject* self, PyObject* args) {
    Py_buffer data_buf;
    
    if (!PyArg_ParseTuple(args, "y*", &data_buf)) {
        return NULL;
    }
    
    char *output = PyMem_Malloc(data_buf.len * 2 + 1);
    if (!output) {
        PyBuffer_Release(&data_buf);
        return PyErr_NoMemory();
    }
    
    int result = cutils_hex_encode(data_buf.buf, data_buf.len, output);
    PyBuffer_Release(&data_buf);
    
    if (result != CUTILS_SUCCESS) {
        PyMem_Free(output);
        PyErr_SetString(PyExc_RuntimeError, cutils_error_string(result));
        return NULL;
    }
    
    PyObject *ret = PyUnicode_FromString(output);
    PyMem_Free(output);
    return ret;
}

static PyMethodDef CutilsMethods[] = {
    {"aes_gcm_encrypt", py_aes_gcm_encrypt, METH_VARARGS, "Encrypt with AES-256-GCM"},
    {"aes_gcm_decrypt", py_aes_gcm_decrypt, METH_VARARGS, "Decrypt with AES-256-GCM"},
    {"sha256", py_sha256, METH_VARARGS, "Compute SHA-256 hash"},
    {"generate_token", py_generate_token, METH_NOARGS, "Generate random token"},
    {"hex_encode", py_hex_encode, METH_VARARGS, "Encode bytes as hex"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef cutilsmodule = {
    PyModuleDef_HEAD_INIT,
    "_cutils",
    "Cryptographic utilities",
    -1,
    CutilsMethods
};

PyMODINIT_FUNC PyInit__cutils(void) {
    return PyModule_Create(&cutilsmodule);
}
