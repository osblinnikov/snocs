#ifndef hlsexample_H_
#define hlsexample_H_


#ifdef WITH_INTEL_HLS
	#include "HLS/stdio.h"
#else
	#include <stdio.h>
	#define component
#endif // WITH_INTEL_HLS

void empty();

#endif // hlsexample_H_