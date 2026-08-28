function(via_argn)
  cmake_parse_arguments(A "" "TEXT" "" ${ARGN})
  message(STATUS "ARGN:       TEXT=[${A_TEXT}]  решта=[${A_UNPARSED_ARGUMENTS}]")
endfunction()

function(via_argv)
  cmake_parse_arguments(PARSE_ARGV 0 B "" "TEXT" "")
  message(STATUS "PARSE_ARGV: TEXT=[${B_TEXT}]  решта=[${B_UNPARSED_ARGUMENTS}]")
endfunction()

via_argn(TEXT "a;b")
via_argv(TEXT "a;b")
