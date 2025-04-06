from bf import *

# res = add(-4) + cond_preserve(
#     1, 2,
#     bf_print('Hello', True, -1),
#     bf_print('World!', True, 0),
# )
res = f"""
    {move(8)}
    -
    >+
    [
        >>
        >,
        {switch(
            1,
            {c: f'<<{add(i + 1)}>>' for i, c in enumerate('><+-[].,')} | {'!': '', 0: ''},
            reset() + '<<'
        )}
        <
    ]
    >
    +[<<+] seek to instruction pointer
    >[
        {clone_to(-1, -3)}
        {move(-1)}
        {clone_to(1)}
        {move(-2)}
        {switch(
            2,
            {
                1: puts('right'),
                2: puts('left'),
                3: puts('add'),
                4: puts('sub'),
                5: puts('open'),
                6: puts('close'),
                7: puts('out'),
                8: puts('in'),
            }
        )}
        {move(5)}
    ]

"""
print(bf_format(res))


# res = add(20) + clone_to(1, 3, (2, 5)) * MotionFactor(-2)
# print(bf_format(res))
