### cmake_cross_platform_tool:使用cmake和python实现跨平台的编译

使用指南：
* 本工具自动cmake程序
* 使用前请先安装python,git，以及需要编译的平台的编译环境
* 运行本文件所在目录下的build_xxx
* windows需要安装vs2013
* android需要安装ndk
* ios和osx需要安装xocde

背景：
* 随着ios和android开发成为非常重要的组成部分，为底层C/C++库提供一个跨平台的编译环境非常有必要
* 为什么选择cmake？下面是比较：
*    1 qmake：可以编译，但是调试不方便
*    2 gyp/gn：位置
*    3 cmake：


特色功能：
* 支持5大平台
* 同时支持直接编译出目标文件和生成ide项目文件
* 

感谢：
* google android cmake项目：https://android.googlesource.com/platform/external/android-cmake
* opencv：参考和使用了opencv相关代码
* polly项目：https://github.com/ruslo/polly

使用方式：
build -h
build --platform=win32 --src_dir=./examples/03-shared-link
build --platform=android --src_dir=./examples/03-shared-link --ndk_path="path to"

TODO list:
ios用lipo合并库，android jni接口不能strip
生成的cmake_config.h 宏不完善# cmake_cross_platform_tool
