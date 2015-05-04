import os.path
import sys
import string

def prepare_vc9(env):
    env['TARGET_ARCH'] = env['PLATFORM']
    if env['PLATFORM'] == 'x64':
        env['TARGET_ARCH'] = 'x86_64'
    env['MSVC_VERSION'] = '9.0'
    env['TOOLS'] = None
    env['CPPPATH'].extend([])
    env['CPPDEFINES'].extend([])
    env['LIBPATH'].extend([])
    env['LIBS'].extend([
        'kernel32.lib',
        'user32.lib',
        'gdi32.lib',
        'winspool.lib',
        'comdlg32.lib',
        'advapi32.lib',
        'shell32.lib',
        'ole32.lib',
        'oleaut32.lib',
        'uuid.lib',
        'odbc32.lib',
        'odbccp32.lib'
    ])
    if env['CONFIGURATION'] == 'Debug':
        env['LINKFLAGS'].extend(['/NOLOGO','/SUBSYSTEM:CONSOLE','/DEBUG','/MACHINE:'+env['TARGET_ARCH'].upper()])
        env['CPPDEFINES'].extend([ 
            'WIN32',
            '_CONSOLE'
        ])
        env['CPPFLAGS'].extend(['/W4','/EHsc','/RTC1','/MDd','/nologo','/Z7','/TP','/errorReport:prompt'])
        env['MSVC_PDB'] = 1
    else:
        env['LINKFLAGS'].extend(['/NOLOGO','/SUBSYSTEM:CONSOLE','/MACHINE:'+env['TARGET_ARCH'].upper()])
        env['CPPDEFINES'].extend([ 
            'WIN32',
            '_CONSOLE'
        ])
        env['CPPFLAGS'].extend(['/W4','/EHsc','/RTC1','/MD','/nologo','/Z7','/TP','/errorReport:prompt'])
        
    return env
