message(STATUS "-------find-------")
FIND_PATH(HELLO_INCLUDE_DIR hello.h C:/Users/Administrator/Desktop/Test/third_party/hello)
FIND_LIBRARY(HELLO_LIBRARY hello C:/Users/Administrator/Desktop/Test/third_party/hello)

message(STATUS ${HELLO_INCLUDE_DIR})
message(STATUS ${HELLO_LIBRARY})

IF(HELLO_INCLUDE_DIR AND HELLO_LIBRARY)
  SET(HELLO_FOUND TRUE)
ENDIF(HELLO_INCLUDE_DIR)
message(STATUS "-------find end-------")
