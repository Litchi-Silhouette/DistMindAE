PROJECT(storage_client)

if(NOT TARGET spdlog)
    # Stand-alone build
    find_package(spdlog REQUIRED)
endif()

# AUX_SOURCE_DIRECTORY(. DIR_STORAGE_CLIENT_SRCS)
ADD_EXECUTABLE ( storage_client store_cli.cpp)
ADD_EXECUTABLE ( storage_stress_test stress_test.cpp cli_common.hpp)
TARGET_LINK_LIBRARIES( storage_client utils )
TARGET_LINK_LIBRARIES(storage_stress_test PRIVATE spdlog utils)

