set_target_properties(<ціль>... PROPERTIES <влас1> <знач1> [<влас2> <знач2>]...)

set_property(TARGET <ціль>...
             [APPEND] [APPEND_STRING]
             PROPERTY <влас> [<знач>...])

get_target_property(<змінна> <ціль> <влас>)

get_property(<змінна> TARGET <ціль>
             PROPERTY <влас>
             [SET | DEFINED | BRIEF_DOCS | FULL_DOCS])

define_property(TARGET PROPERTY <влас> [INHERITED]
                [BRIEF_DOCS <текст>...] [FULL_DOCS <текст>...]
                [INITIALIZE_FROM_VARIABLE <змінна>])
