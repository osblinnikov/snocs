import os.path
import sys
import string

def prepare_mingw(args):
    args['TOOLS'] = ['mingw']
    args['CPPPATH'].extend([])
    args['CPPDEFINES'].extend([])
    args['LIBPATH'].extend([])
    if args['TARGET_ARCH'] == 'x86':
        args['CCFLAGS'].extend(['-m32'])
        args['LINKFLAGS'].extend(['-m32'])
    elif args['TARGET_ARCH'] == 'x64':
        args['CCFLAGS'].extend(['-m64'])
        args['LINKFLAGS'].extend(['-m64'])
    else:
        print "Unknown architecture: "+args['TARGET_ARCH']
        exit()
    if args['configuration'] == 'Debug':
        args['CCFLAGS'].extend(['-g'])
    return args