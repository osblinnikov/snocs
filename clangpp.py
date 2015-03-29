import os.path
import sys
import string

def prepare_clangpp(env):
    # env['CC'] = 'clang'
    env['CXX'] = 'clang++'
    env['TOOLS'] = ['default']
    env['CPPPATH'].extend([])
    env['CPPDEFINES'].extend([])
    additionalCCFLAGS = []
    if env.has_key('more-warnings') and env['more-warnings'] == '1':
        additionalCCFLAGS += warnFlags

    if env.has_key('warnings-as-errors') and env['warnings-as-errors'] == '1':
        additionalCCFLAGS += '-Werror'

    if env['PLATFORM'] == 'x86':
        env['CCFLAGS'].extend(['-m32','-std=c++11','-stdlib=libc++']+additionalCCFLAGS)
        env['LINKFLAGS'].extend(['-m32','-stdlib=libc++'])
        env['LIBS'].extend([])
        env['LIBPATH'].extend(['/usr/lib32'])
    elif env['PLATFORM'] == 'x64':
        env['CCFLAGS'].extend(['-m64','-std=c++11','-stdlib=libc++']+additionalCCFLAGS)
        env['LINKFLAGS'].extend(['-m64','-stdlib=libc++'])
        env['LIBPATH'].extend(['/usr/local/lib64'])
    else:
        print "Unknown platform: "+env['PLATFORM']
        exit()
    if env['CONFIGURATION'] == 'Debug':
        env['CCFLAGS'].extend(['-g'])
    return env


warnFlags = ["-Weverything","-Wno-c++98-compat","-Wno-padded","-Wno-documentation-unknown-command","-Wno-exit-time-destructors","-Wno-global-constructors","-Wno-missing-prototypes","-Wno-c++98-compat-pedantic","-Wno-unused-member-function","-Wno-unused-const-variable","-Wno-switch-enum","-Wno-missing-noreturn","-Wno-covered-switch-default"]