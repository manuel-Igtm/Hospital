#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "libhl7val.h"

static PyObject* py_validate_segment(PyObject* self, PyObject* args) {
    const char *segment;
    Py_ssize_t segment_len;
    
    if (!PyArg_ParseTuple(args, "s#", &segment, &segment_len)) {
        return NULL;
    }
    
    char error_msg[256] = {0};
    
    Py_BEGIN_ALLOW_THREADS
    int result = hl7val_validate_segment(segment, segment_len, error_msg);
    Py_END_ALLOW_THREADS
    
    if (result != HL7VAL_SUCCESS) {
        PyErr_SetString(PyExc_ValueError, error_msg[0] ? error_msg : hl7val_error_string(result));
        return NULL;
    }
    
    Py_RETURN_NONE;
}

static PyObject* py_extract_field(PyObject* self, PyObject* args) {
    const char *segment;
    int field_num;
    
    if (!PyArg_ParseTuple(args, "si", &segment, &field_num)) {
        return NULL;
    }
    
    char output[256];
    int result = hl7val_extract_field(segment, field_num, output, sizeof(output));
    
    if (result != HL7VAL_SUCCESS) {
        PyErr_SetString(PyExc_ValueError, hl7val_error_string(result));
        return NULL;
    }
    
    return PyUnicode_FromString(output);
}

static PyMethodDef HL7ValMethods[] = {
    {"validate_segment", py_validate_segment, METH_VARARGS, "Validate HL7 v2 segment"},
    {"extract_field", py_extract_field, METH_VARARGS, "Extract field from HL7 segment"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef hl7valmodule = {
    PyModuleDef_HEAD_INIT,
    "_hl7val",
    "HL7 v2 validation",
    -1,
    HL7ValMethods
};

PyMODINIT_FUNC PyInit__hl7val(void) {
    return PyModule_Create(&hl7valmodule);
}
