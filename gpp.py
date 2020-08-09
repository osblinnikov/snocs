import os.path
import sys
import string


def prepare_gpp(env):
    

    env['CC'] = 'g++'
    env['TOOLS'] = ['default']

    additionalCPPFLAGS = []
    if env.__contains__('more-warnings') and env['more-warnings'] == '1':
        additionalCPPFLAGS += warnFlags

    if env.__contains__('warnings-as-errors') and env['warnings-as-errors'] == '1':
        additionalCPPFLAGS += '-Werror'

    env['CPPPATH'].extend([])
    env['CPPDEFINES'].extend([])
    if env['PLATFORM'] == 'x86':
        env['CPPFLAGS'].extend(['-m32','-fpic','-std=gnu++11']+additionalCPPFLAGS)
        env['LINKFLAGS'].extend(['-m32'])
        env['LIBS'].extend([])#'stdc++'
        env['LIBPATH'].extend(['/usr/lib32'])
    elif env['PLATFORM'] == 'x64':
        env['CPPFLAGS'].extend(['-m64','-fpic','-std=gnu++11']+additionalCPPFLAGS)
        env['LINKFLAGS'].extend(['-m64'])
        env['LIBPATH'].extend(['/usr/local/lib64'])
    else:
        print("Unknown platform: "+env['PLATFORM'])
        sys.exit()
    if env['CONFIGURATION'] == 'Debug':
        env['CPPFLAGS'].extend(['-g'])

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