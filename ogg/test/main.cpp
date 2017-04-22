#include "ogg/ogg.h"
#include <stdio.h>

int main (){
	
	ogg_sync_state og;
	int result = ogg_sync_init(&og);
	printf("OGG sync init result: %d\n\r", result);
  
}
