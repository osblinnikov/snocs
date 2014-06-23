import os.path
import shutil
# from cogapp import Cog
join = os.path.join
#--------------------------------------
#			Functions
#--------------------------------------

# Prepends the full path information to the output directory so that the build
# files are dropped into the directory specified by trgt rather than in the 
# same directory as the SNocscript file.
# 
# Parameters:
#	 env	 - The environment to assign the Program value for
#	 outdir	- The relative path to the location you want the Program binary to be placed
#	 trgt	- The target application name (without extension)
#	 srcs	- The list of source files
# Ref:
#	 Credit grieve and his local SNocs guru for this: 
#	 http://stackoverflow.com/questions/279860/how-do-i-get-projects-to-place-their-build-output-into-the-same-directory-with
def cogging(files, CLEANING_STAGE):
	# cleaning_arg = '-U' #-u means unix style ending
	# if CLEANING_STAGE != '0':
	# 	cleaning_arg = '-x'
	# #'-s',	'/**generated**/', 
	# argv = ['cogging','-r', cleaning_arg, '-I', os.path.dirname(__file__)] + files
	# ret = Cog().main(argv)
	return

def DefaultParentConfig(c,env,args):
	args['PROG_NAME'] = "cnets_parent"

	if args['NO_DYNAMIC_BUILD'] != '1':
		args['prj_env'] = env.Clone()
		args['ADD_STATIC_DEPENDENCIES'] = 0
		c['inclDepsDynamic'](env,args)

	if args['NO_STATIC_BUILD'] != '1':
		args['PROG_NAME'] += "_static"
		args['prj_env'] = env.Clone()
		args['ADD_STATIC_DEPENDENCIES'] = 1
		c['inclDepsStatic'](env,args)

def enableQtModules(c,env,args):
	if c.has_key('qt5modules') and args['QT_DIR_NAME']=='QT5DIR':
		env.EnableQt5Modules(c['qt5modules'])
	if c.has_key('qt4modules') and args['QT_DIR_NAME']=='QT4DIR':
		env.EnableQt4Modules(c['qt4modules'])

def DefaultLibraryConfig(c, env, args):
	if not c.has_key("paths"):
		c['paths'] = []
	curDir = args['SNOCSCRIPT_PATH']
	if args['NO_DYNAMIC_BUILD'] != '1':
		args['ADD_STATIC_DEPENDENCIES'] = 0
		#--------------------------------------------
		#			SHARED
		args['PROG_NAME'] = c['PROG_NAME']
		args['prj_env'] = env.Clone()
		enableQtModules(c,args['prj_env'],args)
		args['prj_env'].Append(
			CPPPATH = c['paths']+[join(curDir,'include')],
			CPPDEFINES = c['defines']+[c['PROG_NAME']+"_EXPORT"]
		)

		c['inclDepsDynamic'](env, args)
		env.Default(PrefixSharedLibrary(args, 'src', c['sourceFiles']))

		#			 SHARED TESTS
		args['PROG_NAME'] = c['PROG_NAME'] + "_test"
		args['prj_env'] = env.Clone()
		enableQtModules(c,args['prj_env'],args)
		args['prj_env'].Append( CPPPATH = c['paths']+[ join(curDir,'include') ] )
		AddDependency(args, c['PROG_NAME'], curDir)
		
		if c.get('inclDepsDynamic_tests')!=None:
			c['inclDepsDynamic_tests'](env, args)
		c['inclDepsDynamic'](env, args)

		env.Default(PrefixTest(args, 'tests', c['testFiles']))

		if c.has_key('runFiles'):
			#			 SHARED RUN
			args['PROG_NAME'] = c['PROG_NAME'] + "_run"
			args['prj_env'] = env.Clone()
			enableQtModules(c,args['prj_env'],args)
			args['prj_env'].Append( CPPPATH = c['paths']+[ join(curDir,'include') ] )
			AddDependency(args, c['PROG_NAME'], curDir)
			
			if c.get('inclDepsDynamic_run')!=None:
				c['inclDepsDynamic_run'](env, args)
			c['inclDepsDynamic'](env, args)

			env.Default(PrefixProgram(args, 'src', c['runFiles']))

	if args['NO_STATIC_BUILD'] != '1':
		args['ADD_STATIC_DEPENDENCIES'] = 1
		#			STATIC
		args['PROG_NAME'] = c['PROG_NAME'] + "_static"
		args['prj_env'] = env.Clone()
		enableQtModules(c,args['prj_env'],args)
		args['prj_env'].Append( 
			CPPPATH = c['paths']+[join(curDir,'include')],
			CPPDEFINES = c['defines']+[c['PROG_NAME']+"_STATIC"]
		)
		c['inclDepsStatic'](env, args)
		env.Default(PrefixLibrary(args, 'src', c['sourceFiles']))

		#			 STATIC TESTS
		args['PROG_NAME'] = c['PROG_NAME'] + "_static_test"
		args['prj_env'] = env.Clone()
		enableQtModules(c,args['prj_env'],args)
		args['prj_env'].Append(
			CPPPATH = c['paths']+[ join(curDir,'include') ],
			CPPDEFINES = c['defines']+[c['PROG_NAME']+"_STATIC"]
		)
		AddDependency(args, c['PROG_NAME'], curDir)
		if c.get('inclDepsStatic_tests')!=None:
			c['inclDepsStatic_tests'](env, args)
		c['inclDepsStatic'](env, args)
		
		env.Default(PrefixTest(args, 'tests', c['testFiles']))

		if c.has_key('runFiles'):
			#			 SHARED RUN
			args['PROG_NAME'] = c['PROG_NAME'] + "_static_run"
			args['prj_env'] = env.Clone()
			enableQtModules(c,args['prj_env'],args)
			args['prj_env'].Append(
				CPPPATH = c['paths']+[ join(curDir,'include') ],
				CPPDEFINES = c['defines']+[c['PROG_NAME']+"_STATIC"]
			)
			AddDependency(args, c['PROG_NAME'], curDir)
			
			if c.get('inclDepsDynamic_run')!=None:
				c['inclDepsDynamic_run'](env, args)
			c['inclDepsDynamic'](env, args)

			env.Default(PrefixProgram(args, 'src', c['runFiles']))

