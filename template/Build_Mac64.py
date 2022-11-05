import sys
import os
import re
import shutil
import subprocess

def cmake_build(wes_version):
    cmd = 'cmake -G "Xcode"'
    if (wes_version != ""):
        cmd += ' -DWES_VERSION_STRING=%s' % (wes_version)
    cmd += ' ..'
    result = os.system(cmd)
    return result
    
def build_mac(proj_name, build_config):
    cmd = 'xcodebuild -project %s.xcodeproj -target ALL_BUILD -configuration %s' % (proj_name, build_config)
    result = os.system(cmd)
    return result
    
def pack_module(os_name, build_config):
    pack_module_script = 'pack_gui.py'
    cmd = 'python %s %s %s' % (pack_module_script, os_name, build_config)
    result = os.system(cmd)
    return result

def main():
    proj_name = "effect_tool"
    os_name = "Darwin" # Windows/Mac/Android/iOS

    print("usage:")
    print("python Build_Win64.py Debug rebuild                    # shortest")
    print("python Build_Win64.py Debug rebuild 3.0.x.y            # with version")
    #print("python Build_Win64.py Debug rebuild 3.0.x.y ON         # with version and gtest")
    #print("python Build_Mac64.py Debug rebuild 3.0.x.y ON arm64   # with version, gtest amd arm64")

    build_config = sys.argv[1] if len(sys.argv) >= 2 else "Release" # Debug/Release
    rebuild_flag = sys.argv[2] if len(sys.argv) >= 3 else "rebuild" # rebuild/no
    wes_version = sys.argv[3] if len(sys.argv) >= 4 else "" # 3.0.x.y
    #gtest_flag = sys.argv[4] if len(sys.argv) >= 5 else "OFF" # ON/OFF
    #plaform_config = sys.argv[5] if len(sys.argv) >= 6 else "x64" # arm64/x64
    
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
    result = build_mac(proj_name, build_config)
    if result != 0: return result

    # pack modules
    os.chdir(current_dir)
    result = pack_module(os_name, build_config)
    if result != 0: return result

    return 0
    
if __name__ == "__main__":
    if main() != 0 :
        sys.exit(1)
