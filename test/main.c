#include <stdio.h>
#define GLEW_STATIC
#include "GL/glew.h"

int main (){
  glewGetString(GLEW_VERSION);
  return 0;
}
