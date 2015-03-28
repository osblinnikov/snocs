import os.path
import shutil
import copy
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
    c['inclDepsDynamic'](env)
  else:
    initEnv(env, c['PROG_NAME']+"_static")
    c['inclDepsStatic'](env)

def enableQtModules(env,c, doBuildUI):
  # addPaths = []
  if c.has_key('qt5modules') and env['QT_TOOL']=='qt5':
    env['prj_env'].EnableQt5Modules(c['qt5modules'])
    # addPaths = [os.path.abspath(os.path.join(env['QT_DIR'], 'include', x)) for x in c['qt5modules']]
    if doBuildUI:
      qtuisrc = []
      if c.has_key('qt5ui'):
        qtuisrc = PrefixSources(env, '', c['qt5ui'])

      for s in qtuisrc:
        env['prj_env'].Uic5(s)

  if c.has_key('qt4modules') and env['QT_TOOL']=='qt4':
    env['prj_env'].EnableQt4Modules(c['qt4modules'])
    # addPaths = [os.path.abspath(os.path.join(env['QT_DIR'], 'include', x)) for x in c['qt4modules']]
    if doBuildUI:
      qtuisrc = []
      if c.has_key('qt4ui'):
        qtuisrc = PrefixSources(env, '', c['qt4ui'])
      for s in qtuisrc:
        env['prj_env'].Uic4(s)
  # return addPaths

def funcInclDeps(env):
  return

def testInclDeps(c):
  if not c.has_key('inclDeps'):
    defInclDeps = funcInclDeps
  else:
    defInclDeps = c['inclDeps']
  if not c.has_key("inclDepsStatic"):
    c['inclDepsStatic'] = defInclDeps
  if not c.has_key("inclDepsStatic_tests"):
    c['inclDepsStatic_tests'] = defInclDeps
  if not c.has_key("inclDepsStatic_run"):
    c['inclDepsStatic_run'] = defInclDeps    
  if not c.has_key("inclDepsDynamic"):
    c['inclDepsDynamic'] = defInclDeps
  if not c.has_key("inclDepsDynamic_tests"):
    c['inclDepsDynamic_tests'] = defInclDeps
  if not c.has_key("inclDepsDynamic_run"):
    c['inclDepsDynamic_run'] = defInclDeps

def DefaultLibraryConfig(env, c):
  forceShared = c.has_key('forceShared') and c['forceShared'] == 1
  forceStatic = c.has_key('forceStatic') and c['forceStatic'] == 1

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

  if not c.has_key("CPPPATH"):
    c['CPPPATH'] = []
  c['CPPPATH'].append(env['SNOCSCRIPT_PATH'])

  if not c.has_key("CPPDEFINES"):
    c['CPPDEFINES'] = []

  testInclDeps(c)

  if not c.has_key("sourceFiles") or len(c['sourceFiles'])==0:
      c['sourceFiles'] = []
      srcFolder = os.path.join(env['SNOCSCRIPT_PATH'],'src')
      for root, dirs, files in os.walk(srcFolder):
        for fileName in files:
          if fileName == 'main.cpp' or fileName == 'main.c':
            continue
          if (len(fileName)>4 and fileName[-4:] == '.cpp') or (len(fileName)>2 and fileName[-2:] == '.c'):
            fileP = os.path.join(root,fileName)
            relativeFilePath =  fileP[(len(srcFolder)+1):]
            c['sourceFiles'].append(relativeFilePath)  

  #START!
  initEnv(env, c['PROG_NAME'])

  enableQtModules(env,c,True)
  env['prj_env'].Append( 
    CPPPATH = c['CPPPATH'],
    CPPDEFINES = c['CPPDEFINES']+LIB_DEFINES+STATIC_DEFINES
  )
  c['inclDeps'+DepsFunc](env)
  
  env['scons'].Default(PrefixLibrary(env, 'src', c['sourceFiles']))

  if c.has_key('testFiles'):
    #       STATIC TESTS
    initEnv(env, c['PROG_NAME']+"_test")

    enableQtModules(env,c,False)
    env['prj_env'].Append(
      CPPPATH = c['CPPPATH'],
      CPPDEFINES = c['CPPDEFINES']+STATIC_DEFINES
    )
    AddDependency(env, c['PROG_NAME'], env['SNOCSCRIPT_PATH'])
    c['inclDeps'+DepsFunc+'_tests'](env)
    c['inclDeps'+DepsFunc](env)
    
    env['scons'].Default(PrefixTest(env, 'tests', c['testFiles']))

  if c.has_key('runFiles'):
    #       SHARED RUN
    initEnv(env, c['PROG_NAME']+"_run")
    

    enableQtModules(env,c,False)
    env['prj_env'].Append(
      CPPPATH = c['CPPPATH'],
      CPPDEFINES = c['CPPDEFINES']+STATIC_DEFINES
    )
    AddDependency(env, c['PROG_NAME'], env['SNOCSCRIPT_PATH'])
    
    c['inclDeps'+DepsFunc+'_run'](env)
    c['inclDeps'+DepsFunc](env)
    
    env['scons'].Default(PrefixProgram(env, 'src', c['runFiles']))

  env['SHARED'] = SHARED_VAR_BCP

