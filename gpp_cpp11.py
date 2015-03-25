import os.path
import sys
import string

def prepare_gpp_cpp11(args):
    args['CC'] = 'g++'
    args['TOOLS'] = ['default']
    args['CPPPATH'].extend([])
    args['CPPDEFINES'].extend([])
    if args['TARGET_ARCH'] == 'x86':
        args['CCFLAGS'].extend(['-m32','-fpic','-Wall','-Werror','-std=gnu++11'])
        args['LINKFLAGS'].extend(['-m32'])
        args['LIBS'].extend([])#'stdc++'
        args['LIBPATH'].extend(['/usr/lib32'])
    elif args['TARGET_ARCH'] == 'x64':
        args['CCFLAGS'].extend(['-m64','-fpic','-Wall','-Werror','-std=gnu++11'])
        args['LINKFLAGS'].extend(['-m64'])
        args['LIBPATH'].extend(['/usr/local/lib64'])
    else:
        print "Unknown architecture: "+args['TARGET_ARCH']
        exit()
    if args['configuration'] == 'Debug':
        args['CCFLAGS'].extend(['-g'])
    return args
