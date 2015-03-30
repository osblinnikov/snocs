import os.path
import sys
import string

def prepare_mingw(env):
    env['TOOLS'] = ['mingw']
    env['CPPPATH'].extend([])
    env['CPPDEFINES'].extend([])
    env['LIBPATH'].extend([])
    if env['PLATFORM'] == 'x86':
        env['CPPFLAGS'].extend(['-m32'])
        env['LINKFLAGS'].extend(['-m32','ws2_32','-liphlpapi'])
    elif env['PLATFORM'] == 'x64':
        env['CPPFLAGS'].extend(['-m64'])
        env['LINKFLAGS'].extend(['-m64','ws2_32','-liphlpapi'])
    else:
        print "Unknown platform: "+env['PLATFORM']
        exit()
    if env['CONFIGURATION'] == 'Debug':
        env['CPPFLAGS'].extend(['-g'])
    return env