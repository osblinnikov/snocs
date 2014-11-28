import os.path
import sys
from gppqt5 import *
from gpp import *
from gcc import *
from mingw import *
from default import *
from vc9 import *

#PLEASE change it if you don't want the standard snocs location
PROJECTS_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..','..'))

def prepare_args(ARGUMENTS):
    #--------command line arguments------------
    args = {}
    isShared = ARGUMENTS.get('shared', '0')
    if isShared == '0':
        args['NO_DYNAMIC_BUILD'] = '1'
        args['NO_STATIC_BUILD'] = '0'
    else:
        args['NO_DYNAMIC_BUILD'] = '0'
        args['NO_STATIC_BUILD'] = '1'
    # args['CC'] = None
    args['CLEANING_STAGE'] = ARGUMENTS.get('cleaning_all', '0')
    args['ONLY_PROJECT_CLEANING_STAGE'] = ARGUMENTS.get('cleaning_one', '0')
    args['TESTNORUN'] = ARGUMENTS.get('testnorun', '0')
    args['SNOCSCRIPT'] = ARGUMENTS.get('snocscript', None)
    if args['SNOCSCRIPT'] == None or args['SNOCSCRIPT']=="":
        print "SNocscript is not specified!"
        exit()
    args['configuration'] = ARGUMENTS.get('configuration', 'Release')
    if args['configuration'] == 'debug':
        args['configuration'] = 'Debug'
    if args['configuration'] != 'Debug':
        args['configuration'] = 'Release'
    args['COMPILER_CODE'] = ARGUMENTS.get('compiler', 'gcc').lower()
    args['TARGET_ARCH'] = ARGUMENTS.get('platform', 'x86').lower()
    if args['TARGET_ARCH'] == 'Win32':
        args['TARGET_ARCH'] = 'x86'
    args['TARGET_ARCH'] = args['TARGET_ARCH'].lower()
    args['CCCOMSTR'] = None
    args['LINKCOMSTR'] = None
    if ARGUMENTS.get('verbose') != "1":
        args['CCCOMSTR'] = "Compiling $TARGET"
        args['LINKCOMSTR'] = "Linking $TARGET"
    #--------deploy parameters--------
    args['PROJECTS_ROOT_PATH'] = PROJECTS_ROOT_PATH
    args['INSTALL_PATH'] = os.path.join(args['PROJECTS_ROOT_PATH'])
    args['INSTALL_ALIASES'] = [] #here will be the targets for install alias
    args['TEST_ALIASES'] = [] #here will be the targets for test alias
    args['ARCHITECTURE_CODE'] = '_'+args['COMPILER_CODE']+'_'+args['TARGET_ARCH']
    #---------init params-----------
    args['MSVC_PDB'] = 0
    args['MSVC_VERSION'] = None
    args['APP_DEPENDENCIES'] = {}
    args['APP_BUILD'] = {}
    args['TOOLS'] = 'default'
    args['LINKFLAGS'] = []
    args['CCFLAGS'] = []
    args['LIBS'] = []
    args['LIBPATH']=[]
    args['PROJECTS_SRC_PATH'] = os.path.join(args['PROJECTS_ROOT_PATH'],'src')
    args['CPPPATH'] = [
        args['PROJECTS_SRC_PATH']
    ]
    args['CPPDEFINES'] = []
    #--------SWITCHING COMPILER------
    if args['COMPILER_CODE'] == 'default':
        print "WARNING: compiler was not specified, using default parameters"
        args = prepare_default(args)
    elif args['COMPILER_CODE'] == 'gppqt5':
        args = prepare_gppqt5(args)       
    elif args['COMPILER_CODE'] == 'gpp':
        args = prepare_gpp(args)        
    elif args['COMPILER_CODE'] == 'gcc':
        args = prepare_gcc(args)
    elif args['COMPILER_CODE'] == 'mingw':
        args = prepare_mingw(args)
    elif args['COMPILER_CODE'] == 'vc9':
        args = prepare_vc9(args)
    elif args['COMPILER_CODE'] == 'vc10':
        args = prepare_vc9(args)
        args['MSVC_VERSION'] = '10.0'
    elif args['COMPILER_CODE'] == 'vc11':
        args = prepare_vc9(args)
        args['MSVC_VERSION'] = '11.0'
    elif args['COMPILER_CODE'] == 'vc11exp':
        args = prepare_vc9(args)
        args['MSVC_VERSION'] = '11.0Exp'
    else:
        print "---Custom---"        
        args['TOOLS'] = ['default']
        args['CC'] = args['COMPILER_CODE']
        args['LINK'] = ARGUMENTS.get('linker', 'ld').lower()
        print "compiler: "+args['CC']
        print "linker: "+args['LINK']
    args['CPPPATH'].extend(ARGUMENTS.get('CPPPATH', '').split(','))
    args['CPPDEFINES'].extend(ARGUMENTS.get('CPPDEFINES', '').split(','))
    args['CCFLAGS'].extend(ARGUMENTS.get('CCFLAGS', '').split(','))
    args['LINKFLAGS'].extend(ARGUMENTS.get('LINKFLAGS', '').split(','))
    args['LIBPATH'].extend(ARGUMENTS.get('LIBPATH', '').split(','))
    args['LIBS'].extend(ARGUMENTS.get('LIBS', '').split(','))        
    return args

