#include "GL/glew.h"
#include <iostream>
#include <string>

using namespace std;

int main (void){
	
  string glewVersion = reinterpret_cast<char *>(const_cast<GLubyte*>(glewGetString(GLEW_VERSION)));
  cout << "Using GLEW version " << glewVersion << endl;
  
}
