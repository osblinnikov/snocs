import os.path
import shutil
import copy
import sys
from colors import *

# from cogapp import Cog
join = os.path.join
#--------------------------------------
#      Functions
#--------------------------------------

def initEnv(env, name):
  # scons = env['scons']
  # bcp = env['bcp']
  # env = copy.deepcopy(env['bcp'])
  # env['bcp'] = bcp
  # env['scons'] = scons
  env['SNOCSCRIPT_PATH'] = os.path.abspath(os.path.dirname(env['SNOCSCRIPT']))
  env['PROG_NAME'] = name
  env['prj_env'] = env['scons'].Clone()
  return env

def DefaultParentConfig(env,c):
  testInclDeps(c)

  if env['SHARED'] == '1':
    initEnv(env, c['PROG_NAME'])
    c['depsDynamic'](env)
  else:
    initEnv(env, c['PROG_NAME']+"_static")
    c['depsStatic'](env)

def enableQtModules(env,c, doBuildUI):
  # addPaths = []
  if c.__contains__('qt5modules') and env['QT_TOOL']=='qt5':
    env['prj_env'][env['QT_DIR_NAME']] = env['QT_DIR']
    env['prj_env'].AppendENVPath('PKG_CONFIG_PATH', env['QT_PKG_CONFIG_PATH'])
    env['prj_env'].Tool(env['QT_TOOL'])
    env['prj_env'].EnableQt5Modules(c['qt5modules'])
    # addPaths = [os.path.abspath(os.path.join(env['QT_DIR'], 'include', x)) for x in c['qt5modules']]
    if doBuildUI:
      qtuisrc = []
      if c.__contains__('qt5ui'):
        qtuisrc = PrefixSources(env, '', c['qt5ui'])

      for s in qtuisrc:
        env['prj_env'].Uic5(s)

  if c.__contains__('qt4modules') and env['QT_TOOL']=='qt4':
    env['prj_env'][env['QT_DIR_NAME']] = env['QT_DIR']
    env['prj_env'].AppendENVPath('PKG_CONFIG_PATH', env['QT_PKG_CONFIG_PATH'])
    env['prj_env'].Tool(env['QT_TOOL'])
    env['prj_env'].EnableQt4Modules(c['qt4modules'])
    # addPaths = [os.path.abspath(os.path.join(env['QT_DIR'], 'include', x)) for x in c['qt4modules']]
    if doBuildUI:
      qtuisrc = []
      if c.__contains__('qt4ui'):
        qtuisrc = PrefixSources(env, '', c['qt4ui'])
      for s in qtuisrc:
        env['prj_env'].Uic4(s)
  # return addPaths

def funcInclDeps(env):
  return

def testInclDeps(c):
  if not c.__contains__('deps'):
    defInclDeps = funcInclDeps
  else:
    defInclDeps = c['deps']
  if not c.__contains__("depsStatic"):
    c['depsStatic'] = defInclDeps
  if not c.__contains__("depsStatic_tests"):
    c['depsStatic_tests'] = defInclDeps
  if not c.__contains__("depsStatic_run"):
    c['depsStatic_run'] = defInclDeps    
  if not c.__contains__("depsDynamic"):
    c['depsDynamic'] = defInclDeps
  if not c.__contains__("depsDynamic_tests"):
    c['depsDynamic_tests'] = defInclDeps
  if not c.__contains__("depsDynamic_run"):
    c['depsDynamic_run'] = defInclDeps

