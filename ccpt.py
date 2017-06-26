#!/usr/bin/env python3
# coding:utf8

from __future__ import print_function
import glob, re,subprocess, os, os.path, shutil,  sys, argparse,time,getpass,socket
import logging as log
from subprocess import check_call, check_output, CalledProcessError

#===========================================公共定义===========================================
class Fail(Exception):
    def __init__(self, text=None):
        self.t = text
    def __str__(self):
        return "ERROR" if self.t is None else self.t

def execCmdReturn(cmd):
    print(cmd)
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text

def execute(cmd, cwd=None):
    print("Executing: %s in %s" % (cmd, cwd),file=sys.stderr)
    print("-------------------")
    for one in cmd:
        print(one),
    print("-------------------")
    retcode = check_call(cmd, cwd = cwd)
    if retcode != 0:
        raise Exception("Child returned:", retcode)

def rm_one(d):
    d = os.path.abspath(d)
    if os.path.exists(d):
        if os.path.isdir(d):
            log.info("Removing dir: %s", d)
            shutil.rmtree(d)
        elif os.path.isfile(d):
            log.info("Removing file: %s", d)
            os.remove(d)

def check_dir(d, create=False, clean=False):
    d = os.path.abspath(d)
    log.info("Check dir %s (create: %s, clean: %s)", d, create, clean)
    if os.path.exists(d):
        if not os.path.isdir(d):
            raise Fail("Not a directory: %s" % d)
        if clean:
            for x in glob.glob(os.path.join(d, "*")):
                rm_one(x)
    else:
        if create:
            os.makedirs(d)
    return d

#======================================================================================
class ABI:
    def __init__(self, platform, arch, target=None):
        self.platform = platform
        self.arch = arch
        self.target = target if target is not None else platform
    def __str__(self):
        return "%s-%s-%s" % (self.platform, self.arch,self.platform if self.target is None else self.target)

