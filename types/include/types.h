#ifndef CNets_TYPES_H__
#define CNets_TYPES_H__

#include <errno.h>

#ifdef WIN32
/*TO MAKE VC HAPPY, (need to include it before windows.h*/
    #include <winsock2.h>
#endif

#if defined(WIN32) && !defined(CYGWIN)
    #ifndef WINDOWS_HEADER_H_
    #define WINDOWS_HEADER_H_
        #include <windows.h>
        #include <windef.h>
    #endif
#else
	#ifndef BOOL
		typedef unsigned char           BOOL;
	#endif
#endif

#ifndef FALSE
	#define FALSE       0
#endif

#ifndef TRUE
	#define TRUE        1
#endif

typedef struct binary{
	char* data;
	unsigned data_size;
	unsigned full_size;
}binary;

#if defined(WIN32) && !defined(CYGWIN)&& !defined(__MINGW32__)
    #include "vc/stdint.h"
    #include "vc/inttypes.h"
#else
    #include <inttypes.h>
#endif
#endif /* CNets_TYPES_H__ */
