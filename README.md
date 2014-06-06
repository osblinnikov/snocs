SNocs
=====

0. a wrapper for SCons Software Construction tool (www.scons.org)
1. is integrated into golang-like workspace structure (http://golang.org/doc/code.html), but can be easily configured
2. able to build any project from your's workspace even you are not in project directory
3. makes dependency management easy from SNocscript (see the example)
4. allows you to choose compiler, platform and configuration from command line
5. enables you to set up Unit tests for the project

If you want to change default path to the Projects workspace directory just change 'PROJECTS_ROOT_PATH' variable in 'builder.py' file. 

During test phase of building, SNocs extends it's LD_LIBRARY_PATH and PATH variables to allow searching for shared libraries

Installation
---

Clone repo, add to the PATH

Test that all is well:

    snocs example compiler=gcc test

Enjoy your crossplatform usage of the SNocs!

Usage
---

snocs [SNocscriptFilePath] [options]

SNocscriptFilePath can be absolute or relative to current path or 
relative to workspace sources root directory e.g.:

    snocs example compiler=gcc test

Available SNocs options:

    compiler={gcc,mingw,vc9,vc10,vc11,vc11exp}
    configuration={Debug,Release}
    platform={x86,Win32,x64} # Win32 is an alias to x86
    verbose=1 # enables scons debug output
    shared=1 | 0 #enables building shared libraries for default build config
    testnorun=1 #disables tests run in case of test/install targets
    -r        # execute SNocscriptFilePath/SNocscript as Python script without SCons
    -c        # execute cleaning only for chosen SNocscript, not dependent libs
    -call     # execute cleaning for current and all dependent projects
    
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
