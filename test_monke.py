#!/usr/bin/env python3
"""Tests for monke compressor."""

import sys
sys.path.insert(0, ".")
from monke import compress

TESTS = [
    # (label, input, expected_substrings_in_output, forbidden_in_output)
    (
        "pleasantry drop",
        "Sure! I'd be happy to help you with that issue.",
        ["issue"],
        ["Sure", "happy to", "I'd"],
    ),
    (
        "hedging drop",
        "It seems like the problem might be caused by a misconfiguration.",
        ["problem", "caused", "misconfiguration"],
        ["It seems", "might be"],
    ),
    (
        "filler drop",
        "You just basically need to actually simply restart the server.",
        ["restart", "server"],
        ["just", "basically", "actually", "simply"],
    ),
    (
        "synonym replacement",
        "You should utilize the following functionality to demonstrate the feature.",
        ["use", "show", "feature"],
        ["utilize", "demonstrate", "functionality"],
    ),
    (
        "verbose phrase",
        "In order to fix the bug, make sure to verify the token.",
        ["fix", "bug", "check", "token"],
        ["In order to", "make sure to", "verify"],
    ),
    (
        "code block preserved",
        "You should just use:\n```python\nthe_token = a + an\n```\nto fix it.",
        ["```python", "the_token = a + an", "```"],
        [],
    ),
    (
        "inline code preserved",
        "Just call `the_function()` to actually get the result.",
        ["`the_function()`"],
        ["just", "actually"],
    ),
    (
        "error message exact",
        'The error "TypeError: cannot read property of undefined" appears.',
        ['"TypeError: cannot read property of undefined"'],
        [],
    ),
    (
        "pattern output",
        "Sure! I'd be happy to help. The issue you're experiencing is likely caused by a problem in the authentication middleware.",
        ["auth", "middleware"],
        ["Sure", "happy to", "I'd be happy"],
    ),
]

passed = 0
failed = 0

for label, inp, must_have, must_not in TESTS:
    result = compress(inp)
    ok = True
    issues = []

    for term in must_have:
        if term not in result:
            ok = False
            issues.append(f"MISSING: '{term}'")

    for term in must_not:
        if term.lower() in result.lower():
            ok = False
            issues.append(f"FOUND (should be gone): '{term}'")

    status = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    else:
        failed += 1

    print(f"[{status}] {label}")
    print(f"  IN:  {inp[:80]}")
    print(f"  OUT: {result[:80]}")
    if issues:
        for i in issues:
            print(f"  !! {i}")
    print()

print(f"Results: {passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
