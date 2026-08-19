#!/usr/bin/env python3
"""
verify_3d_group.py
==================

Reproduces every role-level and group-theoretic claim in

    T. Chomsiri and W. Sriphum,
    "Generalizing DR Code to Three Dimensions: Combinatorial Structure,
     Group-Theoretic Analysis, and Storage Implications of the 3x3x3 DR Code"
    (Mathematics, manuscript mathematics-4471756, major revision)

Everything is computed from first principles: the 27 cells of the cubic
lattice, the 27 line constraints, and the nine generators of the symmetry
group are the only inputs.  No result from the paper is assumed; each
computed value is compared against the figure quoted in the paper and the
comparison is reported as OK or MISMATCH.  The script exits non-zero on any
mismatch.

Requirements: Python 3.9 or later, standard library only.
Runtime:      about two seconds.

Contents
--------
  Part 1   Lattice, line constraints, slabs, and the 24 role patterns
  Part 2   The nine generators, their coordinate formulas and orders
  Part 3   The group G by breadth-first closure:  |G| = 1,296
  Part 4   Internal semi-direct product  G = (C3 x C3 x C3) : O_h
  Part 5   Orbits of the subgroups of Table 2
  Part 6   The single role-level orbit and its stabiliser of order 54
  Part 7   Fixed-point distribution and Burnside's lemma
  Part 8   Arithmetic quoted in Sections 2 and 6

The full-template enumeration and the erasure-and-decode tests are in the
companion script verify_3d_recovery.py.
"""

import itertools
import sys
from collections import Counter
from math import factorial, ceil, log2

FAILURES = []


def check(label, computed, quoted, fmt=str):
    ok = computed == quoted
    if not ok:
        FAILURES.append(label)
    print(f"  [{'OK ' if ok else 'MISMATCH'}] {label}")
    print(f"           computed {fmt(computed)}   paper {fmt(quoted)}")
    return ok


def note(text):
    print(f"           {text}")


def heading(text):
    print()
    print("=" * 74)
    print(text)
    print("=" * 74)


comma = lambda v: f"{v:,}"

# ---------------------------------------------------------------------------
# Part 1.  Lattice, lines, slabs, role patterns
# ---------------------------------------------------------------------------

CELLS = list(itertools.product(range(3), repeat=3))       # (x, y, z)
INDEX = {c: i for i, c in enumerate(CELLS)}

LINES = []
for a in range(3):
    for b in range(3):
        LINES.append([(i, a, b) for i in range(3)])       # parallel to X
        LINES.append([(a, i, b) for i in range(3)])       # parallel to Y
        LINES.append([(a, b, i) for i in range(3)])       # parallel to Z

SLABS = []
for axis in range(3):
    for v in range(3):
        SLABS.append([c for c in CELLS if c[axis] == v])

LINES_THROUGH = {c: [L for L in LINES if c in L] for c in CELLS}


def enumerate_role_patterns():
    """Algorithm 1 of the paper: recursive placement of roles A, B, C so that
    every axis-parallel line carries each role exactly once."""
    patterns = []
    grid = [None] * 27

    def extend(k):
        if k == 27:
            patterns.append(tuple(grid))
            return
        cell = CELLS[k]
        for role in range(3):
            if any(grid[INDEX[x]] == role
                   for L in LINES_THROUGH[cell] for x in L):
                continue
            grid[k] = role
            extend(k + 1)
            grid[k] = None

    extend(0)
    return patterns


heading("Part 1.  Lattice, line constraints, slabs and role patterns")

check("number of cells", len(CELLS), 27)
check("number of axis-parallel lines (rods)", len(LINES), 27)
check("number of axis-parallel slabs", len(SLABS), 9)
check("every rod lies inside exactly two slabs",
      all(sum(1 for S in SLABS if set(L) <= set(S)) == 2 for L in LINES), True)

ROLE_PATTERNS = enumerate_role_patterns()
check("number of role patterns (Latin cubes of order 3)", len(ROLE_PATTERNS), 24)
note("the count is established here by exhaustive search; the paper no longer")
note("attributes it to an OEIS entry")

check("every role pattern satisfies all 27 line constraints",
      all(sorted(w[INDEX[x]] for x in L) == [0, 1, 2]
          for w in ROLE_PATTERNS for L in LINES), True)
