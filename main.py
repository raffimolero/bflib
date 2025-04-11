from bf import *

Options.DEBUG = False
Options.MINIFY = True

res = f"""
    {switch_preserve_rl(
        -2, -1, 1,
        {
            1: '> ONE',
            2: '> TWO',
            3: '> THREE'
        },
    )}
"""
# print(bf_format(res))
# exit()


def op(operation: str):
    return f"""
        (@T 0 0 1 Y 1)
        >>>->>[>>]{log(operation[0])}< (
            {operation}
        ) <[<<]<<
        (T @0 0 0 Y 1)
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
    >>>->>[>>]{log('[')}<
    [ (
        <[<<]< TRUE
        {log(' T\n')}
    ) ]<[ (
        [<<]< FALSE seek
        {log(' F...\n', 1)}
        {add(OPEN)}<
        +[(
            >>>
            >-<
            {switch_preserve_rl(
                -2, -1, 1,
                {
                    OPEN: '<+>>',
                    CLOSE: '<->>',
                },
            )}
            <<<
            [->>+<<]>>
        )]
        >-<
    ) ]
"""
INSTRUCTIONS[
    "]"
] = f"""
    >>>[>>]{log(']')}<
    [ (
        <[<<]> TRUE seek
        {log(' T...\n')}
        {add(CLOSE)}
        <<
        <+[ (
            [-<<+>>]>
            {switch_preserve_rl(
                -2, -1, 1,
                {
                    OPEN: '<->>',
                    CLOSE: '<+>>',
                },
            )}
            >+<
            <<<
        ) ]
        >>>{add(-OPEN)}
    ) ]<[ (
        [<<] FALSE
        {log(' F\n')}
        >{add(CLOSE - OPEN)}<
    ) ]
    >{add(OPEN - CLOSE)}
    >-<<
"""


ENCODING = {ord(c): i + 1 for i, c in enumerate(INSTRUCTIONS.keys())} | {
    ord("!"): 0,
    0: 0,
}

# EXECUTE = f"""
#     {clone_to(-1, -3)}
#     {move(-1)}
#     {clone_to(1)}
#     {move(-2)}
#     {switch_consume(
#         2,
#         {i + 1: v for i, v in enumerate(INSTRUCTIONS.values())},
#     )}
#     {move(3 - 2)}
# """
EXECUTE = f"""
    {switch_preserve_rl(
        -2, -1, 1,
        {i + 1: v for i, v in enumerate(INSTRUCTIONS.values())},
    )}
"""
# print(bf_format(EXECUTE))
# exit()

res = f"""
    {move(2)}
    ->{log('reading input\n')}+
    [(
        >>
        >,
        {dbg('.')}
        {switch_map(
            -1,
            ENCODING,
            '[[-]<]',
        )}
        <
    )]
    >
    +[<<+]
    {log('\nexecuting\n')}
    >>->[(
        (t 0 @X 1)
        {EXECUTE}
        (t 0 @X 0 Y 1)
        >>
    )]

"""
out = bf_format(res)

print(out)

with open("bf2.bf", "w") as file:
    file.write(out)
