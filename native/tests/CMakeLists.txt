# C unit tests (MVP: only cutils and hl7val)
add_executable(test_hl7val test_hl7val.c)
target_link_libraries(test_hl7val hl7val)
add_test(NAME test_hl7val COMMAND test_hl7val)

add_executable(test_cutils test_cutils.c)
target_link_libraries(test_cutils cutils OpenSSL::Crypto)
add_test(NAME test_cutils COMMAND test_cutils)
