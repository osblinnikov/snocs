import os.path
import sys
import string

def prepare_default(args):
    args['TOOLS'] = None
    args['CPPPATH'].extend([])
    args['CPPDEFINES'].extend([])
    args['LIBPATH'].extend([])
    if args['TARGET_ARCH'] == 'x86':
        args['CCFLAGS'].extend([])
        args['LINKFLAGS'].extend([])
    elif args['TARGET_ARCH'] == 'x64':
        args['CCFLAGS'].extend([])
        args['LINKFLAGS'].extend([])
    else:
        print "Unknown architecture: "+args['TARGET_ARCH']
        exit()
    if args['configuration'] == 'Debug':
        args['CCFLAGS'].extend([])
    return args