from bf import *

# res = add(-4) + cond_preserve(
#     1, 2,
#     bf_print('Hello', True, -1),
#     bf_print('World!', True, 0),
# )
res = f"""
    ,[ (
        {switch(
            3,
            {
                '!': puts('bang'),
                '<': puts('left'),
                '>': puts('right'),
                '+': puts('plus'),
                '-': puts('minus'),
                ',': puts('comma'),
                '.': puts('dot'),
                '[': puts('open'),
                ']': puts('close'),
            },
            reset() + puts('default')
        )}
    ) ,]
"""
print(bf_format(res))



# res = add(20) + clone_to(1, 3, (2, 5)) * MotionFactor(-2)
# print(bf_format(res))