def PrefixProgram(env, folder, srcs):
  if env['PROG_NAME'] in env['WITHOUT']:
    return
  folder = os.path.abspath(os.path.join(env['SNOCSCRIPT_PATH'],folder))
  trgt = env['PROG_NAME']
  if env['SHARED'] == '0':
    trgt = trgt + '_static'
  
  folder_trgt = os.path.join(folder, trgt+env['ARCHITECTURE_CODE']+"_"+env['CONFIGURATION']+'.tmp')
  env['prj_env'].VariantDir(folder_trgt, folder, duplicate=0)
  
  srcs = PrefixSources(env, folder_trgt, srcs)
  linkom = None
  if env['MSVC_VERSION'] != None and float(env['MSVC_VERSION'].translate(None, 'Exp')) < 11:
    linkom = 'mt.exe -nologo -manifest ${TARGET}.manifest -outputresource:$TARGET;1'
  if env['MSVC_PDB']:
    env['prj_env'].Append(PDB = os.path.join( env['BIN_DIR'], trgt + env['ARCHITECTURE_CODE'] + '.pdb' ))
  targetFullPath = os.path.join(env['SNOCSCRIPT_PATH'],trgt + env['ARCHITECTURE_CODE'])
  targetFullPathToBin = os.path.join(env['BIN_DIR'],trgt+env['ARCHITECTURE_CODE'])
  env['APP_BUILD'][targetFullPath] = env['prj_env'].Program(
    target = targetFullPathToBin, 
    source = srcs, 
    LINKCOM  = [env['prj_env']['LINKCOM'], linkom]
  )
  env['INSTALL_ALIASES'].append(env['prj_env'].Install(env['INSTALL_BIN_PATH'], env['APP_BUILD'][targetFullPath]))#setup install directory

  return env['APP_BUILD'][targetFullPath]

def PrefixTest(env, folder, srcs):
  if env['PROG_NAME'] in env['WITHOUT']:
    return  
  folder = os.path.abspath(os.path.join(env['SNOCSCRIPT_PATH'],folder))
  trgt = env['PROG_NAME']
  if env['SHARED'] == '0':
    trgt = trgt + '_static'
  folder_trgt = os.path.join(folder, trgt+env['ARCHITECTURE_CODE']+"_"+env['CONFIGURATION']+'.tmp')
  env['prj_env'].VariantDir(folder_trgt, folder, duplicate=0)

  srcs = PrefixSources(env, folder_trgt, srcs)
  linkom = None
  if env['MSVC_VERSION'] != None and float(env['MSVC_VERSION'].translate(None, 'Exp')) < 11:
    linkom = 'mt.exe -nologo -manifest ${TARGET}.manifest -outputresource:$TARGET;1'
  if env['MSVC_PDB']:
    env['prj_env'].Append(PDB = os.path.join( env['BIN_DIR'], trgt + env['ARCHITECTURE_CODE'] + '.pdb' ))
  targetFullPath = os.path.join(env['SNOCSCRIPT_PATH'],trgt + env['ARCHITECTURE_CODE'])
  targetFullPathToBin = os.path.join(env['BIN_DIR'],trgt+env['ARCHITECTURE_CODE'])
  env['APP_BUILD'][targetFullPath] = env['prj_env'].Program(target = targetFullPathToBin, source = srcs, LINKCOM  = [env['prj_env']['LINKCOM'], linkom])
  env['INSTALL_ALIASES'].append(env['prj_env'].Install(env['INSTALL_BIN_PATH'], env['APP_BUILD'][targetFullPath]))#setup install directory

  testPassedFullPath = os.path.join(env['SNOCSCRIPT_PATH'],env['CONFIGURATION'],'bin',trgt+env['ARCHITECTURE_CODE']+".passed")
  env['TEST_ALIASES'].append(env['prj_env'].Test(testPassedFullPath, env['APP_BUILD'][targetFullPath]))

  return env['APP_BUILD'][targetFullPath]

