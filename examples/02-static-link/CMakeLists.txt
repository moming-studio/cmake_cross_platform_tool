cmake_minimum_required(VERSION 2.8.8)
project(02-static-link)

#编译和安装静态库
add_library(foo STATIC "./foo.cpp")
install(TARGETS foo DESTINATION lib)

#使用静态库，编译和安装可执行文件
add_executable(simple "./main.cpp")
target_link_libraries(simple foo)
install(TARGETS simple DESTINATION bin)

#单元测试
enable_testing()
if(IOS)
  add_test(NAME SimpleTest COMMAND "${CMAKE_COMMAND}" -E echo "Skip iOS test")
elseif(ANDROID)
  add_test(NAME SimpleTest COMMAND "${CMAKE_COMMAND}" -E echo "Skip Android test")
else()
  add_test(NAME SimpleTest COMMAND simple)
  set_tests_properties (SimpleTest PROPERTIES PASS_REGULAR_EXPRESSION "Foo")
endif()

include(../show_cmake_info.cmake)#仅仅显示一些cmake的关键信息
