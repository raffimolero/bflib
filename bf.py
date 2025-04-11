import traceback
import re
import math


class Options:
    DEBUG = True
    MINIFY = False


def dbg(text: str):
    return f"\n{{DEBUG}} ({text}) {{/DEBUG}}\n" if Options.DEBUG else ""


def log(text: str, pos: int = 0, preserve: bool = True, starting_val: int = 0):
    return dbg(
        f"""
            log {bf_escape(text)}
            {move(pos)}
            {puts(text, preserve, starting_val)}
            {move(-pos)}
       """
    )


BF = "[]+-,.<>"
# BF_RE = "".join(f"\\{c}" for c in BF)
BF_NAMES = {
    ord("["): "{OPEN}",
    ord("]"): "{CLOSE}",
    ord("+"): "{PLUS}",
    ord("-"): "{MINUS}",
    ord(","): "{COMMA}",
    ord("."): "{DOT}",
    ord("<"): "{LEFT}",
    ord(">"): "{RIGHT}",
    ord("{"): "{{",
    ord("}"): "}}",
}


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


def bf_escape(text: str) -> str:
    return repr(text.translate(BF_NAMES))


def bf_escape_num(num: int) -> str:
    return str(num).replace("-", "~")


def bf_escape_chr(num: int) -> str:
    out = bf_escape_num(num)
    out += BF_NAMES.get(num, bf_escape_num(repr(chr(num))))
    return out


def setup(pos: int, data: list[int], pad: int = 8) -> str:
    return f"""
        SETUP: (
            {move(pad)}
            {"".join(f"{add(n)}> {bf_escape_chr(n)}\n" for n in data)}
            {move(pos - len(data))}
        )
    """


def move(amount: int) -> str:
    amount = _wrap(amount)
    if amount > 0:
        return ">" * amount
    if amount < 0:
        return "<" * -amount
    return ""


def add(amount: int, pos: int = 0) -> str:
    amount = _wrap(amount)
    if amount > 0:
        return f'{move(pos)}{"+" * amount}{move(-pos)}'
    if amount < 0:
        return f'{move(pos)}{"-" * -amount}{move(-pos)}'
    return ""


def clone_to(*args) -> str:
    """
    desc:
        clones the current cell to a set of other specific locations, possibly with a multiplier.

    example:
        before: (@N 0 0   0)
        {clone_to(1, 3, (2, 5))}
        after:  (@0 N N*5 N)
    """
    out = "[- clone ("
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
        out += add(target_factor)
        out += f" *{bf_escape_num(target_factor)}\n"
        current_pos = target_pos
    out += move(0 - current_pos) + "\n"
    return out + ") ]"


def reset(amount: int = 0) -> str:
    """
    desc:
        sets the current cell to a specified amount.

    before: (@?)
    after:  (@amount)
    """
    return "[-]" + add(amount)


def puts(text: str, preserve: bool = True, starting_val: int = 0) -> str:
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


# TODO: more precise contract
def ifelse_preserve_rr(
    posFlagFalse: int,
    posFlagTrue: int,
    actTrue: str,
    actFalse: str,
) -> str:
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
        [{r}{r}- if (
            {actTrue}
        ) {l}]{r}+[- else (
            {actFalse}
        ) {r}]{l}{l}
    """


def if_preserve_rl(
    posFlagFalse: int,
    posZeroed: int,
    actTrue: str,
) -> str:
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
        [{r} if (
            {actTrue}
        ) ]{l}[{l}]
    """