def builder_unit_test(target, source, env):
    d = env.Dictionary()
    if d['TESTNORUN'] == '0':
        app = str(source[0].abspath)
        if os.spawnl(os.P_WAIT, app, app)==0:
            open(str(target[0]),'w').write("PASSED: "+source[0].path+"\n")
        else:
            open(str(target[0]),'w').write("FAILED: "+source[0].path+"\n")
            return 1

def preparePaths(env,args):
    args['BIN_DIR'] = os.path.join(args['SNOCSCRIPT_PATH'], args['configuration'], 'bin')
    args['LIB_DIR'] = os.path.join(args['SNOCSCRIPT_PATH'], args['configuration'], 'lib')
    env.AppendENVPath('LD_LIBRARY_PATH', args['LIB_DIR'])
    env.AppendENVPath('PATH', args['LIB_DIR'])

def printHelp():
    print "**********************"
    print "Snocs is a little wrapper on SCons Software Construction tool (http://www.scons.org/)."
    print "Usage: snocs [SNocscriptFilePath] [options]"
    print "Examples:"
    print "  snocs .. compiler=vc9 platform=x86 configuration=Debug" 
    print "  snocs test -Q           #build and run tests with reduced log" 
    print "  snocs install -c        #clean installation"
    print "  snocs icanchangethisdomain/SomeProjectName -r  #run Python script"
    print "SNocscriptFilePath can be absolute, relative to current path, or "
    print "relative to projects root path e.g.:"
    print "  snocs example compiler=vc9 test"
    print "**********************"
    print "Available options:"
    print "  compiler={gcc,gpp,gppqt5,mingw,vc9,vc10,vc11,vc11exp}"
    print "  configuration={Debug,Release}"
    print "  platform={x86,Win32,x64} # Win32 is an alias to x86"
    print "  verbose=1 # enables scons debug output"
    print "  shared=1 | 0 #enables building shared libraries for all projects of default config"
    print "  testnorun=0 | 1 #disables tests run in case of test/install targets"
    print "  -r        # execute SNocscriptFilePath/SNocscript as Python script"
    print "  -h        # print this help"
    print "  -c        # execute cleaning only for chosen SNocscript, not dependent libs"
    print "  -call     # execute cleaning for current and all dependent projects"
    print "**********************"
    print "Other options can be SCons specific."
    print "  If you want to change default path to the Projects directory please see the"
    print "  builder.py file and PROJECTS_ROOT_PATH variable"
    print "  During 'test' phase snocs updates LD_LIBRARY_PATH local copy to provide"
    print "  of shared libraries"
    print "**********************"
    
