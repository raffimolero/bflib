from bf import *

# res = add(-4) + cond_preserve(
#     1, 2,
#     bf_print('Hello', True, -1),
#     bf_print('World!', True, 0),
# )

RIGHT = LEFT = ADD = SUB = OPEN = CLOSE = OUT = IN = ""


def op(operation: str):
    return f"""
        ->>[->>]< (
            {operation}
        ) <
        +[<<+]>>-
    """


RIGHT = op(">>")
LEFT = op("<<")
ADD = op("+")
SUB = op("-")
OPEN = f'>{puts("OPEN")}>>>-'
CLOSE = f'>{puts("CLOSE")}>>>-'
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
    +[<<+] seek to instruction pointer
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
print(bf_format(res))


# res = add(20) + clone_to(1, 3, (2, 5)) * MotionFactor(-2)
# print(bf_format(res))
