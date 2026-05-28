# monke

## PURPOSE
COMPRESS AI responses to save tokens. Drop filler, articles, pleasantries, hedging. Short synonyms. Dense, precise output.

## USAGE
```
python monke.py --text "Sure! I'd be happy to help you with that issue."
python monke.py --file response.txt
python monke.py --stdin   # pipe text in
```

## RULES APPLIED
1. DROP articles: a, an, the
2. DROP filler: just, really, basically, actually, simply
3. DROP pleasantries: sure, certainly, of course, happy to, glad to, great question
4. DROP hedging: might, perhaps, possibly, it seems, it appears, I think, I believe, you may want to, you might want to
5. SHORT synonyms: big (not extensive), fix (not implement a solution for), use (not utilize), show (not demonstrate), check (not verify/validate)
6. FRAGMENTS OK — no need for full sentences
7. TECHNICAL TERMS exact — never simplify code, error messages, identifiers
8. CODE BLOCKS unchanged — never touch content inside ``` blocks
9. PATTERN: [thing] [action] [reason]. [next step].
10. ERRORS quoted exact

## OUTPUT
Compressed text printed to stdout. Stats: original token count, compressed token count, % saved.

## EXAMPLE
Input:  "Sure! I'd be happy to help you with that. The issue you're experiencing is likely caused by a problem in the authentication middleware."
Output: "Bug in auth middleware."