check("each role occupies exactly 9 cells in every pattern",
      all(Counter(w) == {0: 9, 1: 9, 2: 9} for w in ROLE_PATTERNS), True)

# ---------------------------------------------------------------------------
# Part 2.  Generators
# ---------------------------------------------------------------------------

IDENTITY = tuple(range(27))


def make_permutation(shift, axis_perm, signs):
    """Cell permutation: translate by `shift`, then apply the signed axis
    permutation.  Gather convention: p[new] = old."""
    p = [0] * 27
    for c in CELLS:
        t = tuple((c[i] + shift[i]) % 3 for i in range(3))
        y = [0] * 3
        for i in range(3):
            y[axis_perm[i]] = t[i] if signs[i] == 1 else 2 - t[i]
        p[INDEX[tuple(y)]] = INDEX[c]
    return tuple(p)


def compose(a, b):
    return tuple(a[b[i]] for i in range(27))


def inverse(p):
    q = [0] * 27
    for i, v in enumerate(p):
        q[v] = i
    return tuple(q)


def order_of(p):
    q, n = p, 1
    while q != IDENTITY:
        q = compose(p, q)
        n += 1
    return n


def apply(p, w):
    return tuple(w[p[i]] for i in range(27))


def image_of_cell(p, c):
    """Where permutation p sends cell c (push-forward)."""
    q = inverse(p)
    return CELLS[q[INDEX[c]]]


NO_SHIFT = (0, 0, 0)
ID_PERM = (0, 1, 2)

sigma_Rx = make_permutation(NO_SHIFT, (0, 2, 1), (1, 1, -1))
sigma_Ry = make_permutation(NO_SHIFT, (2, 1, 0), (-1, 1, 1))
sigma_Rz = make_permutation(NO_SHIFT, (1, 0, 2), (1, -1, 1))
sigma_Mx = make_permutation(NO_SHIFT, ID_PERM, (-1, 1, 1))
sigma_My = make_permutation(NO_SHIFT, ID_PERM, (1, -1, 1))
sigma_Mz = make_permutation(NO_SHIFT, ID_PERM, (1, 1, -1))
sigma_Cx = make_permutation((1, 0, 0), ID_PERM, (1, 1, 1))
sigma_Cy = make_permutation((0, 1, 0), ID_PERM, (1, 1, 1))
sigma_Cz = make_permutation((0, 0, 1), ID_PERM, (1, 1, 1))

ROTATIONS = [sigma_Rx, sigma_Ry, sigma_Rz]
MIRRORS = [sigma_Mx, sigma_My, sigma_Mz]
SHIFTS = [sigma_Cx, sigma_Cy, sigma_Cz]
GENERATORS = ROTATIONS + MIRRORS + SHIFTS

heading("Part 2.  The nine generators (Section 5.1)")

# coordinate formulas as printed in the paper
FORMULAS = {
    "sigma_Rx": (sigma_Rx, lambda x, y, z: (x, 2 - z, y), 4),
    "sigma_Ry": (sigma_Ry, lambda x, y, z: (z, y, 2 - x), 4),
    "sigma_Rz": (sigma_Rz, lambda x, y, z: (2 - y, x, z), 4),
    "sigma_Mx": (sigma_Mx, lambda x, y, z: (2 - x, y, z), 2),
    "sigma_My": (sigma_My, lambda x, y, z: (x, 2 - y, z), 2),
    "sigma_Mz": (sigma_Mz, lambda x, y, z: (x, y, 2 - z), 2),
    "sigma_Cx": (sigma_Cx, lambda x, y, z: ((x + 1) % 3, y, z), 3),
    "sigma_Cy": (sigma_Cy, lambda x, y, z: (x, (y + 1) % 3, z), 3),
    "sigma_Cz": (sigma_Cz, lambda x, y, z: (x, y, (z + 1) % 3), 3),
}
for name, (perm, formula, quoted_order) in FORMULAS.items():
    check(f"{name}: coordinate formula in the paper matches the permutation",
          all(image_of_cell(perm, c) == formula(*c) for c in CELLS), True)
    check(f"{name}: order", order_of(perm), quoted_order)

ROLE_SET = set(ROLE_PATTERNS)
check("Proposition 1: every generator maps role patterns to role patterns",
      all(apply(g, w) in ROLE_SET for g in GENERATORS for w in ROLE_PATTERNS), True)

