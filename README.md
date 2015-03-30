SNocs
=====

0. a wrapper for SCons Software Construction tool (www.scons.org)
1. is integrated into golang-like workspace structure (http://golang.org/doc/code.html), but can be easily configured
2. able to build any project from your's workspace even you are not in project directory
3. makes dependency management easy from SNocscript (see the example)
4. allows you to choose compiler, platform and configuration from command line
5. enables you to set up Unit tests for the project

If you want to change default workspace directory just set SNOCS_PROJECTS_SRC_PATH environment variable. 
If you want to change default installation paths then set SNOCS_INSTALL_LIB_PATH and SNOCS_INSTALL_BIN_PATH environment variables" 

During test phase of building, SNocs extends it's LD_LIBRARY_PATH and PATH variables to allow searching for shared libraries

Installation
---

Clone repo, add to the PATH

Test that all is well:

    snocs example compiler=gcc test

Enjoy your crossplatform usage of SNocs!

Usage
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
    -c        # execute cleaning
    -all      # execute for all dependent projects
    --more-warnings or more-warnings=1            # show as many warnings as possible"
    --warnings-as-errors or warnings-as-errors=1  # treat warns as errors"
    --no-PROJECT1_PREFIX or without=PROJECT1_PREFIX without=PROJECT2_PREFIX # disable projects compilation. PROJECT1_PREFIX must match to the begining of the project name. PREFIX can start with *, it means that the name should contain this PREFIX"
    cpppath=PATH_TO_INCLUDES1 cpppath=PATH_TO_INCLUDES2
    define="DEFINITION1=100" define=DEFINE2
    libpath=PATH_TO_LIBRARIES
    lib=ADDITIONAL_LIBRARY_NAME
    cflag=FLAG1 cflag=FLAG2 cflag=FLAG3 #Compile flags
    lflag=FLAG1 lflag=FLAG2 lflag=FLAG3 #Link flags

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
