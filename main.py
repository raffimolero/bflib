import traceback
import re
import math

BF = '[]+-,.<>'
BF = ''.join(f'\\{c}' for c in BF)

class MotionFactor:
    """
    multiplies all motions within some code so that it's either reflected or travels further
    useful for managing arrays of alternating marker-data-marker-data
    """

    def __init__(self, factor: int):
        self.factor = factor
        self.translation = {
            ord('<'): move(-self.factor),
            ord('>'): move(self.factor),
        }

    def __rmul__(self, lhs: str):
        return lhs.translate(self.translation)

def _wrap(amount: int):
    """
    wraps a value to within signed 8 bit integer range
    """
    return (amount + 128) % 256 - 128

def move(amount: int):
    amount = _wrap(amount)
    if amount > 0:
        return '>' * amount
    if amount < 0:
        return '<' * -amount
    return ''

def add(amount: int):
    amount = _wrap(amount)
    if amount > 0:
        return '+' * amount
    if amount < 0:
        return '-' * -amount
    return ''

def clone_to(*args):
    """
    desc:
        clones the current cell to a set of other specific locations, possibly with a multiplier.
    
    example:
        before: (@N 0 0   0)
        {clone_to(1, 3, (2, 5))}
        after:  (@0 N N*5 N)
    """
    out = '[-(\n'
    current_pos = 0
    def normalize(item):
        match item:
            case pos, mul:
                return pos, mul
            case pos:
                return pos, 1
    args = sorted(map(normalize, args))
    for target_pos, target_factor in args:
        out += move(target_pos - current_pos)
        out += add(target_factor) + '\n'
        current_pos = target_pos
    out += move(0 - current_pos) + '\n'
    return out + ')]'

def set(amount: int = 0):
    """
    desc:
        sets the current cell to a specified amount.

    before: (@?)
    after:  (@amount)
    """
    return '[-]' + add(amount)

def bf_print(text: str, starting_val: int = 0, preserve: bool = False):
    """
    desc:
        prints out some text using one cell. not very efficient but gets the job done.
        set preserve=True to keep the starting_val after printing.

    before: (@starting_val)
    after:  (@starting_val) if preserve else (@?)
    """
    out = ''
    current_val = starting_val
    for c in text:
        target_val = ord(c)
        out += add(target_val - current_val)
        out += '.\n'
        current_val = target_val
    if preserve:
        out += add(starting_val - current_val) + '\n'
    return out

def cond_preserve(
    posFlagFalse: int,
    posFlagTrue: int,
    actTrue: str,
    actFalse: str,
):
    """
    desc:
        actTrue and actFalse begin at @+1, and they must not modify @posFlag.
        modifications to X are actually allowed and will be preserved (labeled Y).

    before: (@X 0 0)
    if X != 0: 
        before: (X @0 0)
        {actTrue}
        after:  (Y @? 0)
    else: # X == 0
        before: (0 @0 -1)
        {actFalse}
        after:  (Y @? -1)
    after:  (@Y ? 0)
    """
    assert posFlagFalse * 2 == posFlagTrue
    return f"""
        [{move(posFlagFalse * 2)}- (
            {actTrue}
        ) {move(-posFlagFalse)}]{move(posFlagFalse)}+[- (
            {actFalse}
        ) {move(posFlagFalse)}]{move(-posFlagFalse * 2)}
        """

def bf_format(text: str, indent: str = '  '):
    """
    formats code based on parentheses
    """
    out = ''
    empty_line = True
    depth = 0
    for c in text:
        if c == ' ':
            continue
        if c == '\n':
            if empty_line:
                continue
            empty_line = True
            out += c
            continue
        if c == '(':
            depth += 1
            # continue
        if c == ')':
            depth -= 1
            # continue
        if empty_line:
            out += indent * depth
            empty_line = False
        out += c
    return out


res = add(-4) + cond_preserve(
    1, 2,
    bf_print('Hello', -1, True),
    bf_print('World!', 0, True),
)
print(bf_format(res))



# res = add(20) + clone_to(1, 3, (2, 5)) * MotionFactor(-2)
# print(bf_format(res))