SLAB_SET = {frozenset(S) for S in SLABS}
LINE_SET = {frozenset(L) for L in LINES}
check("Proposition 1: every generator maps slabs to slabs",
      all(frozenset(image_of_cell(g, c) for c in S) in SLAB_SET
          for g in GENERATORS for S in SLABS), True)
check("Proposition 1: every generator maps lines to lines",
      all(frozenset(image_of_cell(g, c) for c in L) in LINE_SET
          for g in GENERATORS for L in LINES), True)

# ---------------------------------------------------------------------------
# Part 3.  The group G
# ---------------------------------------------------------------------------


def closure(gens):
    seen = {IDENTITY}
    frontier = [IDENTITY]
    while frontier:
        nxt = []
        for a in frontier:
            for g in gens:
                b = compose(a, g)
                if b not in seen:
                    seen.add(b)
                    nxt.append(b)
        frontier = nxt
    return seen


heading("Part 3.  The group G by breadth-first closure (Theorem 3)")

O_H = closure(ROTATIONS + MIRRORS)
N = closure(SHIFTS)
G = closure(GENERATORS)
ROT = closure(ROTATIONS)

check("|O_h|, the full octahedral group", len(O_H), 48)
check("|N| = |C3 x C3 x C3|", len(N), 27)
check("|G|", len(G), 1296, comma)
check("|N| * |O_h| = |G|", len(N) * len(O_H), len(G), comma)
check("rotation subgroup of O_h has order", len(ROT), 24)
rot_orders = Counter(order_of(p) for p in ROT)
check("rotations of order 4 (face quarter-turns)", rot_orders[4], 6)
check("rotations of order 3 (vertex rotations)", rot_orders[3], 8)
check("rotations of order 2 (face half-turns + edge rotations)", rot_orders[2], 3 + 6)

# ---------------------------------------------------------------------------
# Part 4.  Semi-direct product
# ---------------------------------------------------------------------------

heading("Part 4.  Internal semi-direct product structure (Theorem 3)")

check("(i)   N is normal in G",
      all(compose(compose(g, n), inverse(g)) in N for g in G for n in N), True)
oh_normal = all(compose(compose(g, h), inverse(g)) in O_H for g in G for h in O_H)
check("(ii)  O_h is not normal in G",
      "not normal" if not oh_normal else "normal", "not normal")
check("(iii) |N intersect O_h|", len(N & O_H), 1)
products = {compose(n, d) for n in N for d in O_H}
check("(iv)  the products n.d are pairwise distinct",
      len(products), len(N) * len(O_H), comma)
check("(v)   the products exhaust G", products == G, True)
check("conjugation identity  sigma_Rz sigma_Cx sigma_Rz^-1 = sigma_Cy^2",
      compose(compose(sigma_Rz, sigma_Cx), inverse(sigma_Rz))
      == compose(sigma_Cy, sigma_Cy), True)
nlist = sorted(N)
nidx = {p: i for i, p in enumerate(nlist)}
images = {tuple(nidx[compose(compose(d, n), inverse(d))]
                for n in (sigma_Cx, sigma_Cy, sigma_Cz)) for d in O_H}
check("the structure map O_h -> Aut(N) is injective", len(images), len(O_H))

# ---------------------------------------------------------------------------
# Part 5.  Table 2
# ---------------------------------------------------------------------------


def orbit_data(subgroup):
    seen, count, sizes = set(), 0, Counter()
    for w in ROLE_PATTERNS:
        if w in seen:
            continue
        orb = {apply(p, w) for p in subgroup}
        seen |= orb
        count += 1
        sizes[len(orb)] += 1
    return count, dict(sorted(sizes.items()))


heading("Part 5.  Orbits of the subgroups of Table 2")

