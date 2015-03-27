import os.path
import os
import sys
import copy

from gpp import *
from gcc import *
from mingw import *
from default import *
from vc9 import *

#PLEASE change it if you don't want the standard snocs location
PROJECTS_SRC_PATH = os.getenv('SNOCS_PROJECTS_SRC_PATH', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

def prepare_env(ARGUMENTS):
    #--------command line arguments------------
    env = {}
    for k,v in ARGUMENTS.iteritems():
        env[k.upper()] = v

    #init defaults
    env['SHARED'] = ARGUMENTS.get('shared', '0')
    env['CLEANING'] = ARGUMENTS.get('cleaning', '0')
    env['BUILD_ALL'] = ARGUMENTS.get('build_all', '0')
    env['TESTNORUN'] = ARGUMENTS.get('testnorun', '0')
    env['SNOCSCRIPT'] = ARGUMENTS.get('snocscript', None)
    env['CONFIGURATION'] = ARGUMENTS.get('configuration', 'Release')
    env['COMPILER'] = ARGUMENTS.get('compiler', 'gcc')
    env['TARGET_ARCH'] = env['PLATFORM'] = ARGUMENTS.get('platform', 'x86')
    env['LINKER'] = ARGUMENTS.get('linker', 'ld')
    env['WITHOUT'] = ARGUMENTS.get('WITHOUT', '').split(':')

    if env['SNOCSCRIPT'] == None or env['SNOCSCRIPT']=="":
        print "SNocscript is not specified!"
        exit()
    
    if env['CONFIGURATION'].lower() == 'debug'.lower():
        env['CONFIGURATION'] = 'Debug'
    else:
        env['CONFIGURATION'] = 'Release'
    
    if env['PLATFORM'].lower() == 'Win32'.lower():
        env['PLATFORM'] = 'x86'


    #--------deploy parameters--------
    env['INSTALL_BIN_PATH'] = os.getenv('SNOCS_INSTALL_BIN_PATH', os.path.abspath(os.path.join(PROJECTS_SRC_PATH,'..','bin')))
    env['INSTALL_LIB_PATH'] = os.getenv('SNOCS_INSTALL_LIB_PATH', os.path.abspath(os.path.join(PROJECTS_SRC_PATH,'..','lib')))
    env['PROJECTS_SRC_PATH'] = PROJECTS_SRC_PATH
    env['INSTALL_ALIASES'] = [] #here will be the targets for install alias
    env['TEST_ALIASES'] = [] #here will be the targets for test alias
    env['ARCHITECTURE_CODE'] = '_'+env['COMPILER']+'_'+env['PLATFORM']
    #---------init params-----------
    env['MSVC_PDB'] = 0
    env['MSVC_VERSION'] = None
    env['APP_DEPENDENCIES'] = {}
    env['APP_BUILD'] = {}
    env['TOOLS'] = 'default'
    env['LINKFLAGS'] = []
    env['CCFLAGS'] = []
    env['LIBS'] = []
    env['LIBPATH']=[]
    env['CPPPATH'] = [
        env['PROJECTS_SRC_PATH']
    ]
    env['CPPDEFINES'] = []
    #--------SWITCHING COMPILER------
    if env['COMPILER'] == 'default':
        print "WARNING: compiler was not specified, using default parameters"
        env = prepare_default(env)      
    elif env['COMPILER'] == 'gpp':
        env = prepare_gpp(env,False,False,False)
    elif env['COMPILER'] == 'gppwarn':
        env = prepare_gpp(env,False,True,False)
    elif env['COMPILER'] == 'gppwarnerr':
        env = prepare_gpp(env,False,True,True) 
    elif env['COMPILER'] == 'gppqt5':
        env = prepare_gpp(env,True,False,False)
    elif env['COMPILER'] == 'gppqt5warn':
        env = prepare_gpp(env,True,True,False)  
    elif env['COMPILER'] == 'gppqt5warnerr':
        env = prepare_gpp(env,True,True,True)
    elif env['COMPILER'] == 'gcc':
        env = prepare_gcc(env)
    elif env['COMPILER'] == 'mingw':
        env = prepare_mingw(env)
    elif env['COMPILER'] == 'vc9':
        env = prepare_vc9(env)
        env['MSVC_VERSION'] = '9.0'
    elif env['COMPILER'] == 'vc10':
        env = prepare_vc9(env)
        env['MSVC_VERSION'] = '10.0'
    elif env['COMPILER'] == 'vc11':
        env = prepare_vc9(env)
        env['MSVC_VERSION'] = '11.0'
    elif env['COMPILER'] == 'vc11exp':
        env = prepare_vc9(env)
        env['MSVC_VERSION'] = '11.0Exp'
    else:
        print "---Custom---"        
        env['TOOLS'] = ['default']
        env['CC'] = env['COMPILER']
        env['LINK'] = env['LINKER']
        print "compiler: "+env['CC']
        print "linker: "+env['LINK']

    env['CPPPATH'].extend(ARGUMENTS.get('CPPPATH', '').split(':'))
    env['CPPDEFINES'].extend(ARGUMENTS.get('CPPDEFINES', '').split(':'))
    env['CCFLAGS'].extend(ARGUMENTS.get('CCFLAGS', '').split(':'))
    env['LINKFLAGS'].extend(ARGUMENTS.get('LINKFLAGS', '').split(':'))
    env['LIBPATH'].extend(ARGUMENTS.get('LIBPATH', '').split(':'))
    env['LIBS'].extend(ARGUMENTS.get('LIBS', '').split(':'))
    env['bcp'] = copy.deepcopy(env)

    return env

def builder_unit_test(target, source, env):
    d = env.Dictionary()
    if d['TESTNORUN'] == '0':
        app = str(source[0].abspath)
        if os.spawnl(os.P_WAIT, app, app)==0:
            open(str(target[0]),'w').write("PASSED: "+source[0].path+"\n")
        else:
            open(str(target[0]),'w').write("FAILED: "+source[0].path+"\n")
            return 1

def preparePaths(env):
    # scons = env['scons']
    # bcp = env['bcp']
    # env = copy.deepcopy(env['bcp'])
    # env['bcp'] = bcp
    # env['scons'] = scons

    env['SNOCSCRIPT_PATH'] = os.path.abspath(os.path.dirname(env['SNOCSCRIPT']))

    env['BIN_DIR'] = os.path.join(env['SNOCSCRIPT_PATH'], env['CONFIGURATION'], 'bin')
    env['LIB_DIR'] = os.path.join(env['SNOCSCRIPT_PATH'], env['CONFIGURATION'], 'lib')
    env['scons'].AppendENVPath('LD_LIBRARY_PATH', env['LIB_DIR'])
    env['scons'].AppendENVPath('PATH', env['LIB_DIR'])

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
    print "  compiler={gcc,gpp,gppwarn,gppqt5,gppqt5warn,mingw,vc9,vc10,vc11,vc11exp}"
    print "  configuration={Debug,Release}"
    print "  platform={x86,Win32,x64} # Win32 is an alias to x86"
    print "  verbose=1 # enables scons debug output"
    print "  shared=1 | 0 #enables building shared libraries for all projects of default config"
    print "  testnorun=0 | 1 #disables tests run in case of test/install targets"
    print "  -r        # execute SNocscriptFilePath/SNocscript as Python script"
    print "  -h        # print this help"
    print "  -c        # execute cleaning"
    print "  -all      # execute for all dependent projects"
    print "**********************"
    print "Other options can be SCons specific."
    print "  If you want to change default path to the sources then"
    print "  set SNOCS_PROJECTS_SRC_PATH environment variable"
    print "  If you want to change default installation path then "
    print "  set SNOCS_INSTALL_LIB_PATH and SNOCS_INSTALL_BIN_PATH environment variables"
    print "  During 'test' phase snocs updates LD_LIBRARY_PATH local copy to provide"
    print "  of shared libraries"
    print "**********************"
    