class Builder:
    def __init__(self, platform,srcdir, outdir, buildtype,abi,cmakeargs):
        self.platform=platform
        #编译日期
        self.builddate = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()));
        #编译机器信息
        self.buildinfo = "{} build on {}({}-{}) at {}".format(getpass.getuser(), socket.gethostname(), sys.platform,os.name, self.builddate)
        #编译目录
        build_ddir = os.path.join(outdir,
                                      ".build/" + platform + "-" + buildtype.lower() +"-"+ abi.arch)
        #输出目录
        out_dir = os.path.join(outdir, "build-" + buildtype.lower()+"/"+platform)
        self.srcdir = check_dir(srcdir)
        self.builddir = check_dir(build_ddir, create=True,clean=True)#TODO 不用clean
        self.outdir = check_dir(out_dir)
        self.buildypte = buildtype
        self.abi = abi
        self.cmakeargs = cmakeargs

    def get_cmake_dir(self):
        if sys.platform == "win32":
            return os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),
                                "tools/cmake-3.6.3155560-windows-x86_64/bin/")
        elif sys.platform == "linux2":
            return os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),
                                "tools/cmake-3.6.3155560-linux-x86_64/bin/")
        elif sys.platform == 'darwin':
            return os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),
                                "tools/cmake-3.6.3155560-darwin-x86_64/bin/")

    def get_cmake_exe(self):
        if sys.platform == "win32":
            return self.get_cmake_dir()+"/cmake.exe";
        elif sys.platform == "linux2" or sys.platform == 'darwin':
            return self.get_cmake_dir()+"/cmake";

    def get_ninja_exe(self):
        if sys.platform == "win32":
            return self.get_cmake_dir()+"/ninja.exe";
        elif sys.platform == "linux2" or sys.platform == 'darwin':
            return self.get_cmake_dir()+"/ninja";

    def get_ctest_exe(self):
        if sys.platform == "win32":
            return self.get_cmake_dir()+"/ctest.exe";
        elif sys.platform == "linux2" or sys.platform == 'darwin':
            return self.get_cmake_dir()+"/ctest";

    def get_generate_header_path(self):
        return os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),
                            "platforms/common")

    def clean_library_build_dir(self):
        for d in ["CMakeCache.txt", "CMakeFiles/", "bin/", "libs/", "lib/", "package/", "install/samples/"]:
            rm_one(d)

    def get_git_version(self):
        path_old = os.getcwd()
        os.chdir(self.srcdir)
        self.git_version = execCmdReturn("git log -1 --pretty=format:\"git-%cd-%h\" --date=short")
        os.chdir(path_old)

    #子类可能需要重载
    def get_toolchain_file(self):
        return None

    # 子类可能需要重载
    def get_cmake_generator(self):
        return "-GVisual Studio 12 2013%s" % (" Win64"if self.abi.arch=="x64" else "")

    def platform_cmake_args(self):
        return None;

    def do_generate_header(self,cmd):
        cmd_generate_header=cmd[:]
        cmd_generate_header.append("-DCMAKE_CONFIG_FILE_SOURCE_DIR=%s" % self.get_generate_header_path());
        cmd_generate_header.append("-DCMAKE_CONFIG_FILE_GENERATE_DIR=%s" % self.builddir);
        cmd_generate_header.append("-P");
        cmd_generate_header.append(os.path.join(self.get_generate_header_path(),"generate_config_header_file.cmake"));
        # 用cmake生成配置头文件
        execute(cmd_generate_header)

    def do_cmake(self,cmd):
        execute(cmd)

    def do_build(self):
        execute([
            self.get_cmake_exe(),
            "--build",
            self.builddir,
            "--target",
            "ALL_BUILD",
            "--config",
            self.buildypte
        ])

    def do_install(self):

        execute([self.get_cmake_exe(),
                 "-DBUILD_BYPT=%s" % self.buildypte,
                 "-DCMAKE_INSTALL_CONFIG_NAME=%s" % self.buildypte,
                  "-P",
                  os.path.join(self.builddir+"/cmake_install.cmake")
                 ])

    def do_test(self):
        execute([self.get_ctest_exe(), "-C", self.buildypte], cwd=self.builddir)

    def do_pack(self):
        #TODO 打包
        pass

    def build_library(self):
        self.get_git_version()
        cmd = [
            self.get_cmake_exe(),
            "-H%s" % self.srcdir,
            "-B%s" % self.builddir,
            self.get_cmake_generator(),
            "-DCMAKE_INSTALL_PREFIX=%s" % os.path.join(self.outdir,self.abi.arch),
            "-DCMAKE_BUILD_TYPE=%s" % self.buildypte,
            "-DPLATFORM=%s" % self.platform.upper(),
            "-D%s=ON" % self.platform.upper(),
            "-D{}_ABI={}".format(self.platform.upper(),self.abi.arch),
            "-DBUILD_INFO=%s" % self.buildinfo,
            "-DVERSION_GIT=%s" % self.git_version
        ]
        toolchain_file=self.get_toolchain_file()
        if toolchain_file is not None:
            cmd.append("-DCMAKE_TOOLCHAIN_FILE=%s" % toolchain_file)

        platform_cmake_args = self.platform_cmake_args()
        if platform_cmake_args is not None:
            for arg in  platform_cmake_args:
                cmd.append(arg)

        if self.cmakeargs is not None:
            cmd.append(self.cmakeargs)
        self.do_generate_header(cmd)
        self.do_cmake(cmd)
        self.do_build()
        self.do_install()
        self.do_test()
        self.do_pack()

class Win32Builer(Builder):
    pass
class LinuxBuiler(Builder):
    def get_cmake_generator(self):
        return "-GAndroid Gradle - Ninja";

    def do_build(self):
        execute([
            self.get_cmake_exe(),
            "--build",
            self.builddir,
            "--target",
            "all",
            "--config",
            self.buildypte
        ])

    def platform_cmake_args(self):
        return ["-DCMAKE_C_FLAGS=%s" % ("-m32" if self.abi == "x86" else "-m64"),
                "-DCMAKE_CXX_FLAGS=%s" % ("-m32" if self.abi == "x86" else "-m64")];

class AndroidBuiler(LinuxBuiler):
    def get_toolchain_file(self):
        return os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),"platforms/android/android.toolchain.cmake")

    def platform_cmake_args(self):
        return ["-DANDROID_ABI=%s" % self.abi.arch,
                "-DANDROID_STL=gnustl_static",
                "-DCMAKE_MAKE_PROGRAM=%s" % self.get_ninja_exe(),
                "-DANDROID_NATIVE_API_LEVEL=9"];

    def do_install(self):
        cmd=[self.get_cmake_exe(),
         "-DBUILD_BYPT=%s" % self.buildypte,
         "-DCMAKE_INSTALL_CONFIG_NAME=%s" % self.buildypte,
         ]
        if self.buildypte == "Release":
            cmd.append("-DCMAKE_INSTALL_DO_STRIP=ON")
        cmd.append("-P")
        cmd.append(os.path.join(self.builddir + "/cmake_install.cmake"))
        execute(cmd)
    def do_test(self):
        pass