def DefaultLibraryConfig(env, c):
  forceShared = c.get('forceShared', False)
  forceStatic = c.get('forceStatic', False)
  runnableOnly = c.get('runnableOnly', False)

  LIB_DEFINES = []
  STATIC_DEFINES = []
  DepsFunc = ''

  SHARED_VAR_BCP = env['SHARED']
  if env['SHARED'] == '1' or (forceShared and (not forceStatic)):
    env['SHARED'] = '1' #TEMPORARILY REPLACE SHARED VARIABLE, WILL REPLCE BACK AT THE END OF THIS FUNCTION
    DepsFunc = 'Dynamic'
    LIB_DEFINES = [(c['PROG_NAME']+"_EXPORT").upper()]
  else:
    env['SHARED'] = '0'  #TEMPORARILY REPLACE SHARED VARIABLE, WILL REPLCE BACK AT THE END OF THIS FUNCTION
    DepsFunc = 'Static'
    STATIC_DEFINES = [(c['PROG_NAME']+"_STATIC").upper()]

  if not c.__contains__("CCFLAGS"):
    c['CCFLAGS'] = env['CCFLAGS']

  if not c.__contains__("CPPPATH"):
    c['CPPPATH'] = []
  c['CPPPATH'].append(env['SNOCSCRIPT_PATH'])

  if not c.__contains__("CPPDEFINES"):
    c['CPPDEFINES'] = []

  if c.__contains__("defines"):
    c['CPPDEFINES'] += c["defines"]

  if not c.__contains__("SRCPATH"):
    c["SRCPATH"] = "src"
  c["SRCPATH"] = os.path.join(*c["SRCPATH"].split("/"))

  if not c.__contains__("TESTPATH"):
    c["TESTPATH"] = "tests"
  c["TESTPATH"] = os.path.join(*c["TESTPATH"].split("/"))

  testInclDeps(c)

  if not c.__contains__("libFiles") or len(c['libFiles'])==0:
      c['libFiles'] = []
      srcFolder = os.path.join(env['SNOCSCRIPT_PATH'], c["SRCPATH"])
      for root, dirs, files in os.walk(srcFolder):
        if root.endswith('.tmp'):
          continue
        for fileName in files:
          if fileName == 'main.cpp' or fileName == 'main.c':
            continue
          if (len(fileName)>4 and fileName[-4:] == '.cpp') or (len(fileName)>2 and fileName[-2:] == '.c'):
            fileP = os.path.join(root,fileName)
            relativeFilePath =  fileP[(len(srcFolder)+1):]
            c['libFiles'].append(relativeFilePath)
            print("Discovered", relativeFilePath)

  #START!
  if not runnableOnly:
    initEnv(env, c['PROG_NAME'])

    enableQtModules(env,c,True)
    env['prj_env'].Append( 
      CPPPATH = c['CPPPATH'],
      CPPDEFINES = c['CPPDEFINES']+LIB_DEFINES+STATIC_DEFINES,
      CCFLAGS = c['CCFLAGS'] + c.get('CCFLAGSLib', [])
    )
    c['deps'+DepsFunc](env)
    
    if env['SHARED'] == '1':
      env['scons'].Default(PrefixSharedLibrary(env, c["SRCPATH"], c['libFiles']))
    else:
      env['scons'].Default(PrefixLibrary(env, c["SRCPATH"], c['libFiles']))

  if c.get('testFiles', False):
    #       STATIC TESTS
    initEnv(env, c['PROG_NAME']+"_test")

    enableQtModules(env,c,False)
    env['prj_env'].Append(
      CPPPATH = c['CPPPATH'],
      CPPDEFINES = c['CPPDEFINES']+STATIC_DEFINES,
      CCFLAGS = c['CCFLAGS'] + c.get('CCFLAGSTest', [])
    )
    if not runnableOnly:
      AddDependency(env, c['PROG_NAME'], env['SNOCSCRIPT_PATH'])

    c['deps'+DepsFunc+'_tests'](env)
    c['deps'+DepsFunc](env)
    
    env['scons'].Default(PrefixTest(env, c["TESTPATH"], c['testFiles']))

  if c.get('runFiles', False):
    #       SHARED RUN
    initEnv(env, c['PROG_NAME']+"_run")

    enableQtModules(env,c,False)
    env['prj_env'].Append(
      CPPPATH = c['CPPPATH'],
      CPPDEFINES = c['CPPDEFINES']+STATIC_DEFINES,
      CCFLAGS = c['CCFLAGS'] + c.get('CCFLAGSRun', [])
    )
    if not runnableOnly:
      AddDependency(env, c['PROG_NAME'], env['SNOCSCRIPT_PATH'])
    
    c['deps'+DepsFunc+'_run'](env)
    c['deps'+DepsFunc](env)
    
    env['scons'].Default(PrefixProgram(env, c["SRCPATH"], c['runFiles']))

  env['SHARED'] = SHARED_VAR_BCP

