#ifndef CNETS_TIMEUTILS_H_
#define CNETS_TIMEUTILS_H_


#undef CNetsTimeUtils_EXPORT_API
#if defined WIN32 && !defined __MINGW32__ && !defined(CYGWIN) && !defined(CNETSTIMEUTILS_STATIC)
  #ifdef CNetsTimeUtils_EXPORT
    #define CNetsTimeUtils_EXPORT_API __declspec(dllexport)
  #else
    #define CNetsTimeUtils_EXPORT_API __declspec(dllimport)
  #endif
#else
  #define CNetsTimeUtils_EXPORT_API extern
#endif


#include <stdio.h>
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

#if defined(WIN32) && !defined(CYGWIN)&& !defined(__MINGW32__)
    #include "./vc/stdint.h"
    #include "./vc/inttypes.h"
#else
    #include <inttypes.h>
#endif


#if !defined __MINGW32__ && defined _WIN32
    struct timezone{
        int  tz_minuteswest; /* minutes W of Greenwich */
        int  tz_dsttime;     /* type of dst correction */
    };
#endif /*WIN32 endif*/

#if defined(__MINGW32__) || !defined(_WIN32)
    #include <sys/time.h>
#endif
#if defined __MINGW32__ || defined _WIN32
    #if defined(_MSC_VER) || defined(_MSC_EXTENSIONS)
      #define DELTA_EPOCH_IN_MICROSECS  11644473600000000Ui64
    #else
      #define DELTA_EPOCH_IN_MICROSECS  11644473600000000ULL
    #endif
    #include <time.h>
    #ifndef HAVE_STRUCT_TIMESPEC
        #define HAVE_STRUCT_TIMESPEC 1
        typedef struct timespec {
            time_t tv_sec;
            long tv_nsec;
        }timespec;
    #endif /* HAVE_STRUCT_TIMESPEC */
#endif
#ifdef __cplusplus
extern "C" {  /* only need to export C interface if used by C++ source code*/
#endif
    uint64_t CNetsTimeUtils_EXPORT_API   CurTimeNanosec();
    struct timespec CNetsTimeUtils_EXPORT_API  GetTimespecDelay(uint64_t nanosec);
    int  CNetsTimeUtils_EXPORT_API  CompareTimespec(struct timespec *timeSpec);
    int  CNetsTimeUtils_EXPORT_API  CompareTwoTimespecs(struct timespec *lTimeSpec,struct timespec *rTimeSpec);
    int  CNetsTimeUtils_EXPORT_API  TaskDelayTill(struct timespec *end,  void* mutex, void* condition_variable);
    void  CNetsTimeUtils_EXPORT_API  TaskDelay(uint64_t nanosec);
    unsigned CNetsTimeUtils_EXPORT_API DiffTwoTimespecs(struct timespec *lTimeSpec,struct timespec *rTimeSpec);
#ifdef __cplusplus
} /* only need to export C interface if used by C++ source code*/
#endif

#endif /*CNETS_TIMEUTILS_H_*/