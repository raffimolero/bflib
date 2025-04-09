from bf import *


# res = f"""
#     {setup(+4, [2, 0, 2, 0, 2, 0, 5, 0])}
#     {ifelse_preserve_rl(
#         3, -3,
#         puts('TRUE'),
#         puts('FALSE'),
#     )}
# """
# print(bf_format(res))
# exit()


def op(operation: str):
    return f"""
        >>[>>]{puts(operation[0])}< (
            {operation}
        ) <
        [<<]>>-
    """


res = f"""
    {setup(+6 - 5, [2, 0, 2, 0, 2, 0, 5, 1, 10, 1, 5, 1, 6, 1, 6, 1, 6, 1, 2, 1, 2, 1])}
    +[(
        {move(5)}
        >-<
        {add(-5)}[
        {add(-1)}[(
            {add(6)}
            >
        )]<<[(
            >>{add(6)}
            <<<<<-
            >>>>
        )]>>]<<[(
            >>{add(5)}
            <<<<<+
            >>>>
        )]
        {move(-4)}
        {clone_to(2)}
        {move(2)}
    )]
    {move(4)}
"""

# print(bf_format(res))
# exit()

RIGHT = op(">+>")
LEFT = op("<-<")
ADD = op("+")
SUB = op("-")
OPEN = f"""
    >>[>>]{puts('[')}<
    [< (
        [<<] TRUE
        {puts(' T\n')}
        >{add(-5)}
    ) ]<[ (
        [<<] FALSE seek
        {puts(' F...\n')}
        >>-
        <<+[(
            >>>
            >-<
            {add(-5)}[
            {add(-1)}[(
                {add(6)}
                >
            )]<<[(
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
    ->>[->>]{puts(']')}<
    <->[<+ (
        +[<<+] TRUE seek
        {puts(' T...\n')}
        <<<<
        +[(
            >>>
            {add(-5)}[
            {add(-1)}[(
                {add(6)}
                >
            )]<<[(
                >>{add(6)}
                <<<+
                >>
            )]>>]<<[(
                >>{add(5)}
                <<<-
                >>
            )]
            >>+
            <<<<
            {clone_to(-2)}{move(-2)}
        )]
        >>>>>{add(-5)}
    ) ]<[+ (
        +[<<+] FALSE
        {puts(' F\n')}
        >{add(-5)}<
    ) ]
    >{add(5)}
    >-
"""
OUT = op(".")
IN = op(",")


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
    {move(8)}
    -
    >+
    [(
        >>
        >,
        {switch(
            1,
            {c: f'<<{add(i + 1)}>>' for i, c in enumerate('><+-[].,')} | {'!': '', 0: ''},
            reset() + '<<'
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
        {switch(
            2,
            INSTRUCTIONS
        )}
        {move(3)}
    )]

"""
print(bf_minify(bf_format(res)))
