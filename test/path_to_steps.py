def path_to_steps(path: str) -> list[str]:
    """
    Parses the path into steps according to the rules:
      1) '[' is a start marker if:
         1.1) it appears at start-of-string or right after '.'
         1.2) it is NOT immediately followed by another '['
         1.3) there is a valid end marker ']' (which must be followed by '.' or end-of-string)
      2) ']' is a valid end marker only if it matches a recognized '['
         and is followed by '.' or end-of-string.
      3) Otherwise, '.' splits steps.
         If multiple '[' occur consecutively without forming a start marker,
         we reduce them by 1 bracket (e.g. '[[' -> '[', '[[[' -> '[[').
    """

    steps = []
    buffer = []  # Collect characters for the current step
    n = len(path)
    i = 0

    def flush_buffer():
        """Flush whatever is in the buffer to steps as a single step (if not empty)."""
        if buffer:
            steps.append("".join(buffer))
            buffer.clear()

    while i < n:
        c = path[i]

        if c == '.':
            # '.' always ends the current step
            flush_buffer()
            i += 1
            continue

        if c == '[':
            # Potential start marker?
            # Check rule (1.1): either i==0 or path[i-1]=='.'
            # Check rule (1.2): next char != '[' (if it exists)
            can_be_start = False
            if i == 0 or (i > 0 and path[i - 1] == '.'):
                if i + 1 < n and path[i+1] != '[':
                    can_be_start = True
                elif i + 1 == n:
                    # Edge case: '[' is the very last char => can't be a start marker anyway
                    can_be_start = False

            if can_be_start:
                # Attempt to find a valid end marker ']' that is followed by '.' or end-of-string
                j = i + 1
                found_end = -1
                while j < n:
                    if path[j] == ']':
                        # Check if ']' is followed by '.' or end-of-string
                        if j == n - 1 or (j + 1 < n and path[j+1] == '.'):
                            found_end = j
                            break
                    j += 1

                if found_end != -1:
                    # We found a valid bracketed step [ ... ]
                    # flush anything currently in buffer as one step
                    flush_buffer()
                    # The inside content is path[i+1 : found_end]
                    inside = path[i+1:found_end]
                    steps.append(inside)
                    # Move i past the ']'
                    i = found_end + 1
                    # If that ']' was followed by a dot, skip it
                    if i < n and path[i] == '.':
                        i += 1
                    continue
                # else => we did not find a valid end bracket
                # so we treat '[' as literal

            # If we get here, the '[' is not a valid start marker => literal
            # We might have multiple '[' in a row => rule 3.2
            run_start = i
            while i < n and path[i] == '[':
                i += 1
            run_len = i - run_start
            # For run_len brackets, we store (run_len - 1) if run_len > 1, else 1
            store_count = run_len - 1 if run_len > 1 else 1
            buffer.append('[' * store_count)

            continue  # continue the main loop

        else:
            # Normal character, just accumulate
            buffer.append(c)
            i += 1

    # End of string => flush remaining buffer
    flush_buffer()
    return steps


if __name__ == "__main__":
    """
    Again the rules:
    1. start marker [: 
        1.1 must right after . or is start-of-string
        1.2 not be followed by any [
        1.3 an end marker ] to end it
    2. end marker ]:
        2.1 followed by .  or is end-of-string
        2.2 have start market [ to match it
    3. other rules:
        3.1 use . to split the path by default
        3.2 if there’s more than one “[” coming in, result is “one less” -- “[[” -> “[”, “[[[” -> “[[“.

    Examples：
    "price" -> ["price"]
    "price.usd" -> ["price", "usd"]
    
    // has start and end marker. thus treat the between as the whole step
    "[price.usd]" -> ["price.usd"]
    
    // has start and end marker. thus treat the between as the whole step
    "price.[bit.coin]" -> ["price", "bit.coin"]
    
    // [ cannot meet the third requirement so it’s not the start marker, so [ should be included in the steps
    "price.[bit.coin" -> ["price", "[bit", "coin"]
    
    // [ cannot meet the start marker requirement but can follow other rules 1, so it equals "price.[bit.coin" , which is the case above
    "price.[[bit.coin" -> ["price", "[bit", "coin"]
    
    // no start marker, according to the rules. So no end marker. It equals to "price.[bit].coin" and then split by . 
    "price.[[bit].coin" -> ["price", "[bit]", "coin"]
    
    // no end marker so no start marker. Split it by .
    "path.[abc.def]gh" -> ["path", "[abc", "def]gh" ]
    
    // no start marker so no end marker. It equals to "[price.usd]]", then split by .
    "[[price.usd]]" -> ["[price", "usd]]"]
    
    // no start marker so no end marker. It equals to "price.[bit.coin]", then split by .
    "price.[[bit.coin]" -> ["price", "[bit", "coin]"]
    """

    examples = [
        "price",
        "price.usd",
        "[price.usd]",
        "price.[bit.coin]",
        "price.[bit.coin",
        "price.[[bit.coin",
        "price.[[bit].coin",
        "path.[abc.def]gh",
        "[[price.usd]]",
        "price.[[bit.coin]"
    ]
    for ex in examples:
        result = path_to_steps(ex)
        print(f"{ex!r} -> {result}")
