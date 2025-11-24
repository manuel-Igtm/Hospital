cmake_minimum_required(VERSION 3.18)
project(hospital_native C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -fstack-protector-strong")
set(CMAKE_C_FLAGS_DEBUG "-g -O0 -DDEBUG")
set(CMAKE_C_FLAGS_RELEASE "-O3 -DNDEBUG -D_FORTIFY_SOURCE=2")

# In CI, treat warnings as errors
if(DEFINED ENV{CI})
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Werror")
endif()

# Find dependencies
find_package(OpenSSL REQUIRED)
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${OPENSSL_INCLUDE_DIR}
    ${Python3_INCLUDE_DIRS}
)

# Source files for C libraries
set(HL7VAL_SOURCES src/libhl7val.c)
set(CUTILS_SOURCES src/libcutils.c)
set(AUTHZ_SOURCES src/libauthz.c)
set(BILL_SOURCES src/libbill.c)

# Build shared libraries
add_library(hl7val SHARED ${HL7VAL_SOURCES})
target_link_libraries(hl7val)

add_library(cutils SHARED ${CUTILS_SOURCES})
target_link_libraries(cutils OpenSSL::Crypto)

add_library(authz SHARED ${AUTHZ_SOURCES})
target_link_libraries(authz)

add_library(bill SHARED ${BILL_SOURCES})
target_link_libraries(bill)

# Install libraries
install(TARGETS hl7val cutils authz bill
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(DIRECTORY include/ DESTINATION include
    FILES_MATCHING PATTERN "*.h"
)

# Enable testing
enable_testing()
add_subdirectory(tests)

# Valgrind support
find_program(VALGRIND_PATH valgrind)
if(VALGRIND_PATH)
    set(MEMORYCHECK_COMMAND ${VALGRIND_PATH})
    set(MEMORYCHECK_COMMAND_OPTIONS "--leak-check=full --error-exitcode=1 --track-origins=yes")
    include(CTest)
endif()

# Code coverage (Debug builds)
if(CMAKE_BUILD_TYPE MATCHES Debug)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} --coverage")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} --coverage")
endif()
