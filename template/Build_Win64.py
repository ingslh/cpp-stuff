import sys
import os
import re
import shutil
import subprocess

def cmake_build(wes_version):
    cmd = r'"cmake -G "Visual Studio 15 2017 Win64""'
    if (wes_version != ""):
        cmd += ' -DWES_VERSION_STRING=%s' % (wes_version)
    cmd += ' ..'
    result = os.system(cmd)
    return result
    
def build_win(proj_name, build_config):
    ide_check_path =  ['C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\Community\\Common7\\IDE\\devenv.com',
                     'C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\Professional\\Common7\\IDE\\devenv.com',
                     'C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\Enterprise\\Common7\\IDE\\devenv.com']
    def find_ide():
        for ide in ide_check_path:
            if os.path.exists(ide):
                return ide
        return 'devenv.com'

    ide_path = find_ide()
    log_file = 'Window-x64-%s-Build-Log.txt' % build_config

    cmd = r'""%s" %s.sln /ReBuild "%s|x64" /Project ALL_BUILD.vcxproj /Out %s"' % (ide_path, proj_name, build_config, log_file)
    result = os.system(cmd)
    return result
    
def pack_module(os_name, build_config):
    pack_module_script = 'pack_gui.py'
    cmd = 'python %s %s %s' % (pack_module_script, os_name, build_config)
    result = os.system(cmd)
    return result

def main():
    proj_name = "effect_tool"
    os_name = "Windows" # Windows/Mac/Android/iOS

    print("usage:")
    print("python Build_Win64.py Debug rebuild                    # shortest")
    print("python Build_Win64.py Debug rebuild 3.0.x.y            # with version")
    #print("python Build_Win64.py Debug rebuild 3.0.x.y ON         # with version and gtest")

    build_config = sys.argv[1] if len(sys.argv) >= 2 else "Release" # Debug/Release
    rebuild_flag = sys.argv[2] if len(sys.argv) >= 3 else "rebuild" # rebuild/no
    wes_version = sys.argv[3] if len(sys.argv) >= 4 else "" # 3.0.x.y
    #gtest_flag = sys.argv[4] if len(sys.argv) >= 5 else "OFF" # NO/OFF
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    build_dir = os.path.join(current_dir, proj_name, "build")
    if (os.path.exists(build_dir) and rebuild_flag == "rebuild"):
        shutil.rmtree(build_dir)
    if (not os.path.exists(build_dir)):
        os.makedirs(build_dir)

    # cmake build
    os.chdir(build_dir)
    result = cmake_build(wes_version)
    if result != 0: return result

    # msvc build
    os.chdir(build_dir)
    result = build_win(proj_name, build_config)
    if result != 0: return result

    # pack modules
    os.chdir(current_dir)
    result = pack_module(os_name, build_config)
    if result != 0: return result

    return 0
    
if __name__ == "__main__":
    if main() != 0 :
        sys.exit(1)
