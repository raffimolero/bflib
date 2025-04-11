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

RIGHT = op(">+>")
LEFT = op("<-<")
ADD = op("+")
SUB = op("-")
OPEN = f"""
    >>[>>]{log('[')}<
    [< (
        [<<] TRUE
        {log(' T\n')}
        >{add(-5)}
    ) ]<[ (
        [<<] FALSE seek
        {log(' F...\n')}
        >>-
        {move(-2)}
        +[(
            >>>
            >-<
            {add(-5)}[
            {add(-1)}[(
                {add(6)}
                >
            )]===<<[(
                >>{add(6)}
                <<<-
                >>
            )]>>]<<[(
                >>{add(5)}
                <<<+
                >>
            )]
            {move(-2)}{clone_to(2)}{move(2)}
        )]
        >>+<<
        >{add(-5)}
        <
    ) ]
    >{add(5)}
    >-
"""
CLOSE = f"""
    >>[>>]{log(']')}<
    [< (
        [<<] TRUE seek
        {log(' T...\n')}
        {move(-4)} 
        +[(
            >>>
            {add(-5)}[
            {add(-1)}[(
                {add(6)}
                >
            )]===<<[(
                >>{add(6)}
                <<<+
                >>
            )]>>]<<[(
                >>{add(5)}
                <<<-
                >>
            )]
            >>+
            {move(-4)}{clone_to(-2)}{move(-2)}
        )]
        >>>>>{add(-5)}
    ) ]<[ (
        [<<] FALSE
        {log(' F\n')}
        >{add(-5)}<
    ) ]
    >{add(5)}
    >-
"""
OUT = op(".")
IN = op(",")


ENCODING = {ord(c): i for i, c in enumerate("!><+-[].,")} | {
    0: 0,
}

# at this point, pointer is at the previous instruction
# +1 to the last free space
# +3 to the nearest marker
INSTRUCTIONS = {
    1: RIGHT,
    2: LEFT,
    3: ADD,
    4: SUB,
    5: OPEN,
    6: CLOSE,
    7: OUT,
    8: IN,
}

res = f"""
    {move(2)}
    -
    >+
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
            INSTRUCTIONS
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
