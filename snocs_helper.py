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
  c['PROG_NAME'] = 'lib' + c['PROG_NAME']
  testInclDeps(c)

  initEnv(env, c['PROG_NAME'])
  if env['SHARED'] == '1':
    c['depsDynamic'](env)
  else:
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
  c['PROG_NAME'] = 'lib' + c['PROG_NAME']
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
    
    env['scons'].Default(PrefixTest(env, c["TESTPATH"], c['testFiles'], c))

  if c.get('runFiles', False):
    #       SHARED RUN
    initEnv(env, c['PROG_NAME'][3:])

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
    
    env['scons'].Default(PrefixProgram(env, c["SRCPATH"], c['runFiles'], c))

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


def EnsureCleanup(env, target, folder):
  env['prj_env'].Clean(target, folder)


def EnsureEmptyFoldersCleanup(env, target, folder_trgt):
  anyfiles = False
  allempty_subfolders = []
  for root, dirs, files in os.walk(folder_trgt):
    anyfiles = anyfiles or len(files) > 0
    if len(files) == 0 and len(dirs) == 0:
      allempty_subfolders.append(root)
  if not anyfiles and os.path.isdir(folder_trgt):
    allempty_subfolders.append(folder_trgt)
    import shutil
    shutil.rmtree(folder_trgt)
  
  if allempty_subfolders:
    print("Empty subtree found, register for cleanup", DGREEN, allempty_subfolders, NOCOLOR)

  for folder in allempty_subfolders:
    env['prj_env'].Clean(target, folder) 


def recursive_install(target, source, env):
    source_dirname = os.path.dirname(source)
    for root, dirnames, filenames in os.walk(source):
        for filename in filenames:
            yield env.Install(os.path.join(
                target, os.path.relpath(root, os.path.dirname(source))),
                os.path.join(root, filename))


def EnsureCopyOfHLSPrj(prg, targetFullPathToBinFile, folder_trgt, targetFullPathToBinDir, env, alias, prj_name):
  if env['CC'] != 'i++' or env['PLATFORM'] == 'x64':
    return
  prj_name = prj_name + ".prj" if prj_name and not prj_name.endswith(".prj") else prj_name
  prj_name = os.path.join(folder_trgt, prj_name) if prj_name else None

  if not prj_name:
    for root, dirs, files in os.walk(folder_trgt):
        if root.endswith('.prj'):
          prj_name = os.path.split(root)[1]
          break
  if not prj_name:
    return

  src = prj_name
  # if not os.path.isdir(src):
  #   copyDirAction = env['prj_env'].CopyDirectory(targetFullPathToBinDir, src)
  #   # env[alias].append(copyDirAction)
  #   env['prj_env'].AddPreAction(prg, copyDirAction)
    
  # else:
  # print(RED, alias, targetFullPathToBinDir, src, NOCOLOR)
  for t in recursive_install(targetFullPathToBinDir, src, env['prj_env']):
    env[alias].append(t)
    env['prj_env'].Requires(prg, t)

  return src


