#ifndef CNets_TIMEUTILS_EXPORTS_H
#define CNets_TIMEUTILS_EXPORTS_H

#if defined WIN32 && !defined __MINGW32__ && !defined(CYGWIN) && !defined(CNetsTimeUtils_static)
    #ifdef CNetsTimeUtilsExports
        #define CNetsTimeUtilsExportsAPI __declspec(dllexport)
    #else
    	#define CNetsTimeUtilsExportsAPI __declspec(dllimport)
    #endif
#else
    #define CNetsTimeUtilsExportsAPI extern
#endif

#endif /* CNets_TIMEUTILS_EXPORTS_H*/