class IOSBuiler(Builder):
    def do_build(self):
        buildcmd = [
            "xcodebuild",
            "IPHONEOS_DEPLOYMENT_TARGET=7.0",
            "ONLY_ACTIVE_ARCH=YES",
            "ARCHS=%s" % self.abi.arch,
            "-sdk", self.abi.target.lower(),
            "-configuration", self.buildypte,
            "-parallelizeTargets",
            "-jobs", "4",
            "-target", "ALL_BUILD","build"
        ]
        execute(buildcmd,self.builddir)

    def getXCodeMajor(self):
        ret = check_output(["xcodebuild", "-version"])
        m = re.match(r'XCode\s+(\d)\..*', ret, flags=re.IGNORECASE)
        if m:
            return int(m.group(1))
        return 0

    def get_cmake_generator(self):
        return "-GXcode";

    def get_toolchain_file(self):
        return os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),"platforms/ios/cmake/Toolchains/Toolchain-%s_Xcode.cmake" % self.abi.target)

    def platform_cmake_args(self):
        xcode_ver = self.getXCodeMajor()
        args = ['-DIOS_ARCH=%s' % self.abi.arch]
        if xcode_ver >= 7 and self.abi.target == 'iPhoneOS':
            args.append("-DCMAKE_C_FLAGS=-fembed-bitcode")
            args.append("-DCMAKE_CXX_FLAGS=-fembed-bitcode")
        if self.abi.target.lower().startswith("iphoneos"):
            args.append("-DENABLE_NEON=ON")
        args.append("-DCMAKE_EXECUTABLE_SUFFIX=.app")
        return args;

    def do_install(self):
        execute([self.get_cmake_exe(),
                 "-DBUILD_BYPT=%s" % self.buildypte,
                 "-DEFFECTIVE_PLATFORM_NAME=%s" % ("-"+self.abi.target.lower() if self.abi.target != "MacOSX" else ""),
                 "-DCMAKE_INSTALL_CONFIG_NAME=%s" % self.buildypte,
                  "-P",
                  os.path.join(self.builddir+"/cmake_install.cmake")
                 ])

    def do_test(self):
        pass

class OSXBuiler(IOSBuiler):
    def get_toolchain_file(self):
        return None
    def do_test(self):
        Builder.do_test(self)
    def platform_cmake_args(self):
        args = []
        args.append("-DCMAKE_OSX_ARCHITECTURES=%s" % self.abi.arch)
        return args;

def construct_builder(platform,srcdir, outdir, buildtype,abi,cmakeargs):
    # 调用各个平台的脚本
    if (platform == "win32"):
        return Win32Builer(platform,srcdir, outdir, buildtype,abi,cmakeargs)
    elif (platform == "linux"):
        return LinuxBuiler(platform, srcdir, outdir, buildtype, abi, cmakeargs)
    elif (platform == "osx"):
        return OSXBuiler(platform, srcdir, outdir, buildtype, abi, cmakeargs)
    elif (platform == "android"):
        return AndroidBuiler(platform, srcdir, outdir, buildtype, abi, cmakeargs)
    elif (platform == "ios"):
        return IOSBuiler(platform, srcdir, outdir, buildtype, abi, cmakeargs)

