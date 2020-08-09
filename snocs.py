#! /usr/bin/env python
import os.path
import sys
import os
import importlib
from builder import PROJECTS_SRC_PATH
from builder import printHelp

SCONS_BIN_DIR = os.getenv('SCONS_BIN_DIR', '')
#SCONS_LIB_DIR = "SCONS_LIB_DIR=/opt/poky-edison/1.6.1/sysroots/core2-32-poky-linux/usr/lib/python2.7/site-packages "
def Snocs(argv):
    SNocscript = None
    firstRealArgI = 1
    #in case we don't have any arguments
    if len(argv) <= firstRealArgI:
        #try to find the SNocscript right here
        if os.path.exists(os.path.join(os.getcwd(),"SNocscript.py")):
            firstRealArgI = firstRealArgI - 1
            SNocscript = os.path.join(os.getcwd(),"SNocscript.py")
        else:
            print("No SNocscript files found")
            printHelp()
            exit()
    else:
        #try to find the SNocscript in the specified relative to current path
        if os.path.exists(os.path.join(os.getcwd(),argv[firstRealArgI],"SNocscript.py")):
            SNocscript = os.path.join(os.getcwd(),argv[firstRealArgI],"SNocscript.py")
        #try to find the SNocscript in the specified absolute path
        elif os.path.exists(os.path.join(argv[firstRealArgI],"SNocscript.py")):
            SNocscript = os.path.join(argv[firstRealArgI],"SNocscript.py")            
        #try to find the SNocscript in the specified path from projects src root
        elif os.path.exists(os.path.join(PROJECTS_SRC_PATH,argv[firstRealArgI],"SNocscript.py")):
            SNocscript = os.path.join(PROJECTS_SRC_PATH,argv[firstRealArgI],"SNocscript.py")
        #try to find the SNocscript right here
        elif os.path.exists(os.path.join(os.getcwd(),"SNocscript.py")):
            firstRealArgI = firstRealArgI - 1
            SNocscript = os.path.join(os.getcwd(),"SNocscript.py")
        else:
            print("No "+os.path.join(os.getcwd(),"SNocscript.py"))
            print("No "+os.path.join(argv[firstRealArgI],"SNocscript.py"))
            print("No "+os.path.join(os.getcwd(),argv[firstRealArgI],"SNocscript.py"))
            print("No "+os.path.join(PROJECTS_SRC_PATH,argv[firstRealArgI],"SNocscript.py"))
            print("NO SNocscript files found")
            printHelp()
            exit()
        
    OTHER_ARGUMENTS = ""
    MORE_WARNINGS = 0
    WARNINGS_AS_ERRORS = 0
    ALL_PROJECTS = 0
    CLEANING_STAGE = 0
    SKIP_PROJECT_NAMES = []
    if len(argv) > firstRealArgI + 1:
        for i in range(firstRealArgI+1, len(argv)):
            if argv[i] == '-h':
                printHelp()
                exit()
            elif argv[i] == '-r':
                os.system("python "+SNocscript+" "+PROJECTS_SRC_PATH)
                #imp.load_source('SNocscript',os.path.dirname(SNocscript))
                exit()
            elif argv[i] == '-all':
                print("* Will make the dependencies")
                ALL_PROJECTS = 1
                continue
            elif argv[i] == '--more-warnings':
                MORE_WARNINGS = 1
                continue
            elif argv[i] == '--warnings-as-errors':
                WARNINGS_AS_ERRORS = 1
                continue
            elif argv[i].startswith('--no-') and len(argv[i])>5:
                SKIP_PROJECT_NAMES += [argv[i][5:]]
                continue
            elif argv[i].startswith('without=') and len(argv[i])>8:
                SKIP_PROJECT_NAMES += argv[i][8:].split(":")
            elif argv[i] == '-c':
                CLEANING_STAGE = 1
            if ' ' in argv[i] and '=' in argv[i]:
                s = argv[i].split('=')
                argv[i] = s[0]+"=\""+('='.join(s[1:]))+"\""
            OTHER_ARGUMENTS+=" "+argv[i]
        #end for arguments
        
    if ALL_PROJECTS == 1:
        OTHER_ARGUMENTS +=" build_all=1"
    if CLEANING_STAGE == 1:
        OTHER_ARGUMENTS +=" cleaning=1"
    if WARNINGS_AS_ERRORS == 1:
        OTHER_ARGUMENTS +=" warnings-as-errors=1"
    if MORE_WARNINGS == 1:
        OTHER_ARGUMENTS +=" more-warnings=1"
    for name in SKIP_PROJECT_NAMES:
        OTHER_ARGUMENTS +=" without="+name
        # OTHER_ARGUMENTS +=" without="+(':'.join(SKIP_PROJECT_NAMES)) 

    snocsStr = SCONS_BIN_DIR+"scons -f "+os.path.abspath(os.path.dirname(__file__))+"/SNocstruct snocscript="+SNocscript+OTHER_ARGUMENTS
    print(snocsStr)
    os.system(snocsStr)


if __name__ == '__main__':
    Snocs(sys.argv)
