cmake_minimum_required(VERSION 2.8.8)

#message(STATUS "----------in generate_config_header_file start--------------")

#include(${CMAKE_CONFIG_FILE_SOURCE_DIR}/show_cmake_info.cmake)#仅仅显示一些cmake的关键信息

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    option(DEBUG "open debug mode" ON)
else()
    option(RELEASE "open debug mode" ON)
endif()

#生成git或svn版本和平台信息
configure_file (
  "${CMAKE_CONFIG_FILE_SOURCE_DIR}/cmake_config.h.in"
  "${CMAKE_CONFIG_FILE_GENERATE_DIR}/cmake_config.h"
 )

