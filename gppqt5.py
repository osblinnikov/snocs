import os.path
import sys
import string

def get_immediate_subdirectories(dir):
    if os.path.exists(dir):
        return [name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name))]
    else:
        return []

def detectLatestQtDir(arch):
    if arch == 'x86':
        if sys.platform.startswith("linux"):
            return os.environ.get("QTDIR",os.path.expanduser("~/Qt-x86/5.3/gcc"))
        else:
            return os.environ.get("QTDIR","C:\\Qt\\5.3\\mingw")
    elif arch == 'x64':
        if sys.platform.startswith("linux"):
            return os.environ.get("QTDIR",os.path.expanduser("~/Qt/5.3/gcc_64"))
        else:
            return os.environ.get("QTDIR","C:\\Qt\\5.3\\mingw")

def prepare_gppqt5(args):
    args['TOOLS'] = ['default']
    args['QT_TOOL'] = 'qt5'
    args['QT_DIR_NAME'] = 'QT5DIR'
    args['QT_DIR'] = detectLatestQtDir(args['TARGET_ARCH'])
    args['QT_PKG_CONFIG_PATH'] = os.path.join(args['QT_DIR'], 'lib/pkgconfig')
    args['CPPPATH'].extend([])
    args['CPPDEFINES'].extend([])
    if args['TARGET_ARCH'] == 'x86':
        args['CCFLAGS'].extend(['-m32','-fpic','-Wall','-Werror','-xc++'])
        args['LINKFLAGS'].extend(['-m32'])
        args['LIBS'].extend([])#'stdc++'
        args['LIBPATH'].extend(['/usr/lib32'])
    elif args['TARGET_ARCH'] == 'x64':
        args['CCFLAGS'].extend(['-m64','-fpic','-Wall','-Werror','-xc++'])
        args['LINKFLAGS'].extend(['-m64'])
        args['LIBPATH'].extend(['/usr/local/lib64'])
    else:
        print "Unknown architecture: "+args['TARGET_ARCH']
        exit()
    if args['configuration'] == 'Debug':
        args['CCFLAGS'].extend(['-g'])
    return args
