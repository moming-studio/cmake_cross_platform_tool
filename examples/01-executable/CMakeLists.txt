cmake_minimum_required(VERSION 2.8.8)
project(01-executable)

#------------配置信息------------
#版本号管理
set (VERSION_MAJOR 1)
set (VERSION_MINOR 0)
set (VERSION_PATCH 0)
#添加c++11
include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
if(COMPILER_SUPPORTS_CXX11)
    add_definitions("-std=c++11 -pthread")
    option(CXX11 "using c++11" ON)
endif()

#win32默认设置支持，从vs2013开始支持
if(WIN32)
    option(CXX11 "using c++11" ON)
endif()

#生成版本信息
configure_file (
  "${PROJECT_SOURCE_DIR}/config.h.in"
  "${PROJECT_BINARY_DIR}/config.h"
 )
include_directories ("${PROJECT_SOURCE_DIR}")
include_directories ("${PROJECT_BINARY_DIR}")

#------------编译器设置------------
#release也生成pdb
if(WIN32)
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /Zi")
    set(CMAKE_SHARED_LINKER_FLAGS_RELEASE "${CMAKE_SHARED_LINKER_FLAGS_RELEASE} /DEBUG /OPT:REF /OPT:ICF")
    set(CMAKE_EXE_LINKER_FLAGS_RELEASE "${CMAKE_EXE_LINKER_FLAGS_RELEASE} /DEBUG /OPT:REF /OPT:ICF")
endif()

#------------目标设置------------
SET(SRC_LIST "./main.cpp")
if(WIN32)
    SET(SRC_LIST ${SRC_LIST} "./version.rc")
endif()

if(IOS)
    SET(CMAKE_EXECUTABLE_SUFFIX .app)
endif()
#由main.cpp生成可执行文件simple
add_executable(simple ${SRC_LIST})
if(ANDROID)
    target_link_libraries(simple log)
elseif(LINUX)
    target_link_libraries(simple -pthread)
endif()

#------------安装设置------------
#安装可执行文件simple到安装目录的bin子目录
install(TARGETS simple DESTINATION bin)
if(WIN32)
    install(FILES "${PROJECT_BINARY_DIR}/${CMAKE_BUILD_TYPE}/simple.pdb" DESTINATION bin)
endif()

#------------单元设置------------
#单元测试
enable_testing()
if(IOS)
  add_test(NAME SimpleTest COMMAND "${CMAKE_COMMAND}" -E echo "Skip iOS test")
elseif(ANDROID)
  add_test(NAME SimpleTest COMMAND "${CMAKE_COMMAND}" -E echo "Skip Android test")
else()
  add_test(NAME SimpleTest COMMAND simple)
  set_tests_properties (SimpleTest PROPERTIES PASS_REGULAR_EXPRESSION "${PLATFORM}")
endif()
#------------打包设置------------
#TODO
#include(../show_cmake_info.cmake)#仅仅显示一些cmake的关键信息
