#include <stdio.h>
#define GLEW_STATIC
#define GLEW_BUILD
#include "GL/glew.h"

int main (){
  glewGetString(GLEW_VERSION);
  return 0;
}
