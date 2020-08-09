import os.path
import sys
import string

def prepare_gcc(env):
    env['CC'] = 'gcc'
    env['TOOLS'] = ['default', 'gcc']
    env['CPPPATH'].extend([])
    env['CPPDEFINES'].extend([])
    if env['PLATFORM'] == 'x86':
        env['CCFLAGS'].extend(['-m32','-fpic','-Werror'])
        env['LINKFLAGS'].extend(['-m32'])
        env['LIBS'].extend([])#'stdc++'
        env['LIBPATH'].extend(['/usr/lib32'])
    elif env['PLATFORM'] == 'x64':
        env['CCFLAGS'].extend(['-m64','-fpic','-Werror'])
        env['LINKFLAGS'].extend(['-m64'])
        env['LIBPATH'].extend(['/usr/local/lib64'])
    else:
        print("Unknown platform: "+env['PLATFORM'])
        sys.exit()
    if env['CONFIGURATION'] == 'Debug':
        env['CCFLAGS'].extend(['-g'])
    return env
