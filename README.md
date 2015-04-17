SNocs
=====

0. a wrapper for SCons Software Construction tool (www.scons.org)
1. is integrated into golang-like workspace structure (http://golang.org/doc/code.html), but can be easily configured
2. able to build any project from your workspace even if you are not in the project's directory
3. makes dependency management easy from SNocscript using AddDependency function (see the example/SNocscript.py and/or helper.py)
4. allows you to choose compiler, platform and configuration from the command line
5. enables you to automatically set up and execute Unit tests for the project

    If you want to change default workspace directory just set SNOCS_PROJECTS_SRC_PATH environment variable. 
    
    If you want to change default installation paths then set SNOCS_INSTALL_LIB_PATH and SNOCS_INSTALL_BIN_PATH environment variables"
    
    During test phase of building, SNocs extends it's LD_LIBRARY_PATH and PATH variables to allow searching for shared libraries
sea
Installation
---

Clone repo, add to the PATH

Check that all is well:

    snocs example compiler=gcc test

Enjoy your crossplatform usage of SNocs!

SNocscript.py
---

This file is used for specification your build properties for every project in the workspace. During build SNocs scanning all the dependent projects using pathToProject specified in the `AddDependency(env, targetName, pathToProject)` function from [helper.py](https://github.com/osblinnikov/snocs/blob/master/helper.py). During this scans SNocs uses `SNocscript.py` files in the same way as SCons uses SConscript (see [SNocstruct](https://github.com/osblinnikov/snocs/blob/master/SNocstruct), look for `SConscript` function call). 

The SNocs is a fancy but very powerful and flexible wrapper for SCons. Developer is enabled to write high-level project description in SNocscript.py and SNocs will make the all magic for project dependency management, includes, libraries, static and shared libraries build, compilator choosing and more. At the same time developer is free to use low-level SCons API thus SNocs "batteries" are included but adjustable and/or removable. If you want to use SCons `"libraries/headers search"` then see [this example](https://github.com/osblinnikov/caf-workspace/blob/master/actor-framework-snocs/libcaf_opencl_SNocscript.py), if you want to create multiple test targets per project instead of a single one then see [this example](https://github.com/osblinnikov/caf-workspace/blob/master/actor-framework-snocs/unit_testing_SNocscript.py) , if you wanna make multiple executable targets in project, e.g `"examples of your library use"` - see [this SNocscript.py](https://github.com/osblinnikov/caf-workspace/blob/master/actor-framework-snocs/examples_SNocscript.py).

To get started writing your new project or adapt existing project to SNocs see the [example directory](https://github.com/osblinnikov/snocs/blob/master/example/). In case you need more flexibility check the source code of [helper functions](https://github.com/osblinnikov/snocs/blob/master/helper.py) or these [SNocscripts for CAF build](https://github.com/osblinnikov/caf-workspace/tree/master/actor-framework-snocs)

Feel free to ask for help in the issue tracker.

Usage from command line
---

snocs [SNocscriptFilePath] [options] [target]

SNocscriptFilePath can be absolute or relative to current path or 
relative to workspace sources root directory e.g.:

    snocs example compiler=gpp_cpp11 test

Available SNocs options:

    compiler={gcc,gpp,mingw,clangpp,vc9,vc9exp,vc10,vc10exp,vc11,vc11exp}
    configuration={Debug,Release}
    platform={x86,Win32,x64} # Win32 is an alias to x86
    verbose=1 # enables scons debug output
    shared=1 | 0 #enables building shared libraries for default build config
    testnorun=1 #disables tests run in case of test/install targets
    -r        # execute SNocscriptFilePath/SNocscript as Python script without SCons
    -h        # print this help"
    -c        # execute cleaning
    -all      # execute for all dependent projects
    --more-warnings or more-warnings=1            # show as many warnings as possible"
    --warnings-as-errors or warnings-as-errors=1  # treat warns as errors"
    --no-PROJECT1_PREFIX or without=PROJECT1_PREFIX without=PROJECT2_PREFIX # disable projects compilation. PROJECT1_PREFIX must match to the begining of the project name. PREFIX can start with *, it means that the name should contain this PREFIX
    compiler_path=FULL_PATH_TO_THE_COMPILER
    linker_path=FULL_PATH_TO_THE_LINKER
    cpppath=PATH_TO_INCLUDES1 cpppath=PATH_TO_INCLUDES2
    define="DEFINITION1=100" define=DEFINE2
    libpath=PATH_TO_LIBRARIES
    lib=ADDITIONAL_LIBRARY_NAME
    cflag=FLAG1 cxxflag=FLAG2 cppflag=FLAG3 #Compile flags
    lflag=FLAG1 lflag=FLAG2   lflag=FLAG3   #Link flags

Available targets:

    test
    install

Other options can be specific for SCons

Examples:

    snocs .. compiler=vc9 platform=x86 configuration=Debug
    snocs test -Q           #builds and runs tests with reduced log
    snocs install -c        #cleans installation
    snocs icanchangethisdomain/SomeProjectName -r  # runs SNocscript as Python script
    
    
    
TODO:
---

    --prefix=Installation directory prefix
    pkg-config .pc files generation with the correct prefixes