def PrefixProgram(env, folder, srcs, c=None):
  if isProjectDisabled(env):
    return
  c = c if c else {}
  abs_script_path = os.path.abspath(env['SNOCSCRIPT_PATH'])
  
  static_target = 'shared' if env['SHARED'] == '1' else 'static'
  trgt = env['PROG_NAME']
  targetWithArch = static_target + env['ARCHITECTURE_CODE']    
  targetFullPath = os.path.join(env['SNOCSCRIPT_PATH'], targetWithArch)
  targetFullPathToBinDir = os.path.join(env['BIN_DIR'], targetWithArch)
  targetFullPathToBinFile = os.path.join(targetFullPathToBinDir, trgt)
  targetFullPathToInstall = os.path.join(env['INSTALL_BIN_PATH'], targetWithArch)
  
  folder_trgt = os.path.join(abs_script_path, 'build', targetWithArch + "_" + env['CONFIGURATION']+'.tmp', folder)
  folder = os.path.join(abs_script_path, folder)
  env['prj_env'].VariantDir(folder_trgt, folder, duplicate=0)
  
  srcs = PrefixSources(env, folder_trgt, srcs)
  linkom = []
  if env['MSVC_VERSION'] != None and float(env['MSVC_VERSION'].translate(None, 'Exp')) < 11:
    linkom = ['mt.exe -nologo -manifest ${TARGET}.manifest -outputresource:$TARGET;1']
  if env['MSVC_PDB']:
    env['prj_env'].Append(PDB = targetFullPathToBinFile+ '.pdb')
  
  # print(srcs)
  prg = env['prj_env'].Program(
    target = targetFullPathToBinFile, 
    source = srcs, 
    LINKCOM  = [env['prj_env']['LINKCOM']]+linkom
  )

  install_target = env['prj_env'].Install(targetFullPathToInstall, prg)
  hls_src = EnsureCopyOfHLSPrj(install_target, targetFullPathToBinFile, folder_trgt, targetFullPathToInstall, env, 'INSTALL_ALIASES', c.get('MAIN_HLS_PROJECT_NAME', False))
  env['INSTALL_ALIASES'].append(install_target)#setup install directory

  if env['CLEANING']:
    EnsureCleanup(env, prg, hls_src)
    EnsureCleanup(env, prg, targetFullPathToBinDir)
    EnsureCleanup(env, prg, targetFullPathToInstall)
    EnsureEmptyFoldersCleanup(env, prg, os.path.split(env['BIN_DIR'])[0])
    EnsureEmptyFoldersCleanup(env, install_target, os.path.split(env['INSTALL_BIN_PATH'])[0])
    EnsureEmptyFoldersCleanup(env, prg, os.path.join(abs_script_path, 'build'))
  env['APP_BUILD'][targetFullPath] = prg
  return prg

def PrefixTest(env, folder, srcs, c=None):
  if isProjectDisabled(env):
    return
  c = c if c else {}

  abs_script_path = os.path.abspath(env['SNOCSCRIPT_PATH'])
  
  static_target = 'shared' if env['SHARED'] == '1' else 'static'
  trgt = env['PROG_NAME']
  targetWithArch = static_target + env['ARCHITECTURE_CODE']

  targetFullPath = os.path.join(env['SNOCSCRIPT_PATH'], targetWithArch)
  targetFullPathToBinDir = os.path.join(env['BIN_DIR'], targetWithArch)
  targetFullPathToBinFile = os.path.join(targetFullPathToBinDir, trgt)
  targetFullPathToInstall = os.path.join(env['INSTALL_BIN_PATH'], targetWithArch, '')
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

  prg = env['prj_env'].Program(target = targetFullPathToBinFile, source = srcs, LINKCOM  = [env['prj_env']['LINKCOM']]+linkom)
  test_target = env['prj_env'].Test(testPassedFullPath, prg)
  install_target = env['prj_env'].Install(targetFullPathToInstall, prg)

  env['INSTALL_ALIASES'].append(install_target)#setup install directory
  env['TEST_ALIASES'].append(test_target)

  hls_src2 = EnsureCopyOfHLSPrj(test_target, targetFullPathToBinFile, folder_trgt, targetFullPathToBinDir, env, 'TEST_ALIASES', c.get('TEST_HLS_PROJECT_NAME', False))
  hls_src1 = EnsureCopyOfHLSPrj(install_target, targetFullPathToBinFile, folder_trgt, targetFullPathToInstall, env, 'INSTALL_ALIASES', c.get('TEST_HLS_PROJECT_NAME', False))

  if env['CLEANING']:
    EnsureCleanup(env, prg, hls_src1)
    EnsureCleanup(env, prg, hls_src2)
    EnsureCleanup(env, prg, targetFullPathToBinDir)
    EnsureCleanup(env, prg, targetFullPathToInstall)
    EnsureEmptyFoldersCleanup(env, prg, os.path.split(env['BIN_DIR'])[0])
  env['APP_BUILD'][targetFullPath] = prg
  return prg

