
from helper import *
#           Environment
Import( 'env' )

def add_dependencies(env):
    #airuTech = join(args['SNOCSCRIPT_PATH'],'..','..')
    #projectsRoot = args['PROJECTS_ROOT_PATH']
    # AddDependency(args,'CNetsTimeUtils',join(airuTech,'cnets','timeUtils'))
    AddPthreads(env)

c = {}
c['PROG_NAME'] = 'CNetsTimeUtils'
c['sourceFiles'] = ['timeUtils.c']
c['testFiles'] = ['timeUtilsTests.c']
c['runFiles'] = ['main.c']
c['defines'] = []
c['inclDepsDynamic'] = add_dependencies
c['inclDepsStatic'] = add_dependencies
DefaultLibraryConfig(env,c)