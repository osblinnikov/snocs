import os.path
import sys
import string

def prepare_vc9(args):
    COMPILE_ARCH = string.upper(args['TARGET_ARCH'])
    if args['TARGET_ARCH'] == 'x64':
        args['TARGET_ARCH'] = 'x86_64'
    args['MSVC_VERSION'] = '9.0'
    args['TOOLS'] = None
    args['CPPPATH'].extend([])
    args['CPPDEFINES'].extend([])
    args['LIBPATH'].extend([])
    args['LIBS'].extend([
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
    if args['configuration'] == 'Debug':
        args['LINKFLAGS'].extend(['/NOLOGO','/SUBSYSTEM:CONSOLE','/DEBUG','/MACHINE:'+COMPILE_ARCH])
        args['CPPDEFINES'].extend([ 
            'WIN32',
            '_DEBUG',
            '_CONSOLE'
        ])
        args['CCFLAGS'].extend(['/W4','/EHsc','/RTC1','/MDd','/nologo','/Z7','/TP','/errorReport:prompt'])
        args['MSVC_PDB'] = 1
    else:
        args['LINKFLAGS'].extend(['/NOLOGO','/SUBSYSTEM:CONSOLE','/MACHINE:'+COMPILE_ARCH])
        args['CPPDEFINES'].extend([ 
            'WIN32',
            'NDEBUG',
            '_CONSOLE'
        ])
        args['CCFLAGS'].extend(['/W4','/EHsc','/RTC1','/MD','/nologo','/Z7','/TP','/errorReport:prompt'])
        
    return args