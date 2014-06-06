from helper import *

#           Environment
Import( 'env', 'args' )

def inclDeps(env, args):
    airuTech = join(args['SNOCSCRIPT_PATH'],'..','..')
    projectsRoot = args['PROJECTS_ROOT_PATH']
    # AddDependency(args,'CNetsTimeUtils',join(airuTech,'cnets','timeUtils'))
    AddPthreads(env, args)

c = {}
c['PROG_NAME'] = 'CNetsTimeUtils'
c['sourceFiles'] = ['timeUtils.c']
c['testFiles'] = ['timeUtilsTests.c']
c['exportsDefines'] = ['CNetsTimeUtilsExports']
c['defines'] = []
c['inclDepsDynamic'] = inclDeps
c['inclDepsStatic'] = inclDeps
DefaultLibraryConfig(c, env, args)