-
>+ set first instruction to "right"
[
  >> move to new position
  >, get new raw instruction
  >+<      switch x
  [---------- ---------- ---------- --- case 33 bang
  [---------- case 43 plus
  [- case 44 comma
  [- case 45 minus
  [- case 46 dot
  [---------- ---- case 60 left
  [-- case 62 right
  [---------- ---------- --------- case 91 while
  [-- case 93 end
  [>-<       default
    [-]   must reset or move
    << move 2 back
    ]>[-     case close 6
    <<++++++>>
  ]<]>[-     case open 5
    <<+++++>>
  ]<]>[-     case right 1
    <<+>>
  ]<]>[-     case left 2
    <<++>>
  ]<]>[-     case dot 7
    <<+++++++>>
  ]<]>[-     case minus 4
    <<++++>>
  ]<]>[-     case comma 8
    <<++++++++>>
  ]<]>[-     case plus 3
    <<+++>>
  ]<]>[-     case bang 0
  ]<]>[-     case null 0
  ]
  << check instruction
]
>
+[<<+] seek to instruction pointer
-[
  > switch x
  [- case right
  [- case left
  [- case plus
  [- case minus
  [- case open
  [- case close
  [- case dot
  [- case comma
  [>-<       default should be unreachable
    [-]   must reset or move
  ##]>[-     case comma
    <++++++++> refresh
    +[>>+] seek data pointer
    >,< input
    +[<<-] seek instruction pointer
    >> move to next instruction
  ]<]>[-     case dot
    <+++++++> refresh
  ]<]>[-     case close
    <++++++> refresh
  ]<]>[-     case open
    <+++++> refresh
  ]<]>[-     case minus
    <++++> refresh
  ]<]>[-     case plus
    <+++> refresh
  ]<]>[-     case left
    <++> refresh
  ]<]>[-     case right
    <+> refresh
    >>[->>] seek data pointer
    +[<<+] seek instruction pointer
    >>-
  ]<]>[-     case null
  ]
]

!,.[->+<]!Hello, World!