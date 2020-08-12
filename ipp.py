import os
import sys
import string

def prepare_ipp(env):
    env['CC'] = 'i++'
    env['TOOLS'] = ['default']
    env['CPPPATH'].extend([])
    env['CPPDEFINES'].extend(['WITH_INTEL_HLS'])
    if any([('-march=' in v) for v in env['CCFLAGS']]):
        raise Exception("Please use 'platform' to specify architecture with ipp compiler")

    if env['PLATFORM'] == 'x64':
        env['CCFLAGS'].extend(['-m64','-Werror', '-march=x86-64'])
        # env['LINKFLAGS'].extend(['-m64','-march=x86-64'])
        env['LIBPATH'].extend(['/usr/local/lib64'])
    else:
        env['CCFLAGS'].extend(['-m64','-Werror', '-march='+env['PLATFORM']])
        # env['LINKFLAGS'].extend(['-m64', '-march='+env['PLATFORM']])
        env['LIBPATH'].extend(['/usr/local/lib64'])

    if env['CONFIGURATION'] != 'Debug':
        env['CCFLAGS'].extend(['-g0'])

    HLS_LIBDIR = os.environ.get("HLS_LIBDIR", "")
    if not HLS_LIBDIR:
        raise Exception("HLS_LIBDIR environment variable is expected")
    env['LD_LIBRARY_PATH'].extend([HLS_LIBDIR])

    return env
