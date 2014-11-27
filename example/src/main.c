#include "../include/timeUtils.h"
#include <stdio.h>

int main(){
    printf("-- CNets: Time Utils Tests: Test Delay ---\n");
    int i;
    for(i=0; i<2; i++){
        uint64_t curtime = CurTimeNanosec();
        uint32_t curtime_sec = (uint32_t)(curtime/1000000000L);
        uint32_t curtime_nanosec = (uint32_t)(curtime - (uint64_t)curtime_sec*1000000000L);
        printf("%d %d\n",curtime_sec, curtime_nanosec);
        TaskDelay(1000000000L);
    }
    printf("-- CNets: Time Utils Tests Ending---\n");
    return 0;
}
