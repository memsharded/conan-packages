#include "GL/glew.h"
#include <iostream>
#include <string>

using namespace std;

int main (void){
  GLenum initResult = glewInit();

  if (initResult != GLEW_OK) {
    cout << "Error initialising GLEW (but it doesn't matter)" << endl;
  }
  else {
    string glewVersion = reinterpret_cast<char *>(const_cast<GLubyte*>(glewGetString(GLEW_VERSION)));
    cout << "Using GLEW version " << glewVersion << endl;
  }

}
