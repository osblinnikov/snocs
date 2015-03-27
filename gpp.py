import os.path
import sys
import string


def prepare_gpp(env, withqt, morewarns, warnaserr):
    additionalCCFLAGS = []

    env['CC'] = 'g++'
    env['TOOLS'] = ['default']
    
    if withqt:
        env['QT_TOOL'] = 'qt5'
        env['QT_DIR_NAME'] = 'QT5DIR'
        env['QT_DIR'] = detectLatestQtDir(env['PLATFORM'])
        if not os.path.exists(env['QT_DIR']):
            print 'either QTDIR environment variable is not set or '+env['QT_DIR']+" is not exists"
            Exit(1)
        env['QT_PKG_CONFIG_PATH'] = os.path.join(env['QT_DIR'], 'lib/pkgconfig')

    if morewarns:
        additionalCCFLAGS += warnFlags

    if warnaserr:
        additionalCCFLAGS += '-Werror'

    env['CPPPATH'].extend([])
    env['CPPDEFINES'].extend([])
    if env['PLATFORM'] == 'x86':
        env['CCFLAGS'].extend(['-m32','-fpic','-std=gnu++11']+additionalCCFLAGS)
        env['LINKFLAGS'].extend(['-m32'])
        env['LIBS'].extend([])#'stdc++'
        env['LIBPATH'].extend(['/usr/lib32'])
    elif env['PLATFORM'] == 'x64':
        env['CCFLAGS'].extend(['-m64','-fpic','-std=gnu++11']+additionalCCFLAGS)
        env['LINKFLAGS'].extend(['-m64'])
        env['LIBPATH'].extend(['/usr/local/lib64'])
    else:
        print "Unknown platform: "+env['PLATFORM']
        exit()
    if env['CONFIGURATION'] == 'Debug':
        env['CCFLAGS'].extend(['-g'])

    return env


warnFlags = ["-Waddress","-Wall","-Warray-bounds",
               "-Wattributes","-Wbuiltin-macro-redefined","-Wcast-align",
               "-Wcast-qual","-Wchar-subscripts","-Wclobbered","-Wcomment",
               "-Wconversion","-Wconversion-null","-Wcoverage-mismatch",
               "-Wcpp","-Wdelete-non-virtual-dtor","-Wdeprecated",
               "-Wdeprecated-declarations","-Wdiv-by-zero","-Wdouble-promotion",
               "-Wempty-body","-Wendif-labels","-Wenum-compare","-Wextra",
               "-Wfloat-equal","-Wformat","-Wfree-nonheap-object",
               "-Wignored-qualifiers","-Winit-self",
               "-Winline","-Wint-to-pointer-cast","-Winvalid-memory-model",
               "-Winvalid-offsetof","-Wlogical-op","-Wmain","-Wmaybe-uninitialized",
               "-Wmissing-braces","-Wmissing-field-initializers","-Wmultichar",
               "-Wnarrowing","-Wnoexcept","-Wnon-template-friend",
               "-Wnon-virtual-dtor","-Wnonnull","-Woverflow",
               "-Woverlength-strings","-Wparentheses",
               "-Wpmf-conversions","-Wpointer-arith","-Wreorder",
               "-Wreturn-type","-Wsequence-point","-Wshadow",
               "-Wsign-compare","-Wswitch","-Wtype-limits","-Wundef",
               "-Wuninitialized","-Wunused","-Wvla","-Wwrite-strings"]

def get_immediate_subdirectories(dir):
    if os.path.exists(dir):
        return [name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name))]
    else:
        return []

def detectLatestQtDir(platform):
    if platform == 'x86':
        if sys.platform.startswith("linux"):
            return os.environ.get("QTDIR",os.path.expanduser("~/Qt-x86/5.3/gcc"))
        else:
            return os.environ.get("QTDIR","C:\\Qt\\5.3\\mingw")
    elif platform == 'x64':
        if sys.platform.startswith("linux"):
            return os.environ.get("QTDIR",os.path.expanduser("~/Qt/5.3/gcc_64"))
        else:
            return os.environ.get("QTDIR","C:\\Qt\\5.3\\mingw")

