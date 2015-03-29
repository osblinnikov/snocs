import os.path
import sys
import string


def prepare_gpp(env):
    

    env['CC'] = 'g++'
    env['TOOLS'] = ['default']
    env['QTVER'] = os.environ.get("QTVER", False)
    if env['QTVER'] != False:
        if env['QTVER'].startswith('5'):
          env['QT_DIR_NAME'] = 'QT5DIR'
          env['QT_TOOL'] = 'qt5'
        elif env['QTVER'].startswith('4'):
          env['QT_DIR_NAME'] = 'QT4DIR'
          env['QT_TOOL'] = 'qt4'
        else:
          print 'Unknown QTVER '+env['QTVER']+" only started with 4 or 5 is allowed"
          Exit(1)
        env['QT_DIR'] = detectLatestQtDir(env['PLATFORM'],env['QTVER'])
        env['QT_PKG_CONFIG_PATH'] = os.path.join(env['QT_DIR'], 'lib/pkgconfig')


    additionalCCFLAGS = []
    if env.has_key('more-warnings') and env['more-warnings'] == '1':
        additionalCCFLAGS += warnFlags

    if env.has_key('warnings-as-errors') and env['warnings-as-errors'] == '1':
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

def detectLatestQtDir(platform,QTVER):
  QTDIR = os.environ.get("QTDIR",'')
  if len(QTDIR) == 0:
    if sys.platform.startswith("linux"):
      if platform == 'x86':
        QTDIR = os.path.expanduser("~/Qt-x86/"+QTVER+"/gcc")
      else:
        QTDIR = os.path.expanduser("~/Qt/"+QTVER+"/gcc_64")
    elif sys.platform.startswith("windows"):
      QTDIR = "C:\\Qt\\"+QTVER+"\\mingw"
    else:
      print "gpp.detectLatestQtDir(): QTDIR env variable is not set and OS "+sys.platform+" is unknown"
  
  if not os.path.exists(QTDIR):
    print 'gpp.detectLatestQtDir(): QTDIR='+QTDIR+" not exists"
    Exit(1)
  return QTDIR

