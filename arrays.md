# Array

Static arrays are of constant length like in C, dynamic arrays expand/contract based on operation like in Python.

## Sliding window technique

Use it when the problem involves:

* Subarrays / substrings
* Contiguous ranges
* Sums, averages, or counts over a window
* Conditions like “maximum/minimum subarray with … property”

Fixed/variable size

Problem: Find the smallest subarray with sum ≥ target.

Idea:
* Expand the window by moving the right pointer until the sum ≥ target
* Then shrink it from the left to make it as small as possible