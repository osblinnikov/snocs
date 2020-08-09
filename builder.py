import os.path
import os
import sys
import copy

from ipp import *
from gpp import *
from gcc import *
from mingw import *
from default import *
from vc9 import *
from clangpp import *

import platform

#PLEASE change it if you don't want the standard snocs location
PROJECTS_SRC_PATH = os.getenv('SNOCS_PROJECTS_SRC_PATH', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

if platform.system() == 'Linux':
    RED='\033[0;31m'
    GREEN='\033[1;32m'
    DGREEN='\033[0;32m'
    NOCOLOR='\033[0m'
else:
    DGREEN=NOCOLOR=GREEN=RED=''
def detectQtDir(platform,QTVER):
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
      print(RED+"builder.detectQtDir(): QTDIR env variable is not set and OS "+sys.platform+" is unknown"+NOCOLOR)
  if QTDIR.startswith("~"):
    QTDIR = os.path.expanduser(QTDIR)
  if not os.path.exists(QTDIR):
    print(RED+'builder.detectQtDir(): QTDIR='+QTDIR+" not exists"+NOCOLOR)
    sys.exit(1)
  return QTDIR



def prepare_env(ARGUMENTS, ARGLIST):
    #--------command line arguments------------
    env = {}
    for k,v in ARGUMENTS.items():
        env[k.upper()] = v

    #init defaults
    env['SHARED'] = ARGUMENTS.get('shared', '0')
    env['VERBOSE'] = ARGUMENTS.get('verbose', '0')
    env['CLEANING'] = ARGUMENTS.get('cleaning', '0')
    env['BUILD_ALL'] = ARGUMENTS.get('build_all', '0')
    env['TESTNORUN'] = ARGUMENTS.get('testnorun', '0')
    env['SNOCSCRIPT'] = ARGUMENTS.get('snocscript', None)
    env['CONFIGURATION'] = ARGUMENTS.get('configuration', 'Release')
    env['COMPILER'] = ARGUMENTS.get('compiler', 'gcc')
    env['PLATFORM'] = ARGUMENTS.get('platform', 'x86')
    env['LINKER'] = ARGUMENTS.get('linker', 'ld')
    env['WITHOUT'] = findArgs(ARGLIST,'without')

    if env['SNOCSCRIPT'] == None or env['SNOCSCRIPT']=="":
        print(RED+"SNocscript is not specified!"+NOCOLOR)
        exit()
    
    if env['CONFIGURATION'].lower() == 'debug'.lower():
        env['CONFIGURATION'] = 'Debug'
    else:
        env['CONFIGURATION'] = 'Release'
    
    if env['PLATFORM'].lower() == 'Win32'.lower():
        env['PLATFORM'] = 'x86'


    #--------deploy parameters--------
    env['INSTALL_BIN_PATH'] = os.getenv('SNOCS_INSTALL_BIN_PATH', os.path.abspath(os.path.join(PROJECTS_SRC_PATH,'build','bin')))
    env['INSTALL_LIB_PATH'] = os.getenv('SNOCS_INSTALL_LIB_PATH', os.path.abspath(os.path.join(PROJECTS_SRC_PATH,'build','lib')))
    env['INSTALL_INC_PATH'] = os.getenv('SNOCS_INSTALL_INC_PATH', os.path.abspath(os.path.join(PROJECTS_SRC_PATH,'build','include')))
    env['PROJECTS_SRC_PATH'] = PROJECTS_SRC_PATH
    env['INSTALL_ALIASES'] = [] #here will be the targets for install alias
    env['TEST_ALIASES'] = [] #here will be the targets for test alias
    env['ARCHITECTURE_CODE'] = '_'+os.path.split(env['COMPILER'])[-1].split(".")[0]+'_'+env['PLATFORM']
    #---------init params-----------
    env['MSVC_PDB'] = 0
    env['MSVC_VERSION'] = None
    env['APP_DEPENDENCIES'] = {}
    env['APP_BUILD'] = {}
    env['TOOLS'] = 'default'
    env['LINKFLAGS'] = []
    env['CCFLAGS'] = []
    env['CPPFLAGS'] = []
    env['CXXFLAGS'] = []
    env['LIBS'] = []
    env['LIBPATH']=[
        env['INSTALL_LIB_PATH']
    ]
    env['LD_LIBRARY_PATH'] = []
    env['CPPPATH'] = [
        env['PROJECTS_SRC_PATH'],
        env['INSTALL_INC_PATH']
    ]
    env['CPPDEFINES'] = []
    if env['CONFIGURATION'] == 'Debug':
        env['CPPDEFINES'].extend(['_DEBUG'])
    else:
        env['CPPDEFINES'].extend(['NDEBUG'])

    env['QTVER'] = os.environ.get("QTVER", False)
    if env['QTVER'] != False:
        if env['QTVER'].startswith('5'):
          env['QT_DIR_NAME'] = 'QT5DIR'
          env['QT_TOOL'] = 'qt5'
        elif env['QTVER'].startswith('4'):
          env['QT_DIR_NAME'] = 'QT4DIR'
          env['QT_TOOL'] = 'qt4'
        else:
          print(RED+'Unknown QTVER '+env['QTVER']+" only started with 4 or 5 is allowed"+NOCOLOR)
          sys.exit(1)
        env['QT_DIR'] = detectQtDir(env['PLATFORM'],env['QTVER'])
        env['QT_PKG_CONFIG_PATH'] = os.path.join(env['QT_DIR'], 'lib/pkgconfig')


    #--------SWITCHING COMPILER------
    if env['COMPILER'] == 'default':
        print("WARNING: compiler was not specified, using default parameters")
        env = prepare_default(env)
    elif env['COMPILER'] == 'ipp':
        env = prepare_ipp(env)
    elif env['COMPILER'] == 'gpp':
        env = prepare_gpp(env)
    elif env['COMPILER'] == 'gcc':
        env = prepare_gcc(env)
    elif env['COMPILER'] == 'clangpp':
        env = prepare_clangpp(env)
    elif env['COMPILER'] == 'mingw':
        env = prepare_mingw(env)
    elif env['COMPILER'].startswith('vc'):
        env = prepare_vc9(env)
        compiler = env['COMPILER'][2:].lower() # skip vc
        if compiler.endswith('exp'):
            Exp = 'Exp'
        else:
            Exp = ''
        compiler = compiler.replace('exp','')
        env['MSVC_VERSION'] = compiler+'.0'+Exp
    else:
        print(DGREEN+"---Custom---"+NOCOLOR)
        env['TOOLS'] = ['default']
        env['CC'] = env['COMPILER']
        env['LINK'] = env['LINKER']
        print(DGREEN+"compiler: "+env['CC']+NOCOLOR)
        print(DGREEN+"linker: "+env['LINK']+NOCOLOR)

    if env.__contains__("COMPILER_PATH"):
        print(DGREEN+"Will use provided COMPILER_PATH="+env["COMPILER_PATH"]+NOCOLOR)
        env['CC'] = env["COMPILER_PATH"]
    if env.__contains__("LINKER_PATH"):
        print(DGREEN+"Will use provided LINKER_PATH="+env["LINKER_PATH"]+NOCOLOR)
        env['LINK'] = env["LINKER_PATH"]
    if env.__contains__("ARCHIEVER_PATH"):
        print(DGREEN+"Will use provided ARCHIEVER_PATH="+env["ARCHIEVER_PATH"]+NOCOLOR)
        env['AR'] = env["ARCHIEVER_PATH"]
    if env.__contains__("RANLIB_PATH"):
        print(DGREEN+"Will use provided RUNLIB_PATH="+env["RANLIB_PATH"]+NOCOLOR)
        env['RANLIB'] = env["RANLIB_PATH"]        
    env['CPPPATH'].extend(findArgs(ARGLIST,'cpppath'))
    env['CPPDEFINES'].extend(findArgs(ARGLIST,'define'))
    env['CCFLAGS'].extend(findArgs(ARGLIST,'cflag'))
    env['CXXFLAGS'].extend(findArgs(ARGLIST,'cxxflag'))
    env['CPPFLAGS'].extend(findArgs(ARGLIST,'cppflag'))
    env['LINKFLAGS'].extend(findArgs(ARGLIST,'lflag'))
    env['LIBPATH'].extend(findArgs(ARGLIST,'libpath'))
    env['LIBS'].extend(findArgs(ARGLIST,'lib'))
    env['LD_LIBRARY_PATH'].extend(findArgs(ARGLIST,'ld_library_path'))
    env['bcp'] = copy.deepcopy(env)

    return env

def findArgs(ARGLIST, argName):
    l = []
    for key, value in ARGLIST:
        if key.lower() == argName.lower():
            l.append(value)
    if len(l) > 0:
        print(argName+"s:")
        print(l)
    return l

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
    print("""**********************
Snocs is a build tool based on SCons Software Construction tool (http://www.scons.org/).
Usage: snocs [SNocscriptFilePath] [options]
    print("Examples:
  snocs .. compiler=vc9 platform=x86 configuration=Debug
  snocs test -Q           #build and run tests with reduced log
  snocs install -c        #clean installation
  snocs icanchangethisdomain/SomeProjectName -r  #run Python script
SNocscriptFilePath can be absolute, relative to current path, or
relative to projects root path e.g.:
  snocs example compiler=vc9 test
**********************
Available options:
  compiler={gcc,gpp,mingw,clangpp,vc9,vc9exp,vc10,vc10exp,vc11,vc11exp,ipp}
  configuration={Debug,Release}
  platform={x86,Win32,x64} # Win32 is an alias to x86
  verbose=0|1|2 # enables scons debug output
  shared=1|0 #enables building shared libraries for all projects of default config
  testnorun=0|1 #disables tests run in case of test/install targets
  -r        # execute SNocscriptFilePath/SNocscript as Python script
  -h        # print(this help
  -c        # execute cleaning
  -all      # execute for all dependent projects
  --more-warnings or more-warnings=1 # show as many warnings as possible
  --warnings-as-errors or warnings-as-errors=1 # treat warns as errors
  --no-PROJECT1_PREFIX or without=PROJECT1_PREFIX without=PROJECT2_PREFIX # disable projects compilation
        PROJECT1_PREFIX must match to the begining of the project name.
        PREFIX can start with *, it means that the name should contain this PREFIX
  compiler_path=FULL_PATH_TO_THE_COMPILER
  linker_path=FULL_PATH_TO_THE_LINKER
  cpppath=PATH_TO_INCLUDES1 cpppath=PATH_TO_INCLUDES2
  define="DEFINITION1=100" define=DEFINE2
  libpath=PATH_TO_LIBRARIES
  lib=ADDITIONAL_LIBRARY_NAME
  cflag=FLAG1 cxxflag=FLAG2 cppflag=FLAG3 #Compile flags
  lflag=FLAG1 lflag=FLAG2   lflag=FLAG3   #Link flags
  ld_library_path=/some/path/to/dynamic/lib  ld_library_path=/another/path
**********************"
Other options can be SCons specific.
  If you want to change default path to the sources then
  set SNOCS_PROJECTS_SRC_PATH environment variable
  If you want to change default installation path then
  set SNOCS_INSTALL_LIB_PATH and SNOCS_INSTALL_BIN_PATH environment variables
  During 'test' phase snocs updates LD_LIBRARY_PATH local copy to provide
  of shared libraries"
**********************""")
    