def ifelse_preserve_rl(
    posFlagFalse: int,
    posZeroed: int,
    actTrue: str,
    actFalse: str,
) -> str:
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
        )}{r}{r}[- else (
            {actFalse}
        ) ]
    """


def switch_map(
    pos: int, cases: dict[int, int], default: int | str | None = None
) -> str:
    """
    desc:
        consuming switch case that maps one set of values to another.

    before: (@X 0)
    after: (@0 Y)
    """

    items = sorted((_char_or_int(k), v) for k, v in cases.items())

    out = ""
    cur_k, cur_v = 0, 0
    for k, v in items:
        out += f"""
            {add(v - cur_v, pos)}{add(cur_k - k)}[ case {bf_escape_chr(k)} = {bf_escape_chr(v)}
        """
        cur_k, cur_v = k, v

    if default == None:
        default = cur_v
    if isinstance(default, int):
        default = f"""
            default (
                {add(-cur_v, pos)}
                [-]
            )
        """

    return out + default + "]" * len(items)


def switch_consume(
    posFlag: int,
    cases: dict[int, str],
    default: str = "[-]",
) -> str:
    """
    desc:
        consuming switch case.

    before: (@X 0)
    default:
        before: (@? 0)
        {default}
        after:  (@0 0)
    case X:
        before: (0 @0)
        {case}
        after:  (0 @0)
    after:  (0 @0)
    """
    assert len(cases) > 0

    r = move(posFlag)
    l = move(-posFlag)

    out = f"{r}+{l} switch @0 with @{bf_escape_num(posFlag)} as scratch"

    items = sorted((_char_or_int(k), v) for k, v in cases.items())

    out += "("
    cur = 0
    for k, _ in items:
        out += f"{add(cur - k)}[ case {bf_escape_chr(k)}\n"
        cur = k
    out += ")"

    out += f"""
        {r}-{l} default (
            {default}
        ) ]==
    """.strip()

    out += f"{l}]".join(
        f"""
        {r}[- case {bf_escape_chr(k)} (
            {v}
        ) ]
    """.strip()
        for k, v in reversed(items)
    )

    return out


def switch_preserve_rl(
    posTrueL: int,
    posZeroL: int,
    posZeroR: int,
    cases: dict[str | int, str],
    default: str = ">",
) -> str:
    """
    desc:
        non-consuming switch-case.

    before: (T ? @X ?)
    default:
        before: (? ? @? ?)
        {default}
        after:  (? 0 ? @0)
    case X:
        before: (@T ? 0 ?)
        {case}
        after:  (T @0 X 0)
    after:  (T 0 @Y 0)
    """
    assert len(cases) > 0
    assert posZeroL == -posZeroR
    assert posTrueL == posZeroL * 2

    r = move(posZeroR)
    l = move(-posZeroR)

    out = f"switch preserving @0: @{bf_escape_num(posZeroL)} and @{bf_escape_num(posZeroR)} assumed zero; @{bf_escape_num(posTrueL)} assumed nonzero"

    items = sorted((_char_or_int(k), v) for k, v in cases.items())
    deltas = []

    out += "("
    cur = 0
    for k, _ in items:
        deltas.append(k - cur)
        out += f"{add(cur - k)}[ case {bf_escape_chr(k)}\n"
        cur = k
    out += ")"

    out += f"""
        default (
            {default}
        ) ]===
    """.strip()

    out += f"{r}]".join(
        f"""
        {l}{l}[ case {bf_escape_chr(k)} (
            {v}
        ) ]{r}{add(d)}
    """.strip()
        for (k, v), d in zip(reversed(items), reversed(deltas))
    )

    return out


def bf_format(text: str, indent: str = "    ") -> str:
    """
    formats code based on parentheses
    """
    out = ""
    space_buf = 0
    empty_line = True
    depth = 0
    for c in text:
        if c == " ":
            space_buf += 1
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
            space_buf = 0
            out += indent * depth
            empty_line = False
        else:
            out += " " * space_buf
            space_buf = 0
        out += c
    if Options.MINIFY:
        out = bf_minify(out)
    return out


def bf_minify(text: str, width: int = 80) -> str:
    out = ""
    line_length = 0
    for c in text:
        if c in BF:
            if line_length >= width:
                out += "\n"
                line_length = 0
            out += c
            line_length += 1
    return out
