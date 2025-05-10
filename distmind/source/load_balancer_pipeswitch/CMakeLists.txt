# CMakeLists for src directory
PROJECT(load_balancer_pipeswitch)

AUX_SOURCE_DIRECTORY(. DIR_LOAD_BALANCER_SRCS)
ADD_EXECUTABLE(lb_pipes ${DIR_LOAD_BALANCER_SRCS})
TARGET_LINK_LIBRARIES(lb_pipes utils;pthread)