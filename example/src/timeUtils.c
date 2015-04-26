#include "../timeUtils.h"
#include <pthread.h>
#include <stdio.h>
#if !defined __MINGW32__ && defined _WIN32
    int gettimeofday(struct timeval *tv, struct timezone *tz) {
      FILETIME ft;
      unsigned __int64 tmpres = 0;
      static int tzflag;
     
      if (NULL != tv)
      {
        GetSystemTimeAsFileTime(&ft);
     
        tmpres |= ft.dwHighDateTime;
        tmpres <<= 32;
        tmpres |= ft.dwLowDateTime;
     
         /*converting file time to unix epoch*/
         tmpres /= 10; /*convert into microseconds*/
         tmpres -= DELTA_EPOCH_IN_MICROSECS;
        tv->tv_sec = (long)(tmpres / 1000000UL);
        tv->tv_usec = (long)(tmpres % 1000000UL);
      }
     
      if (NULL != tz)
      {
        if (!tzflag)
        {
          _tzset();
          tzflag++;
        }
        long timezone;
        _get_timezone(&timezone);
        tz->tz_minuteswest = timezone / 60;
        int daylight;
        _get_daylight(&daylight);
        tz->tz_dsttime = daylight;
      }
      return 0;
    }
#endif

/**--------------------------------------------
Function: CurTimeNanosec()
Purpose: gets current time in nanosecs
Returns: UNSINGED64
--------------------------------------------*/
uint64_t CurTimeNanosec(){
    struct timeval currenttime;
    uint64_t time;
    gettimeofday( &currenttime, NULL );
    time = (uint64_t)currenttime.tv_sec*(uint64_t)1000000000L + (uint64_t)currenttime.tv_usec*(uint64_t)1000L;
    return time;
}

/**--------------------------------------------
Function: GetTimespecDelay()
Purpose: gets: time = current time + nanosec
Returns: timespec
--------------------------------------------*/
struct timespec  GetTimespecDelay(uint64_t nanosec){
    struct timeval  currenttime;
    struct timespec wait;
    long dt_sec, dt_nsec;

    // Set timeout time, relatvie to current time
    gettimeofday( &currenttime, NULL );
    dt_sec  = (long) (nanosec/(uint64_t)1000000000L);
    dt_nsec = (long) (nanosec - (uint64_t)dt_sec* 1000000000L);
    wait.tv_nsec = (currenttime.tv_usec * 1000L + dt_nsec);
    if( wait.tv_nsec > 1000000000L )
    {
        wait.tv_nsec -= 1000000000L;
        dt_sec ++;
    }
    wait.tv_sec  = currenttime.tv_sec + dt_sec;
    return wait;
}

/**--------------------------------------------
Function: CompareTwoTimespecs()
Purpose: compares time in the parameter to the current time 
Returns: if(current<timeSpec) return -1; if(current==timeSpec) return 0; if(current>timeSpec) return 1;
--------------------------------------------*/
int  CompareTimespec(struct timespec *timeSpec){
    struct timeval  currenttime;
    gettimeofday( &currenttime, NULL );
    struct timespec lTimeSpec;
    lTimeSpec.tv_sec = currenttime.tv_sec;
    lTimeSpec.tv_nsec = currenttime.tv_usec*1000L;
    return CompareTwoTimespecs(&lTimeSpec,timeSpec);
}

/**--------------------------------------------
Function: CompareTwoTimespecs()
Purpose: compares times. 
Returns: if(left<right) return -1; if(left==right) return 0; if(left>right) return 1;
--------------------------------------------*/
int  CompareTwoTimespecs(struct timespec *lTimeSpec, struct timespec *rTimeSpec){
    if(lTimeSpec->tv_sec == rTimeSpec->tv_sec && lTimeSpec->tv_nsec == rTimeSpec->tv_nsec){return 0;}
    if(lTimeSpec->tv_sec >  rTimeSpec->tv_sec){return 1;} 
    if(lTimeSpec->tv_sec == rTimeSpec->tv_sec && lTimeSpec->tv_nsec >  rTimeSpec->tv_nsec){return 1;}
    return -1;
}

/**--------------------------------------------
Function: CompareTwoTimespecs()
Purpose: compares times. 
Returns: 
--------------------------------------------*/
unsigned DiffTwoTimespecs(struct timespec *lTimeSpec,struct timespec *rTimeSpec){
    uint64_t diff;
    diff = (uint64_t)lTimeSpec->tv_sec*(uint64_t)1000000000L + (uint64_t)lTimeSpec->tv_nsec;
    diff -= (uint64_t)rTimeSpec->tv_sec*(uint64_t)1000000000L + (uint64_t)rTimeSpec->tv_nsec;
    return (unsigned)diff/1000000;
}

/**--------------------------------------------
Function: TaskDelayTill()
Purpose: delay the current thread from execution until time is reached or condition variable 
is fired
Params: end * pointer to the final time, until we are waiting for
        condition_variable* pointer to the pthreads condition variable, 
        mutex* pointer to pthreads mutex. mutex should be locked before call and it will be locked after call
Returns: TRUE if successful
		or FALSE if timeout in condition variable wait
--------------------------------------------*/
int TaskDelayTill(struct timespec *end,  void* condition_variable, void* mutex){
    if(!end || !condition_variable || !mutex){return 0;}
    if(CompareTimespec(end) >= 0 ){return 0;}
    int error = pthread_cond_timedwait((pthread_cond_t*)condition_variable, (pthread_mutex_t*)mutex, end);
    if(error == ETIMEDOUT || error == EINVAL || error == EPERM)
        return 0;
    else
        return 1;
}

/**--------------------------------------------
Function: TaskDelay()
Purpose: delay the current thread from execution
Returns: void
--------------------------------------------*/
void TaskDelay(uint64_t nanosec){
    struct timespec tsWait;
    tsWait.tv_sec  = ((uint64_t)nanosec/(uint64_t)1000000000L);
    tsWait.tv_nsec = (long)((uint64_t)nanosec - (uint64_t)tsWait.tv_sec*(uint64_t)1000000000L);
    #ifdef _WIN32
    pthread_delay_np(&tsWait);
    #else
    nanosleep(&tsWait,NULL);/*null for now, but in the future it should be used for waiting 
    if the pause has been interrupted by a signal that was delivered to the thread. 
    The remaining sleep time has been written into *rem so that the thread can easily 
    call nanosleep() again and continue with the pause.*/
    #endif
}