def PrefixProgram(args, folder, srcs):
	trgt = args['PROG_NAME']
	folder_trgt = os.path.join(folder, trgt+'.tmp')
	args['prj_env'].VariantDir(folder_trgt, folder, duplicate=0)
	#------------	COG	-------------------
	cogging(PrefixSources(args, folder, srcs), args['CLEANING_STAGE'])
	#--------------------------------------
	srcs = PrefixSources(args, folder_trgt, srcs)
	linkom = None
	if args['MSVC_VERSION'] != None and float(args['MSVC_VERSION'].translate(None, 'Exp')) < 11:
		linkom = 'mt.exe -nologo -manifest ${TARGET}.manifest -outputresource:$TARGET;1'
	if args['MSVC_PDB']:
		args['prj_env'].Append(PDB = os.path.join( args['BIN_DIR'], trgt + args['ARCHITECTURE_CODE'] + '.pdb' ))
	targetFullPath = os.path.join(args['SNOCSCRIPT_PATH'],trgt + args['ARCHITECTURE_CODE'])
	targetFullPathToBin = os.path.join(args['BIN_DIR'],trgt+args['ARCHITECTURE_CODE'])
	args['APP_BUILD'][targetFullPath] = args['prj_env'].Program(
		target = targetFullPathToBin, 
		source = srcs, 
		LINKCOM	= [args['prj_env']['LINKCOM'], linkom]
	)
	args['INSTALL_ALIASES'].append(args['prj_env'].Install(os.path.join(args['INSTALL_PATH'],'bin'), args['APP_BUILD'][targetFullPath]))#setup install directory

	return args['APP_BUILD'][targetFullPath]