# Similar to PrefixProgram above, except for Library
def PrefixLibrary(env, folder, srcs):
  if isProjectDisabled(env):
    return
  abs_script_path = os.path.abspath(env['SNOCSCRIPT_PATH'])
  
  static_target = 'shared' if env['SHARED'] == '1' else 'static'
  trgt = env['PROG_NAME']
  targetWithArch = static_target + env['ARCHITECTURE_CODE']

  folder_trgt = os.path.join(abs_script_path, 'build', targetWithArch+"_"+env['CONFIGURATION']+'.tmp', folder)
  folder = os.path.join(abs_script_path, folder)
  env['prj_env'].VariantDir(folder_trgt, folder, duplicate=0)
  
  srcs = PrefixSources(env, folder_trgt, srcs)
  if env['MSVC_PDB']:
    env['prj_env'].Append(PDB = os.path.join( env['LIB_DIR'], trgt+env['ARCHITECTURE_CODE'] + '.pdb' ))
  targetFullPath = os.path.join(env['SNOCSCRIPT_PATH'],trgt+env['ARCHITECTURE_CODE'])
  targetFullPathToBin = os.path.join(env['LIB_DIR'],trgt+env['ARCHITECTURE_CODE'])
  prg = env['prj_env'].Library(target = targetFullPathToBin, source = srcs)
  env['INSTALL_ALIASES'].append(env['prj_env'].Install(env['INSTALL_LIB_PATH'], prg))#setup install directory
  env['APP_BUILD'][targetFullPath] = prg
  return prg
  
# Similar to PrefixProgram above, except for SharedLibrary
def PrefixSharedLibrary(env, folder, srcs):
  if isProjectDisabled(env):
    return
  abs_script_path = os.path.abspath(env['SNOCSCRIPT_PATH'])
  
  static_target = 'shared' if env['SHARED'] == '1' else 'static'
  trgt = env['PROG_NAME']
  targetWithArch = static_target + env['ARCHITECTURE_CODE']

  folder_trgt = os.path.join(abs_script_path, 'build', targetWithArch+"_"+env['CONFIGURATION']+'.tmp', folder)
  folder = os.path.join(abs_script_path, folder)
  env['prj_env'].VariantDir(folder_trgt, folder, duplicate=0)
  
  srcs = PrefixSources(env, folder_trgt, srcs)
  linkom = [env['prj_env']['LINKCOM']]
  if env['MSVC_VERSION'] != None and float(env['MSVC_VERSION'].translate(None, 'Exp')) < 11:
    linkom = ['mt.exe -nologo -manifest ${TARGET}.manifest -outputresource:$TARGET;2']
  
  if env['MSVC_PDB']:
    env['prj_env'].Append(PDB = os.path.join( env['LIB_DIR'], trgt+env['ARCHITECTURE_CODE'] + '.pdb' ))
  
  if env['CC'] == 'i++':
    env['prj_env']['CC'] = 'g++'
    env['prj_env']['CCFLAGS'] = list(filter(lambda s:  '-march' not in s and '-g0' not in s, env['prj_env']['CCFLAGS']))
    if env['CONFIGURATION'] == 'Debug':
        env['CPPFLAGS'].extend(['-g'])
    env['prj_env']['LINKFLAGS'] = list(filter(lambda s: '-march' not in s, env['prj_env']['LINKFLAGS']))
    env['prj_env']['CPPDEFINES'] = list(filter(lambda s: 'WITH_INTEL_HLS' not in s, env['prj_env']['CPPDEFINES']))

  targetFullPath = os.path.join(env['SNOCSCRIPT_PATH'],trgt+env['ARCHITECTURE_CODE'])
  targetFullPathToBin = os.path.join(env['LIB_DIR'],trgt+env['ARCHITECTURE_CODE'])
  env['APP_BUILD'][targetFullPath] = env['prj_env'].SharedLibrary(target = targetFullPathToBin, source = srcs, LINKCOM  = linkom) 
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
      elif x.startswith("/"):
        p = env['PROJECTS_SRC_PATH'] + x
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
  # if env['SHARED'] == '0':
  #   dep = dep + '_static'
  deppath = os.path.abspath(os.path.join(env['PROJECTS_SRC_PATH'],deppath))
  AddOrdering(env,dep,deppath)
  AddDependencyConfig(env,dep, deppath)
  
def AddOrdering(env, dep, deppath):
  prog = env['PROG_NAME']
  # if env['SHARED'] == '0':
  #   prog = prog + '_static'
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
