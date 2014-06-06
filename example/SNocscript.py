from helper import *

#           Environment
Import( 'env', 'args' )

def inclDeps(env, args):
    airuTech = join(args['SCONSCRIPT_PATH'],'..','..')
    # AddDependency(args,'CNetsTimeUtils',join(airuTech,'cnets','timeUtils'))
    AddPthreads(env, args)

c = {}
c['PROG_NAME'] = 'CNetsTimeUtils'
c['sourceFiles'] = ['timeUtils.c']
c['testFiles'] = ['timeUtilsTests.c']
c['exportsDefines'] = ['CNetsTimeUtilsExports']
c['inclDepsDynamic'] = inclDeps
c['inclDepsStatic'] = inclDeps
DefaultLibraryConfig(c, env, args)