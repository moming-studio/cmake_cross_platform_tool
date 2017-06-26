#include <cstdlib>
#include <cstring>
#include <string>
#include <list>

#include <config.h>
#include <cmake_config.h>

#if defined(CXX11)
#include <thread>
#endif


//------------------跨平台的打印函数------------------
#if defined(ANDROID)
//android的打印
#define TAG "android tag"
#include <android/log.h>
#define LOG(...) __android_log_print(ANDROID_LOG_ERROR ,TAG, __VA_ARGS__)
#else
//其他平台的打印
#include <stdio.h>
#define LOG(...) {printf(__VA_ARGS__);printf("\n");}
#endif

int main() {
  char platform[8] = {0};
  char abi[8] = {0};
  int isdebug = 0;
#if defined(DEBUG)
  isdebug =1;
#endif
//获取平台和架构信息
#if defined(ANDROID)
  strcpy(platform,"ANDROID");
  strcpy(abi,ANDROID_ABI);
#elif  defined(IOS)
  strcpy(platform,"IOS");
  strcpy(abi,IOS_ABI);
#elif  defined(WIN32)
  strcpy(platform,"WIN32");
  strcpy(abi,WIN32_ABI);
#elif  defined(LINUX)
  strcpy(platform,"LINUX");
  strcpy(abi,LINUX_ABI);
#elif  defined(OSX)
  strcpy(platform,"OSX");
  strcpy(abi,OSX_ABI);
#else
  strcpy(platform,"NONE");
  strcpy(abi,"NONE");
#endif

  //验证c++模板库
  std::list<std::string> l;
  l.push_back("Hello World");

  //验证c++11
#if defined(CXX11)
  std::thread t([]()->int {LOG("in the child thread with c++11"); return 1 + 1; });
  t.join();
#else
  LOG("no c++11(%d) supports",__cplusplus);
#endif

  //打印信息
  LOG("Hello World With %s(%s),V%d.%d.%d.%s,%s(%s)",platform,abi,VERSION_MAJOR,VERSION_MINOR,VERSION_PATCH,VERSION_GIT,isdebug?"Debug":"Release",BUILD_INFO);

  return EXIT_SUCCESS;
}