TABLE_2 = [
    ("<sigma_Mx, sigma_My, sigma_Mz>  (mirrors only)",  closure(MIRRORS),   8,   3, {8: 3}),
    ("<sigma_Rx, sigma_Ry, sigma_Rz>  (rotations only)", ROT,             24,   3, {8: 3}),
    ("O_h                             (full octahedral)", O_H,             48,   3, {8: 3}),
    ("<sigma_Cx, sigma_Cy, sigma_Cz>  (cyclic only)",   N,                27,   8, {3: 8}),
    ("<sigma_Cx>                      (a single C3)",   closure([sigma_Cx]), 3, 8, {3: 8}),
    ("G = (C3 x C3 x C3) : O_h        (full group)",    G,              1296,   1, {24: 1}),
]
for label, H, q_order, q_orbits, q_sizes in TABLE_2:
    print(f"\n  -- {label}")
    check("     subgroup order", len(H), q_order, comma)
    n_orb, sizes = orbit_data(H)
    check("     number of orbits on the 24 role patterns", n_orb, q_orbits)
    check("     orbit sizes", sizes, q_sizes)
    check("     sizes sum to 24", sum(k * v for k, v in sizes.items()), 24)

# ---------------------------------------------------------------------------
# Part 6.  Theorem 4
# ---------------------------------------------------------------------------

heading("Part 6.  The single role-level orbit and its stabiliser (Theorem 4)")

w0 = ROLE_PATTERNS[0]
orbit0 = {apply(p, w0) for p in G}
check("orbit of one role pattern under G has size", len(orbit0), 24)
check("that orbit is the whole set of role patterns", orbit0 == ROLE_SET, True)
stab0 = [p for p in G if apply(p, w0) == w0]
check("stabiliser order", len(stab0), 54)
check("orbit-stabiliser: 24 * 54 = |G|", len(orbit0) * len(stab0), len(G), comma)
check("every one of the 24 patterns has a stabiliser of order 54",
      all(len([p for p in G if apply(p, w) == w]) == 54 for w in ROLE_PATTERNS), True)

# ---------------------------------------------------------------------------
# Part 7.  Burnside
# ---------------------------------------------------------------------------

heading("Part 7.  Fixed-point distribution and Burnside's lemma (Section 5.3.2)")

fixed_counts = Counter()
for p in G:
    fixed_counts[sum(1 for w in ROLE_PATTERNS if apply(p, w) == w)] += 1
distribution = dict(sorted(fixed_counts.items()))

print("  |Fix(g)|   number of group elements")
print("  --------   ------------------------")
for v in sorted(distribution):
    print(f"  {v:8}   {distribution[v]:,}")
print()
check("fixed-point distribution", distribution, {0: 1113, 6: 152, 12: 30, 24: 1})
check("the counts account for all group elements",
      sum(distribution.values()), 1296, comma)
weighted = sum(v * c for v, c in distribution.items())
note("weighted sum = " + " + ".join(f"{v}*{c:,}" for v, c in distribution.items())
     + f" = {weighted:,}")
check("sum over g of |Fix(g)|", weighted, 1296, comma)
check("Burnside: number of orbits = sum / |G|", weighted // len(G), 1)
check("only the identity fixes all 24 patterns", fixed_counts[24], 1)

# ---------------------------------------------------------------------------
# Part 8.  Arithmetic quoted in Sections 2 and 6
# ---------------------------------------------------------------------------

heading("Part 8.  Arithmetic quoted in the text")

check("2D: 12 Latin squares x (3!)^3 = 2,592", 12 * factorial(3) ** 3, 2592, comma)
check("2D: 2,592 / 72 = 36 orbits", 2592 // 72, 36)
check("|G| / |2D group| = 1,296 / 72", 1296 // 72, 18)
check("|O_h| / |D4| = 48 / 8", 48 // 8, 6)
check("lookup table entries 24 x 27", 24 * 27, 648)
check("bits per role label, ceil(log2 3)", ceil(log2(3)), 2)
check("packed lookup table at 2 bits per cell, bytes", 24 * 27 * 2 // 8, 162)
check("27! has about 1.09e28 permutations",
      round(factorial(27) / 1e28, 2), 1.09)
years = factorial(27) / 1e12 / (365.25 * 24 * 3600)
check("27! at 1e12 per second is about 3e8 years", round(years / 1e8), 3)

# ---------------------------------------------------------------------------

heading("Summary")
if FAILURES:
    print(f"  {len(FAILURES)} check(s) did NOT match the paper:")
    for f in FAILURES:
        print(f"    - {f}")
    sys.exit(1)
print("  All checks passed.  Every role-level and group-theoretic claim in the")
print("  paper is reproduced from first principles by this script.")
sys.exit(0)
