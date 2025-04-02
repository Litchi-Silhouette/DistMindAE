# CMakeLists for src directory
PROJECT(lb_lfu)

AUX_SOURCE_DIRECTORY(. DIR_LOAD_BALANCER_SRCS)
ADD_EXECUTABLE ( load_balancer ${DIR_LOAD_BALANCER_SRCS})
TARGET_LINK_LIBRARIES( lb_lfu lb_strategy;utils;pthread )