def isProjectDisabled(env):
  # print(env['WITHOUT'])
  for fltr in env['WITHOUT']:
    if len(fltr) == 0:
      return
    if env['PROG_NAME'].startswith(fltr):
      print("env['PROG_NAME']="+env['PROG_NAME']+" startswith "+fltr)
      return True
    if fltr.startswith("*") and (fltr in env['PROG_NAME']):
      print("fltr "+fltr+" in "+env['PROG_NAME'])
      return True
  return False


def EnsureCleanup(target, folder):
  from SCons.Script import Clean
  Clean(target, folder)


def EnsureEmptyFoldersCleanup(target, folder_trgt):
  anyfiles = False
  allempty_subfolders = []
  for root, dirs, files in os.walk(folder_trgt):
    anyfiles = anyfiles or len(files) > 0
    if len(files) == 0 and len(dirs) == 0:
      allempty_subfolders.append(root)
  if not anyfiles and os.path.isdir(folder_trgt):
    allempty_subfolders.append(folder_trgt)
  
  if allempty_subfolders:
    print("Empty subtree found, register for cleanup", allempty_subfolders)

  from SCons.Script import Clean
  for folder in allempty_subfolders:
    Clean(target, folder) 


def recursive_install(target, source, env):
    source_dirname = os.path.dirname(source)
    for root, dirnames, filenames in os.walk(source):
        for filename in filenames:
            yield env.Install(os.path.join(
                target, os.path.relpath(root, os.path.dirname(source))),
                os.path.join(root, filename))


def EnsureCopyOfHLSPrj(prg, folder_trgt, targetFullPathToBinDir, env, alias, prj_name):
  if env['CC'] != 'i++' or env['PLATFORM'] == 'x64':
    return
  prj_name = prj_name + ".prj" if prj_name and not prj_name.endswith(".prj") else prj_name
  prj_name = folder_trgt + prj_name if prj_name else None

  if not prj_name:
    for root, dirs, files in os.walk(folder_trgt):
        if root.endswith('.prj'):
          prj_name = os.path.split(root)[1]
          break
  if not prj_name:
    return

  src = os.path.join(folder_trgt, prj_name)
  
  for t in recursive_install(targetFullPathToBinDir, src, env['prj_env']):
    env[alias].append(t)

  from SCons.Script import Clean
  Clean(prg, src)


def PrefixProgram(env, folder, srcs, c=None):
  if isProjectDisabled(env):
    return
  c = c if c else {}
  abs_script_path = os.path.abspath(env['SNOCSCRIPT_PATH'])
  
  trgt = env['PROG_NAME']
  if env['SHARED'] == '0':
    trgt = trgt + '_static'

  targetWithArch = trgt + env['ARCHITECTURE_CODE']    
  targetFullPath = os.path.join(env['SNOCSCRIPT_PATH'], targetWithArch)
  targetFullPathToBinDir = os.path.join(env['BIN_DIR'], targetWithArch)
  targetFullPathToBinFile = os.path.join(targetFullPathToBinDir, trgt)
  targetFullPathToInstall = os.path.join(env['INSTALL_BIN_PATH'], targetWithArch)
  
  folder_trgt = os.path.join(abs_script_path, 'build', targetWithArch+"_"+env['CONFIGURATION']+'.tmp', folder)
  folder = os.path.join(abs_script_path, folder)
  env['prj_env'].VariantDir(folder_trgt, folder, duplicate=0)
  
  srcs = PrefixSources(env, folder_trgt, srcs)
  linkom = []
  if env['MSVC_VERSION'] != None and float(env['MSVC_VERSION'].translate(None, 'Exp')) < 11:
    linkom = ['mt.exe -nologo -manifest ${TARGET}.manifest -outputresource:$TARGET;1']
  if env['MSVC_PDB']:
    env['prj_env'].Append(PDB = targetFullPathToBinFile+ '.pdb')
  
  # print(srcs)
  prg = env['APP_BUILD'][targetFullPath] = env['prj_env'].Program(
    target = targetFullPathToBinFile, 
    source = srcs, 
    LINKCOM  = [env['prj_env']['LINKCOM']]+linkom
  )
  EnsureCopyOfHLSPrj(prg, folder_trgt, targetFullPathToInstall, env, 'INSTALL_ALIASES', c.get('MAIN_HLS_PROJECT_NAME', False))
  env['INSTALL_ALIASES'].append(env['prj_env'].Install(targetFullPathToInstall, env['APP_BUILD'][targetFullPath]))#setup install directory

  EnsureCleanup(prg, targetFullPathToBinDir)
  EnsureCleanup(prg, targetFullPathToInstall)
  EnsureEmptyFoldersCleanup(prg, os.path.split(env['BIN_DIR'])[0])
  EnsureEmptyFoldersCleanup(prg, os.path.split(env['INSTALL_BIN_PATH'])[0])
  EnsureEmptyFoldersCleanup(prg, os.path.join(abs_script_path, 'build'))

  return env['APP_BUILD'][targetFullPath]

