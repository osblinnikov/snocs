import platform

if platform.system() == 'Linux':
    RED='\033[0;31m'
    GREEN='\033[1;32m'
    DGREEN='\033[0;32m'
    NOCOLOR='\033[0m'
else:
    DGREEN=NOCOLOR=GREEN=RED=''