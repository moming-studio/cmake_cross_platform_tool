cmake_minimum_required(VERSION 2.8.8)
project(03-shared-link)

add_library(foo SHARED foo.cpp)
add_library(boo SHARED boo.cpp)

#生成包含导出宏的头文件和动态库的xxx.lib文件，可以不用而直接在代码里面使用__declspec(dllexport)和__declspec(dllimport)
include(GenerateExportHeader)
generate_export_header(foo)
generate_export_header(boo)
include_directories("${CMAKE_CURRENT_BINARY_DIR}") #把生成包含导出宏的头文件目录包含进来

target_link_libraries(boo foo)
install(TARGETS boo DESTINATION lib)
install(TARGETS foo DESTINATION lib)

add_executable(simple "./main.cpp")
target_link_libraries(simple boo)
install(TARGETS simple DESTINATION bin)
install(TARGETS boo DESTINATION bin) #dll还需要安装到bin目录，不然exe无法运行
install(TARGETS foo DESTINATION bin)

#单元测试
enable_testing()
if(IOS)
  add_test(NAME SimpleTest COMMAND "${CMAKE_COMMAND}" -E echo "Skip iOS test")
elseif(ANDROID)
  add_test(NAME SimpleTest COMMAND "${CMAKE_COMMAND}" -E echo "Skip Android test")
else()
  add_test(NAME SimpleTest COMMAND simple)
  set_tests_properties (SimpleTest PROPERTIES PASS_REGULAR_EXPRESSION "Boo say:")
endif()

include(../show_cmake_info.cmake)#仅仅显示一些cmake的关键信息