def PrefixTest(env, folder, srcs, c=None):
  if isProjectDisabled(env):
    return
  c = c if c else {}

  abs_script_path = os.path.abspath(env['SNOCSCRIPT_PATH'])
  
  trgt = env['PROG_NAME']
  if env['SHARED'] == '0':
    trgt = trgt + '_static'

  targetWithArch = trgt + env['ARCHITECTURE_CODE']    
  targetFullPath = os.path.join(env['SNOCSCRIPT_PATH'], targetWithArch)
  targetFullPathToBinDir = os.path.join(env['BIN_DIR'], targetWithArch)
  targetFullPathToBinFile = os.path.join(targetFullPathToBinDir, trgt)
  targetFullPathToInstall = os.path.join(env['INSTALL_BIN_PATH'], targetWithArch)
  testPassedFullPath = targetFullPathToBinFile + ".passed"

  folder_trgt = os.path.join(abs_script_path, 'build', targetWithArch+"_"+env['CONFIGURATION']+'.tmp', folder)
  folder = os.path.join(abs_script_path, folder)
  env['prj_env'].VariantDir(folder_trgt, folder, duplicate=0)

  srcs = PrefixSources(env, folder_trgt, srcs)
  linkom = []
  if env['MSVC_VERSION'] != None and float(env['MSVC_VERSION'].translate(None, 'Exp')) < 11:
    linkom = ['mt.exe -nologo -manifest ${TARGET}.manifest -outputresource:$TARGET;1']
  if env['MSVC_PDB']:
    env['prj_env'].Append(PDB = targetFullPathToBinFile + '.pdb' )

  prg = env['APP_BUILD'][targetFullPath] = env['prj_env'].Program(target = targetFullPathToBinFile, source = srcs, LINKCOM  = [env['prj_env']['LINKCOM']]+linkom)
  EnsureCopyOfHLSPrj(prg, folder_trgt, targetFullPathToInstall, env, 'INSTALL_ALIASES', c.get('TEST_HLS_PROJECT_NAME', False))
  env['INSTALL_ALIASES'].append(env['prj_env'].Install(targetFullPathToInstall, env['APP_BUILD'][targetFullPath]))#setup install directory

  EnsureCopyOfHLSPrj(prg, folder_trgt, targetFullPathToBinDir, env, 'TEST_ALIASES', c.get('TEST_HLS_PROJECT_NAME', False))
  env['TEST_ALIASES'].append(env['prj_env'].Test(testPassedFullPath, env['APP_BUILD'][targetFullPath]))

  EnsureCleanup(prg, targetFullPathToBinDir)
  EnsureCleanup(prg, targetFullPathToInstall)

  EnsureEmptyFoldersCleanup(prg, os.path.split(env['BIN_DIR'])[0])

  return env['APP_BUILD'][targetFullPath]