class Director:
    def __init__(self):
        log.basicConfig(format='%(message)s', level=log.DEBUG)
    def add_argument(self):
        # 参数定义
        self.parser = argparse.ArgumentParser(description='The %(prog)s is a cmake cross platform tool')
        self.parser.add_argument("-p","--platform",nargs="+", help="set platform",choices=['win32', 'linux', 'osx', 'android', 'ios'])
        self.parser.add_argument("-s","--src_dir", default=os.path.abspath(os.curdir), help="path to source dir")
        self.parser.add_argument("-o","--out_dir", help="path to out dir")
        self.parser.add_argument("-b","--build_type",nargs="+",default=['debug', 'release'], help="build type", choices=['debug', 'release'])
        self.parser.add_argument("-a","--arch",nargs="+",help="build arch", choices=['x86', 'x86_64',"armeabi","armeabi-v7a","arm64-v8a","mips","mips64","i386","armv7","armv7s","arm64"],default=['x86', 'x86_64',"armeabi","armeabi-v7a","arm64-v8a","mips","mips64","i386","armv7","armv7s","arm64"])
        self.parser.add_argument("-c","--cmakeargs",nargs="+",type=str, help="other args pass to cmake")
        self.parser.add_argument("-n",'--ndk_path',help="Path to Android NDK to use for build")
        #, default="D:\\android\\sdk\\ndk-bundle"
        # parser.add_argument('--sdk_path',default="D:\\android\\sdk", help="Path to Android SDK to use for build")

    def config_abi(self):
        # 配置abi
        self.args.abi=[];
        for i,platform in enumerate(self.args.platform):
            for i, arch in enumerate(self.args.arch):
                if platform in ["win32","linux"]:
                    if arch in ["x86","x86_64"]:
                        self.args.abi.append(ABI(platform, arch))
                elif platform in ["osx"]:
                    if arch in ["i386", "x86_64"]:
                        self.args.abi.append(ABI(platform, arch, "MacOSX"))
                elif platform == "android":
                    if arch in ["x86","x86_64","armeabi","armeabi-v7a","arm64-v8a","mips","mips64"]:
                        self.args.abi.append(ABI(platform, arch))
                elif platform == "ios":
                    if arch in ["i386","x86_64"]:
                        self.args.abi.append(ABI(platform, arch,"iPhoneSimulator"))
                    elif arch in ["armv7","armv7s","arm64"]:
                        self.args.abi.append(ABI(platform, arch,"iPhoneOS"))
    def parse_args(self):
        #打印参数信息
        log.info("cmd args:%s", sys.argv)
        self.args = self.parser.parse_args()
        log.debug("parse_args: %s", self.args)

        #给出默认参数
        if self.args.platform is None:
            self.args.platform=[]
            if sys.platform == "win32":
                self.args.platform.append(sys.platform)
            elif sys.platform == "linux2":
                self.args.platform.append("linux")
            elif sys.platform == "darwin":
                self.args.platform.append("osx")
        if len(self.args.platform) == 0:
            raise Fail("no platform set");

        #检查参数是否合法
        if self.args.src_dir is not None:
            self.args.src_dir = os.path.abspath(self.args.src_dir)
        if not os.path.exists(os.path.join(self.args.src_dir,"CMakeLists.txt")):
            raise Fail("no CMakeLists.txt in %s" % os.path.abspath(self.args.src_dir));

        if self.args.out_dir is not None:
            self.args.out_dir = os.path.abspath(self.args.out_dir)
        else:
            self.args.out_dir = self.args.src_dir

        #检查android的ndk环境
        if "android" in self.args.platform:
            if self.args.ndk_path is not None:
                os.environ["ANDROID_NDK"] = self.args.ndk_path
            if "ANDROID_NDK" not in os.environ.keys():
                raise Fail("not set android ndk")
            log.info("Android NDK path: %s", os.environ["ANDROID_NDK"])
        #设置编译选项
        build_types=[]
        for build_type in self.args.build_type:
            build_types.append(build_type.capitalize())
        self.args.build_type = build_types

        log.debug("configed args: %s", self.args)
        self.config_abi()
        log.info("all abi:")
        if len(self.args.abi) ==0 :
            raise Fail("arch set error for %s" % self.args.platform)
        for j, abi in enumerate(self.args.abi):
            log.info("%s", abi)

    def direct(self):
        self.add_argument()
        self.parse_args()
        if len(self.args.build_type) > 0 and  len(self.args.abi) > 0 :
            #编译
            for i,build_type in enumerate(self.args.build_type):
                for j, abi in enumerate(self.args.abi):
                    log.info("=====")
                    log.info("===== Building library for %s-%s start", abi,build_type)
                    log.info("=====")
                    builder = construct_builder(abi.platform, self.args.src_dir, self.args.out_dir, build_type,abi, self.args.cmakeargs)
                    builder.clean_library_build_dir()
                    builder.build_library()
                    log.info("=====")
                    log.info("===== Building library for %s-%s end", abi,build_type)
                    log.info("=====")
                log.info("=====")
                log.info("===== Build finished")
                log.info("=====")

if __name__ == "__main__":
    director = Director()
    director.direct()