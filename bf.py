import traceback
import re
import math

BF = "[]+-,.<>"
BF = "".join(f"\\{c}" for c in BF)


class MotionFactor:
    """
    multiplies all motions within some code so that it's either reflected or travels further
    useful for managing arrays of alternating marker-data-marker-data
    """

    def __init__(self, factor: int):
        self.factor = factor
        self.translation = {
            ord("<"): move(-self.factor),
            ord(">"): move(self.factor),
        }

    def __rmul__(self, lhs: str):
        return lhs.translate(self.translation)


def _wrap(amount: int):
    """
    wraps a value to within signed 8 bit integer range
    """
    return (amount + 128) % 256 - 128


def _char_or_int(val: str | int):
    if isinstance(val, int):
        return val
    if isinstance(val, str) and len(val) == 1:
        return ord(val)
    raise "non integer value passed to _int converter"


def setup(pos: int, data: list[int], pad: int = 8):
    return (
        move(pad)
        + "\n"
        + "".join(f"{add(_wrap(n))}>\n" for n in data)
        + move(pos - len(data))
    )


def move(amount: int):
    amount = _wrap(amount)
    if amount > 0:
        return ">" * amount
    if amount < 0:
        return "<" * -amount
    return ""


def add(amount: int):
    amount = _wrap(amount)
    if amount > 0:
        return "+" * amount
    if amount < 0:
        return "-" * -amount
    return ""


def clone_to(*args):
    """
    desc:
        clones the current cell to a set of other specific locations, possibly with a multiplier.

    example:
        before: (@N 0 0   0)
        {clone_to(1, 3, (2, 5))}
        after:  (@0 N N*5 N)
    """
    out = "[- ("
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
        out += add(target_factor) + "\n"
        current_pos = target_pos
    out += move(0 - current_pos) + "\n"
    return out + ") ]"


def reset(amount: int = 0):
    """
    desc:
        sets the current cell to a specified amount.

    before: (@?)
    after:  (@amount)
    """
    return "[-]" + add(amount)


def puts(text: str, preserve: bool = True, starting_val: int = 0):
    """
    desc:
        prints out some text using one cell. not very efficient but gets the job done.
        set preserve=True to keep the starting_val after printing.

    before: (@starting_val)
    after:  (@starting_val) if preserve else (@?)
    """
    out = ""
    current_val = starting_val
    for c in text:
        target_val = ord(c)
        out += add(target_val - current_val)
        out += ".\n"
        current_val = target_val
    if preserve:
        out += add(starting_val - current_val) + "\n"
    return out


def ifelse_preserve_rr(
    posFlagFalse: int,
    posFlagTrue: int,
    actTrue: str,
    actFalse: str,
):
    """
    desc:
        performs an if-else check on the current cell.
        executes actTrue when it's nonzero, else actFalse when zero.
        actTrue and actFalse begin at @posFlagTrue, and they must not modify @posFlagFalse.
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
    r = move(posFlagFalse)
    l = move(-posFlagFalse)
    return f"""
        [{r}{r}- (
            {actTrue}
        ) {l}]{r}+[- (
            {actFalse}
        ) {r}]{l}{l}
    """


def if_preserve_rl(
    posFlagFalse: int,
    posZeroed: int,
    actTrue: str,
):
    """
    desc:
        performs an if- check on the current cell.
        executes actTrue when it's nonzero, else nothing.
        actTrue begins at @posFlagFalse, and must set it to zero.
        ends at the other side.

    before: (0 @X ?)
    if X != 0:
        before: (0 X @?)
        {actTrue}
        after:  (0 X @0)
    after:  (@0 X 0)
    """
    assert posFlagFalse * -1 == posZeroed
    r = move(posFlagFalse)
    l = move(-posFlagFalse)
    return f"""
        [{r} (
            {actTrue}
        ) ]{l}[{l}]
    """


def ifelse_preserve_rl(
    posFlagFalse: int,
    posZeroed: int,
    actTrue: str,
    actFalse: str,
):
    """
    desc:
        performs an if-else check on the current cell.
        executes actTrue when it's nonzero, else actFalse when zero.
        actTrue and actFalse begin at @posFlagFalse, and they must not modify @posFlagFalse or @posZeroed.
        modifications to X are not allowed.

    before: (0 @X 0)
    if X != 0:
        before: (0 X @0)
        {actTrue}
        after:  (0 X @0)
    else: # X == 0
        before: (0 @0 0)
        {actFalse}
        after:  (0 @0 0)
    after:  (@0 X 0)
    """
    assert posFlagFalse * -1 == posZeroed
    r = move(posFlagFalse)
    l = move(-posFlagFalse)

    return f"""
        {r}+{l}{if_preserve_rl(
            posFlagFalse, posZeroed,
            '-' + actTrue,
        )}{r}{r}[- (
            {actFalse}
        ) ]
    """


def switch(
    posFlag: int,
    cases: dict[str | int, str],
    default: str = reset(),
):
    """
    desc:
        consuming switch case.

    before: (@X 0)
    case X:
        before: (0 @0)
        {case}
        after:  (0 @0)
    default:
        before: (@? 0)
        {default}
        after:  (@0 0)
    after:  (@0 0)
    """

    r = move(posFlag)
    l = move(-posFlag)

    out = f"{r}+{l}"

    items = sorted((_char_or_int(k), v) for k, v in cases.items())

    out += "("
    cur = 0
    for k, _ in items:
        out += f"{add(cur - k)}[\n"
        cur = k
    out += ")"

    out += f"""
        {r}-{l} (
            {default}
        ) ]==
    """.strip()

    out += f"{l}]".join(
        f"""
        {r}[- (
            {v}
        ) ]
    """.strip()
        for _, v in reversed(items)
    )

    return out + l


def switch_preserve_rl(
    posFlag: int,
    cases: dict[str | int, str],
    default: str = reset(),
):
    """
    desc:
        non-consuming switch case.

    """
    raise "not worth it. probably better to just clone twice and consume the copy, which isn't implemented here yet."


def bf_format(text: str, indent: str = "    "):
    """
    formats code based on parentheses
    """
    out = ""
    empty_line = True
    depth = 0
    for c in text:
        if c == " ":
            continue
        if c == "(":
            depth += 1
            c = "\n"
        if c == ")":
            depth -= 1
            c = "\n"
        if c == "\n":
            if empty_line:
                continue
            empty_line = True
            out += c
            continue
        if empty_line:
            out += indent * depth
            empty_line = False
        out += c
    return out