# Similar to PrefixProgram above, except for Library
def PrefixLibrary(env, folder, srcs):
  if isProjectDisabled(env):
    return
  abs_script_path = os.path.abspath(env['SNOCSCRIPT_PATH'])
  
  trgt = env['PROG_NAME']
  if env['SHARED'] == '0':
    trgt = trgt + '_static'
  folder_trgt = os.path.join(abs_script_path, 'build', trgt+env['ARCHITECTURE_CODE']+"_"+env['CONFIGURATION']+'.tmp', folder)
  folder = os.path.join(abs_script_path, folder)
  env['prj_env'].VariantDir(folder_trgt, folder, duplicate=0)
  
  srcs = PrefixSources(env, folder_trgt, srcs)
  if env['MSVC_PDB']:
    env['prj_env'].Append(PDB = os.path.join( env['LIB_DIR'], trgt+env['ARCHITECTURE_CODE'] + '.pdb' ))
  targetFullPath = os.path.join(env['SNOCSCRIPT_PATH'],trgt+env['ARCHITECTURE_CODE'])
  targetFullPathToBin = os.path.join(env['LIB_DIR'],trgt+env['ARCHITECTURE_CODE'])
  env['APP_BUILD'][targetFullPath] = env['prj_env'].Library(target = targetFullPathToBin, source = srcs)
  env['INSTALL_ALIASES'].append(env['prj_env'].Install(env['INSTALL_LIB_PATH'], env['APP_BUILD'][targetFullPath]))#setup install directory
  return env['APP_BUILD'][targetFullPath]
  
# Similar to PrefixProgram above, except for SharedLibrary
def PrefixSharedLibrary(env, folder, srcs):
  if isProjectDisabled(env):
    return
  abs_script_path = os.path.abspath(env['SNOCSCRIPT_PATH'])
  
  trgt = env['PROG_NAME']
  if env['SHARED'] == '0':
    trgt = trgt + '_static'
  folder_trgt = os.path.join(abs_script_path, 'build', trgt+env['ARCHITECTURE_CODE']+"_"+env['CONFIGURATION']+'.tmp', folder)
  folder = os.path.join(abs_script_path, folder)
  env['prj_env'].VariantDir(folder_trgt, folder, duplicate=0)
  
  srcs = PrefixSources(env, folder_trgt, srcs)
  linkom = []
  if env['MSVC_VERSION'] != None and float(env['MSVC_VERSION'].translate(None, 'Exp')) < 11:
    linkom = ['mt.exe -nologo -manifest ${TARGET}.manifest -outputresource:$TARGET;2']
  if env['MSVC_PDB']:
    env['prj_env'].Append(PDB = os.path.join( env['LIB_DIR'], trgt+env['ARCHITECTURE_CODE'] + '.pdb' ))
  targetFullPath = os.path.join(env['SNOCSCRIPT_PATH'],trgt+env['ARCHITECTURE_CODE'])
  targetFullPathToBin = os.path.join(env['LIB_DIR'],trgt+env['ARCHITECTURE_CODE'])
  env['APP_BUILD'][targetFullPath] = env['prj_env'].SharedLibrary(target = targetFullPathToBin, source = srcs, LINKCOM  = [env['prj_env']['LINKCOM']]+linkom) 
  env['INSTALL_ALIASES'].append(env['prj_env'].Install(env['INSTALL_LIB_PATH'], env['APP_BUILD'][targetFullPath]))#setup install directory
  return env['APP_BUILD'][targetFullPath]

def PrefixFilename(filename, extensions):
  return [(filename + ext) for ext in extensions]

# Prefix the source files names with the source directory
def PrefixSources(env, srcdir, srcs):
  out = []
  for x in srcs:
    if isinstance(x, str):
      if x.startswith("../"):
        p = os.path.join(env['SNOCSCRIPT_PATH'], x[3:])
      elif x.startswith("./"):
        p = os.path.join(env['SNOCSCRIPT_PATH'], x[2:])
      else:
        p = os.path.join(env['SNOCSCRIPT_PATH'],srcdir, x)

      out.append(os.path.abspath(p))
    else:
      out.append(x)
  return out
  #return  [os.path.abspath(os.path.join(env['SNOCSCRIPT_PATH'],srcdir, x)) for x in srcs]

