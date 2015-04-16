
from helper import *
#           Environment
Import( 'env' )

def add_dependencies(env):
    # AddDependency(env,'libcaf_core','github.com/actor-framework/libcaf_core')
    AddPthreads(env)
    # AddNetwork(env)
    # AddOpenGL(env)

c = {}
c['PROG_NAME'] = 'CNetsTimeUtils'
c['sourceFiles'] = ['timeUtils.c']
c['testFiles'] = ['timeUtilsTests.c']
c['runFiles'] = ['main.c']
c['defines'] = []
c['inclDepsDynamic'] = add_dependencies
c['inclDepsStatic'] = add_dependencies
DefaultLibraryConfig(env,c)