def PrefixTest(args, folder, srcs):
	trgt = args['PROG_NAME']
	folder_trgt = os.path.join(folder, trgt+'.tmp')
	args['prj_env'].VariantDir(folder_trgt, folder, duplicate=0)
	#------------	COG	-------------------
	cogging(PrefixSources(args, folder, srcs), args['CLEANING_STAGE'])
	#--------------------------------------
	srcs = PrefixSources(args, folder_trgt, srcs)
	linkom = None
	if args['MSVC_VERSION'] != None and float(args['MSVC_VERSION'].translate(None, 'Exp')) < 11:
		linkom = 'mt.exe -nologo -manifest ${TARGET}.manifest -outputresource:$TARGET;1'
	if args['MSVC_PDB']:
		args['prj_env'].Append(PDB = os.path.join( args['BIN_DIR'], trgt + args['ARCHITECTURE_CODE'] + '.pdb' ))
	targetFullPath = os.path.join(args['SNOCSCRIPT_PATH'],trgt + args['ARCHITECTURE_CODE'])
	targetFullPathToBin = os.path.join(args['BIN_DIR'],trgt+args['ARCHITECTURE_CODE'])
	args['APP_BUILD'][targetFullPath] = args['prj_env'].Program(target = targetFullPathToBin, source = srcs, LINKCOM	= [args['prj_env']['LINKCOM'], linkom])
	args['INSTALL_ALIASES'].append(args['prj_env'].Install(os.path.join(args['INSTALL_PATH'],'bin'), args['APP_BUILD'][targetFullPath]))#setup install directory

	testPassedFullPath = os.path.join(args['SNOCSCRIPT_PATH'],args['configuration'],'bin',trgt+args['ARCHITECTURE_CODE']+".passed")
	args['TEST_ALIASES'].append(args['prj_env'].Test(testPassedFullPath, args['APP_BUILD'][targetFullPath]))

	return args['APP_BUILD'][targetFullPath]

# Similar to PrefixProgram above, except for Library
def PrefixLibrary(args, folder, srcs):
	trgt = args['PROG_NAME']
	folder_trgt = os.path.join(folder, trgt+'.tmp')
	args['prj_env'].VariantDir(folder_trgt, folder, duplicate=0)
	#------------	COG	-------------------
	cogging(PrefixSources(args, folder, srcs), args['CLEANING_STAGE'])
	#--------------------------------------
	srcs = PrefixSources(args, folder_trgt, srcs)
	if args['MSVC_PDB']:
		args['prj_env'].Append(PDB = os.path.join( args['LIB_DIR'], trgt+args['ARCHITECTURE_CODE'] + '.pdb' ))
	targetFullPath = os.path.join(args['SNOCSCRIPT_PATH'],trgt+args['ARCHITECTURE_CODE'])
	targetFullPathToBin = os.path.join(args['LIB_DIR'],trgt+args['ARCHITECTURE_CODE'])
	args['APP_BUILD'][targetFullPath] = args['prj_env'].Library(target = targetFullPathToBin, source = srcs)
	args['INSTALL_ALIASES'].append(args['prj_env'].Install(os.path.join(args['INSTALL_PATH'],'lib'), args['APP_BUILD'][targetFullPath]))#setup install directory
	return args['APP_BUILD'][targetFullPath]
	
# Similar to PrefixProgram above, except for SharedLibrary
def PrefixSharedLibrary(args, folder, srcs):
	trgt = args['PROG_NAME']
	folder_trgt = os.path.join(folder, trgt+'.tmp')
	args['prj_env'].VariantDir(folder_trgt, folder, duplicate=0)
	#------------	COG	-------------------
	cogging(PrefixSources(args, folder, srcs), args['CLEANING_STAGE'])
	#--------------------------------------
	srcs = PrefixSources(args, folder_trgt, srcs)
	linkom = None
	if args['MSVC_VERSION'] != None and float(args['MSVC_VERSION'].translate(None, 'Exp')) < 11:
		linkom = 'mt.exe -nologo -manifest ${TARGET}.manifest -outputresource:$TARGET;2'
	if args['MSVC_PDB']:
		args['prj_env'].Append(PDB = os.path.join( args['LIB_DIR'], trgt+args['ARCHITECTURE_CODE'] + '.pdb' ))
	targetFullPath = os.path.join(args['SNOCSCRIPT_PATH'],trgt+args['ARCHITECTURE_CODE'])
	targetFullPathToBin = os.path.join(args['LIB_DIR'],trgt+args['ARCHITECTURE_CODE'])
	args['APP_BUILD'][targetFullPath] = args['prj_env'].SharedLibrary(target = targetFullPathToBin, source = srcs, LINKCOM	= [args['prj_env']['LINKCOM'], linkom]) 
	args['INSTALL_ALIASES'].append(args['prj_env'].Install(os.path.join(args['INSTALL_PATH'],'lib'), args['APP_BUILD'][targetFullPath]))#setup install directory
	return args['APP_BUILD'][targetFullPath]