def AddDependencyConfig(env, dep, deppath, ccflags=None, linkflags=None):
  if deppath == None:
    deppath = '.'
  definesVar = []
  if env['SHARED'] == '0':
    definesVar = [dep.upper()]
  # print("CPPPATH+ "+deppath)
  env['prj_env'].Append(
    LIBPATH = [os.path.join(deppath,env['CONFIGURATION'],'lib')],
    LIBS = [dep+env['ARCHITECTURE_CODE']],
    LINKFLAGS = (linkflags if linkflags else []),
    CPPPATH = [deppath],
    CPPDEFINES = definesVar,
    CCFLAGS = (ccflags if ccflags else [])
  )

def AddDependency(env, dep, deppath):
  if env['SHARED'] == '0':
    dep = dep + '_static'
  deppath = os.path.abspath(os.path.join(env['PROJECTS_SRC_PATH'],deppath))
  AddOrdering(env,dep,deppath)
  AddDependencyConfig(env,dep, deppath)
  
def AddOrdering(env, dep, deppath):
  prog = env['PROG_NAME']
  if env['SHARED'] == '0':
    prog = prog + '_static'
  #print(prog+"->"+dep)
  prog = os.path.join(env['SNOCSCRIPT_PATH'],prog+env['ARCHITECTURE_CODE'])
  if env['APP_DEPENDENCIES'].get(prog) == None:
    env['APP_DEPENDENCIES'][prog] = [];
  depFullPath = os.path.join(deppath,dep+env['ARCHITECTURE_CODE'])
  env['APP_DEPENDENCIES'][prog].append(depFullPath)
  if deppath != env['SNOCSCRIPT_PATH']:
    if env.get('CROSSPROJECT_DEPENDENCIES') == None:
      env['CROSSPROJECT_DEPENDENCIES'] = {};
    if env['CROSSPROJECT_DEPENDENCIES'].get(deppath) == None:
      env['CROSSPROJECT_DEPENDENCIES'][deppath] = dep
      
def AddScript(env, dep, deppath):
  if deppath != env['SNOCSCRIPT_PATH']:
    if env.get('CROSSPROJECT_DEPENDENCIES') == None:
      env['CROSSPROJECT_DEPENDENCIES'] = {};
    if env['CROSSPROJECT_DEPENDENCIES'].get(deppath) == None:
      env['CROSSPROJECT_DEPENDENCIES'][deppath] = dep
      
def AddPthreads(env):
  PATH_TO_PTHREADS_WIN = os.path.join(env['PROJECTS_SRC_PATH'],'sourceware.org','pthreads-win32','dll-latest')
  if env['MSVC_VERSION'] != None:
    env['prj_env'].Append(
      LIBS = ['pthreadVC2'],
      CPPPATH = [os.path.join(PATH_TO_PTHREADS_WIN,'include')],
      LIBPATH = [os.path.join(PATH_TO_PTHREADS_WIN,'lib',env['PLATFORM'])]
    )
    env['prj_env'].AppendENVPath('PATH', os.path.join(PATH_TO_PTHREADS_WIN,'dll',env['PLATFORM']))
  elif env['COMPILER'] == 'mingw':
    env['prj_env'].Append(
      LIBS = ['pthreadGC2'],
      CPPPATH = [os.path.join(PATH_TO_PTHREADS_WIN,'include')],
      LIBPATH = [os.path.join(PATH_TO_PTHREADS_WIN,'lib',env['PLATFORM'])]
    )
    env['prj_env'].AppendENVPath('PATH', os.path.join(PATH_TO_PTHREADS_WIN,'dll',env['PLATFORM']))
  elif not env.__contains__('LINK'):
    env['prj_env'].Append(
      # LIBS = ['pthread'],
      LINKFLAGS = ['-pthread']
    )

def AddNetwork(env):
  if env['MSVC_VERSION'] != None:
    env['prj_env'].Append(LIBS = ['WSock32'])
  elif env['COMPILER'] == 'mingw':
    env['prj_env'].Append(LIBS = ['ws2_32', 'IPHLPAPI'])

def AddOpenGL(env):
  if env['MSVC_VERSION'] != None:
    print("OpenGL for MSVC is not implemented yet in snocs")
  elif env['COMPILER'] == 'mingw':
    print("OpenGL for mingw is not implemented yet in snocs")
  else:
    env['prj_env'].Append(
      LIBS = ['GL'],
      # LINKFLAGS = ['-GL']
    )
