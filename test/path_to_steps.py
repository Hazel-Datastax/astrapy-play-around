def path_to_steps(path: str) -> list[str]:
    """
    Splits the 'path' string into segments according to rules:

    1) Start in Regular mode:
       - '.' => boundary => finalize current segment
       - '[' => switch to Quoted mode (discard the '[')
       - any other character => appended to current segment
    2) Quoted mode:
       - ']' => switch back to Regular mode (discard the ']')
       - any other character => appended to current segment
    3) If we reach end of string in Quoted mode => error (no matching ']').
    4) If we reach end of string in Regular mode => finalize current segment (which can be empty).
    """

    segments = []
    buffer = []
    in_quoted_mode = False  # false => regular mode, true => quoted mode

    for c in path:
        if not in_quoted_mode:
            # We are in Regular mode
            if c == '.':
                # boundary => finalize current buffer
                segments.append("".join(buffer))
                buffer.clear()
            elif c == '[':
                # switch to Quoted mode; do not add '[' to buffer
                in_quoted_mode = True
            else:
                # normal character (including ']' in this mode) => add to buffer
                buffer.append(c)
        else:
            # We are in Quoted mode
            if c == ']':
                # end quoted mode => do not add ']' to buffer
                in_quoted_mode = False
            else:
                # everything else is literal ('.' and '[' included)
                buffer.append(c)

    # End of string:
    if in_quoted_mode:
        # We never encountered the closing ']' => error
        raise ValueError("Unmatched '[' in path (no closing ']').")

    # If there's any leftover in buffer, that's our last segment
    segments.append("".join(buffer))

    return segments


if __name__ == "__main__":
    '''
    "price" -> ["price"]
    "price.usd" -> ["price", "usd"]
    "price.bit[.]coin" -> ["price", "bit.coin"]
    "price.bit[.coin" -> ERROR: Unmatched '[' in path (no closing ']')
    "a[[x]]" -> ["a[x]"] // note: double [[ / ]] NOT special
    "a]b" -> ["a]b"] // "]" not a special character (except as end-marker)
    "a[[b]" -> ["a[b"] // "[" must be quoted
    "a[1]" -> ["a1"] // unnecessary quoting but works
    "a[]" -> ["a"]
    "price.monkey[[0]]" -> ["price", "monkey[0]"]
    "price.monkey[0]" -> ["price", "monkey0"]
    "price.monkey[1]" -> ["price", "monkey1"]
    '''
    examples = [
        "price",
        "price.usd",
        "price.bit[.]coin",
        "price.bit[.coin",  # This should raise an error: no matching ']'
        "a[[x]]",
        "a]b",
        "a[[b]",
        "a[1]",
        "a[]",
        "price.monkey[[0]]",
        "price.monkey[0]",
        "price.monkey[1]",
    ]

    for ex in examples:
        try:
            result = path_to_steps(ex)
            print(f"{ex!r} -> {result}")
        except ValueError as e:
            print(f"{ex!r} -> ERROR: {e}")

