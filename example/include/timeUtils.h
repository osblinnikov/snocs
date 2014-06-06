#ifndef CNETS_TIMEUTILS_H_
#define CNETS_TIMEUTILS_H_

#include "Exports.h"
#include "../../types/include/types.h"

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
    uint64_t CNetsTimeUtilsExportsAPI   CurTimeNanosec();
    struct timespec CNetsTimeUtilsExportsAPI  GetTimespecDelay(uint64_t nanosec);
    int  CNetsTimeUtilsExportsAPI  CompareTimespec(struct timespec *timeSpec);
    int  CNetsTimeUtilsExportsAPI  CompareTwoTimespecs(struct timespec *lTimeSpec,struct timespec *rTimeSpec);
    int  CNetsTimeUtilsExportsAPI  TaskDelayTill(struct timespec *end,  void* mutex, void* condition_variable);
    void  CNetsTimeUtilsExportsAPI  TaskDelay(uint64_t nanosec);
    unsigned CNetsTimeUtilsExportsAPI DiffTwoTimespecs(struct timespec *lTimeSpec,struct timespec *rTimeSpec);
#ifdef __cplusplus
} /* only need to export C interface if used by C++ source code*/
#endif

#endif /*CNETS_TIMEUTILS_H_*/