# Similar to PrefixProgram above, except for Library
def PrefixLibrary(env, folder, srcs):
  if env['PROG_NAME'] in env['WITHOUT']:
    return  
  folder = os.path.abspath(os.path.join(env['SNOCSCRIPT_PATH'],folder))
  trgt = env['PROG_NAME']
  if env['SHARED'] == '0':
    trgt = trgt + '_static'
  folder_trgt = os.path.join(folder, trgt+env['ARCHITECTURE_CODE']+"_"+env['CONFIGURATION']+'.tmp')
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
  if env['PROG_NAME'] in env['WITHOUT']:
    return  
  folder = os.path.abspath(os.path.join(env['SNOCSCRIPT_PATH'],folder))
  trgt = env['PROG_NAME']
  if env['SHARED'] == '0':
    trgt = trgt + '_static'
  folder_trgt = os.path.join(folder, trgt+env['ARCHITECTURE_CODE']+"_"+env['CONFIGURATION']+'.tmp')
  env['prj_env'].VariantDir(folder_trgt, folder, duplicate=0)
  
  srcs = PrefixSources(env, folder_trgt, srcs)
  linkom = None
  if env['MSVC_VERSION'] != None and float(env['MSVC_VERSION'].translate(None, 'Exp')) < 11:
    linkom = 'mt.exe -nologo -manifest ${TARGET}.manifest -outputresource:$TARGET;2'
  if env['MSVC_PDB']:
    env['prj_env'].Append(PDB = os.path.join( env['LIB_DIR'], trgt+env['ARCHITECTURE_CODE'] + '.pdb' ))
  targetFullPath = os.path.join(env['SNOCSCRIPT_PATH'],trgt+env['ARCHITECTURE_CODE'])
  targetFullPathToBin = os.path.join(env['LIB_DIR'],trgt+env['ARCHITECTURE_CODE'])
  env['APP_BUILD'][targetFullPath] = env['prj_env'].SharedLibrary(target = targetFullPathToBin, source = srcs, LINKCOM  = [env['prj_env']['LINKCOM'], linkom]) 
  env['INSTALL_ALIASES'].append(env['prj_env'].Install(env['INSTALL_LIB_PATH'], env['APP_BUILD'][targetFullPath]))#setup install directory
  return env['APP_BUILD'][targetFullPath]

def PrefixFilename(filename, extensions):
  return [(filename + ext) for ext in extensions]

# Prefix the source files names with the source directory
def PrefixSources(env, srcdir, srcs):
  out = []
  for x in srcs:
    if isinstance(x, basestring):
      out.append(os.path.abspath(os.path.join(env['SNOCSCRIPT_PATH'],srcdir, x)))
    else:
      out.append(x)
  return out
  #return  [os.path.abspath(os.path.join(env['SNOCSCRIPT_PATH'],srcdir, x)) for x in srcs]

def AddDependencyConfig(env, dep, deppath):
  if deppath == None:
    deppath = '.'
  definesVar = []
  if env['SHARED'] == '0':
    definesVar = [dep.upper()]
  # print "CPPPATH+ "+deppath
  env['prj_env'].Append(
    LIBPATH = [os.path.join(deppath,env['CONFIGURATION'],'lib')],
    LIBS = [dep+env['ARCHITECTURE_CODE']],
    LINKFLAGS = [],
    CPPPATH = [deppath],
    CPPDEFINES = definesVar,
    CCFLAGS = []
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
  #print prog+"->"+dep
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
    env.AppendENVPath('PATH', os.path.join(PATH_TO_PTHREADS_WIN,'dll',env['PLATFORM']))
  elif env['COMPILER'] == 'mingw':
    env['prj_env'].Append(
      LIBS = ['pthreadGC2'],
      CPPPATH = [os.path.join(PATH_TO_PTHREADS_WIN,'include')],
      LIBPATH = [os.path.join(PATH_TO_PTHREADS_WIN,'lib',env['PLATFORM'])]
    )
    env.AppendENVPath('PATH', os.path.join(PATH_TO_PTHREADS_WIN,'dll',env['PLATFORM']))
  elif not env.has_key('LINK'):
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
    print "OpenGL for MSVC is not implemented yet in snocs"
  elif env['COMPILER'] == 'mingw':
    print "OpenGL for mingw is not implemented yet in snocs"
  else:
    env['prj_env'].Append(
      LIBS = ['GL'],
      # LINKFLAGS = ['-GL']
    )
