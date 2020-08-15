
from snocs_helper import *
#           Environment
Import( 'env' )

def add_dependencies(env):
	pass
    # AddDependency(env,'libcaf_core','github.com/actor-framework/libcaf_core')
    # AddPthreads(env)
    # AddNetwork(env)
    # AddOpenGL(env)

c = {}
c['PROG_NAME'] = 'hlsexample'
c['TEST_HLS_PROJECT_NAME'] = 'tests'
c['MAIN_HLS_PROJECT_NAME'] = 'main'
c['libFiles'] = ['empty.c']
c['testFiles'] = ['tests.c']
c['runFiles'] = ['main.c']
c['defines'] = []
c['depsDynamic'] = add_dependencies
c['depsStatic'] = add_dependencies
c['runnableOnly'] = False
DefaultLibraryConfig(env,c)
