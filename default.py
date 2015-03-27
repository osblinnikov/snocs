import os.path
import sys
import string

def prepare_default(env):
    env['TOOLS'] = None
    env['CPPPATH'].extend([])
    env['CPPDEFINES'].extend([])
    env['LIBPATH'].extend([])
    if env['TARGET_ARCH'] == 'x86':
        env['CCFLAGS'].extend([])
        env['LINKFLAGS'].extend([])
    elif env['TARGET_ARCH'] == 'x64':
        env['CCFLAGS'].extend([])
        env['LINKFLAGS'].extend([])
    else:
        print "Unknown architecture: "+env['TARGET_ARCH']
        exit()
    if env['configuration'] == 'Debug':
        env['CCFLAGS'].extend([])
    return env