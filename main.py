from bf import *

Options.DEBUG = False

# res = f"""
#     {setup(+4, [2, 0, 2, 0, 2, 0, 5, 0])}
#     {switch_preserve_rl(
#         -2, -1, 1,
#         {1: puts('ONE'), 2: puts('TWO')},
#     )}
# """
# print(bf_format(res))
# exit()


def op(operation: str):
    return f"""
        >>[>>]{log(operation[0])}< (
            {operation}
        ) <[<<]>>-
    """


# res = f"""
#     {setup(+6 - 5, [2, 0, 2, 0, 2, 0, 5, 1, 10, 1, 5, 1, 6, 1, 6, 1, 6, 1, 2, 1, 2, 1])}
#     +[(
#         {move(5)}
#         >-<
#         {add(-5)}[
#         {add(-1)}[(
#             {add(6)}
#             >
#         )]===<<[(
#             >>{add(6)}
#             <<<<<-
#             >>>>
#         )]>>]<<[(
#             >>{add(5)}
#             <<<<<+
#             >>>>
#         )]
#         {move(-4)}
#         {clone_to(2)}
#         {move(2)}
#     )]
#     {move(4)}
# """

# print(bf_format(res))
# exit()

# at this point, pointer is at the previous instruction
# +1 to the last free space
# +3 to the nearest marker
INSTRUCTIONS = {
    "[": "",
    "]": "",
    ">": op(">+>"),
    "<": op("<-<"),
    "+": op("+"),
    "-": op("-"),
    ".": op("."),
    ",": op(","),
}

OPEN = 1
CLOSE = 2
INSTRUCTIONS[
    "["
] = f"""
    >>[>>]{log('[')}<
    [< (
        [<<] TRUE
        {log(' T\n')}
        >{add(-OPEN)}
    ) ]<[ (
        [<<] FALSE seek
        {log(' F...\n')}
        >>-
        {move(-CLOSE)}
        +[(
            >>>
            >-<
            {add(-OPEN)}[
            {add(OPEN - CLOSE)}[(
                {add(CLOSE)}
                >
            )]===<<[(
                >>{add(CLOSE)}
                <<<-
                >>
            )]>>]<<[(
                >>{add(OPEN)}
                <<<+
                >>
            )]
            {move(-2)}{clone_to(2)}{move(2)}
        )]
        >>+<<
        >{add(-OPEN)}
        <
    ) ]
    >{add(OPEN)}
    >-
"""
INSTRUCTIONS[
    "]"
] = f"""
    >>[>>]{log(']')}<
    [< (
        [<<] TRUE seek
        {log(' T...\n')}
        {move(-4)} 
        +[(
            >>>
            {add(-OPEN)}[
            {add(OPEN - CLOSE)}[(
                {add(CLOSE)}
                >
            )]===<<[(
                >>{add(CLOSE)}
                <<<+
                >>
            )]>>]<<[(
                >>{add(OPEN)}
                <<<-
                >>
            )]
            >>+
            {move(-4)}{clone_to(-2)}{move(-2)}
        )]
        >>>>>{add(-OPEN)}
    ) ]<[ (
        [<<] FALSE
        {log(' F\n')}
        >{add(-OPEN)}<
    ) ]
    >{add(OPEN)}
    >-
"""


ENCODING = {ord(c): i + 1 for i, c in enumerate(INSTRUCTIONS.keys())} | {
    ord("!"): 0,
    0: 0,
}


res = f"""
    {move(2)}
    -
    >{add(3)}
    [(
        >>
        >,
        {dbg('.')}
        {switch_map(
            -1,
            ENCODING,
            '[[-]<]'
        )}
        <
    )]
    >
    +[<<+]
    >[(
        {clone_to(-1, -3)}
        {move(-1)}
        {clone_to(1)}
        {move(-2)}
        {switch_consume(
            2,
            {i + 1: v for i, v in enumerate(INSTRUCTIONS.values())},
        )}
        {move(3 - 2)}
    )]

"""
out = bf_format(res)
if not Options.DEBUG:
    out = bf_minify(out)

print(out)

with open("bf2.bf", "w") as file:
    file.write(out)