def PrefixFilename(filename, extensions):
	return [(filename + ext) for ext in extensions]

# Prefix the source files names with the source directory
def PrefixSources(args, srcdir, srcs):
	return	[os.path.join(args['SNOCSCRIPT_PATH'],srcdir, x) for x in srcs]

def AddDependencyConfig(args, dep, deppath):
	if deppath == None:
		deppath = '.'
	definesVar = []
	if args['ADD_STATIC_DEPENDENCIES'] == 1:
		definesVar = [dep]
	args['prj_env'].Append(
		LIBPATH = [os.path.join(deppath,args['configuration'],'lib')],
		LIBS = [dep+args['ARCHITECTURE_CODE']],
		LINKFLAGS = [],
		CPPPATH = [os.path.join(deppath,'include')],
		CPPDEFINES = definesVar,
		CCFLAGS = []
	)

def AddDependency(args, dep, deppath):
	if args['ADD_STATIC_DEPENDENCIES'] == 1:
		dep = dep + '_static'
	deppath = os.path.abspath(deppath)
	AddOrdering(args,dep,deppath)
	AddDependencyConfig(args,dep, deppath)
	
def AddOrdering(args, dep, deppath):
	prog = args['PROG_NAME']
	#print prog+"->"+dep
	prog = os.path.join(args['SNOCSCRIPT_PATH'],prog+args['ARCHITECTURE_CODE'])
	if args['APP_DEPENDENCIES'].get(prog) == None:
		args['APP_DEPENDENCIES'][prog] = [];
	depFullPath = os.path.join(deppath,dep+args['ARCHITECTURE_CODE'])
	args['APP_DEPENDENCIES'][prog].append(depFullPath)
	if deppath != args['SNOCSCRIPT_PATH']:
		if args.get('CROSSPROJECT_DEPENDENCIES') == None:
			args['CROSSPROJECT_DEPENDENCIES'] = {};
		if args['CROSSPROJECT_DEPENDENCIES'].get(deppath) == None:
			args['CROSSPROJECT_DEPENDENCIES'][deppath] = dep
			
def AddScript(args, dep, deppath):
	if deppath != args['SNOCSCRIPT_PATH']:
		if args.get('CROSSPROJECT_DEPENDENCIES') == None:
			args['CROSSPROJECT_DEPENDENCIES'] = {};
		if args['CROSSPROJECT_DEPENDENCIES'].get(deppath) == None:
			args['CROSSPROJECT_DEPENDENCIES'][deppath] = dep
			
def AddPthreads(env, args):
	PATH_TO_PTHREADS_WIN = os.path.join(args['PROJECTS_SRC_PATH'],'sourceware.org','pthreads-win32','dll-latest')
	if args['MSVC_VERSION'] != None:
		args['prj_env'].Append(
			LIBS = ['pthreadVC2'],
			CPPPATH = [os.path.join(PATH_TO_PTHREADS_WIN,'include')],
			LIBPATH = [os.path.join(PATH_TO_PTHREADS_WIN,'lib',args['TARGET_ARCH'])]
		)
		env.AppendENVPath('PATH', os.path.join(PATH_TO_PTHREADS_WIN,'dll',args['TARGET_ARCH']))
	elif args['COMPILER_CODE'] == 'mingw':
		args['prj_env'].Append(
			LIBS = ['pthreadGC2'],
			CPPPATH = [os.path.join(PATH_TO_PTHREADS_WIN,'include')],
			LIBPATH = [os.path.join(PATH_TO_PTHREADS_WIN,'lib',args['TARGET_ARCH'])]
		)
		env.AppendENVPath('PATH', os.path.join(PATH_TO_PTHREADS_WIN,'dll',args['TARGET_ARCH']))
	else:
		args['prj_env'].Append(
			# LIBS = ['pthread'],
			LINKFLAGS = ['-pthread']
		)
def AddNetwork(args):
	if args['MSVC_VERSION'] != None:
		args['prj_env'].Append(LIBS = ['WSock32'])
	elif args['COMPILER_CODE'] == 'mingw':
		args['prj_env'].Append(LIBS = ['ws2_32', 'IPHLPAPI'])
