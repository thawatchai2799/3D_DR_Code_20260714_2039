#!/usr/bin/env python3
"""
DR27.py - DR Code 3D Pattern Enumerator and Verifier (3x3x3 cube)
=================================================================

Companion code for:
  W. Sriphum and T. Chomsiri, "Generalizing DR Code to Three Dimensions:
  Combinatorial Structure, Group-Theoretic Analysis, and Storage
  Implications of the 3x3x3 DR Code", 2026.

This program extends the DR Code from 2D (3x3 = 9 cells) to 3D
(3x3x3 = 27 cells) using smart backtracking with constraint
propagation, since enumerating all 27! ~ 1.09e28 permutations
directly is computationally infeasible.

Structure of the 3D DR Code
---------------------------
- 27 logical data blocks divided into 3 classes (A, B, C), 9 blocks each:
    Class A: A0..A8
    Class B: B0..B8
    Class C: C0..C8, computed as Ci = Ai XOR Bi
- Blocks are placed on a 3x3x3 cube.
- Recoverability constraint: every line in the X, Y, or Z axis
  (27 lines in total) must contain blocks from all three distinct
  classes.

Computed results (all verified at runtime by this script)
---------------------------------------------------------
Part 1 - Enumeration (Section 4 of the paper):
  - Class-level patterns (Latin cubes of order 3 with three symbols,
    OEIS A076389): exactly 24
  - Full DR Code 3D templates: 24 x (9!)^3 = 1,146,833,420,156,928,000
    ~ 1.15e18                                              (Theorem 1)
  - Recovery cases: 27 rods (1D lines) + 9 slabs (2D planes) = 36
    (versus 6 cases for the 2D DR Code)

Part 2 - Group-theoretic verification (Section 5 of the paper):
  - The symmetry group G = (C3 x C3 x C3) semidirect-product O_h is
    constructed explicitly as a permutation group on the 27 cells from
    the nine generators (3 rotations, 3 mirrors, 3 cyclic shifts), and
    the following are verified by exhaustive computation:
      * |O_h| = 48, |N| = |C3^3| = 27, |G| = 1,296        (Theorem 3)
      * N is normal in G; O_h is not normal in G;
        N intersect O_h = {identity}  =>  G = N x| O_h     (Theorem 3)
      * all 24 class-level patterns form a single orbit under G,
        with stabilizer of order 54 = 1,296 / 24           (Theorem 4)
      * Burnside fixed-point distribution over the 24 patterns:
        |Fix(g)| = 0 for 1,113 elements, 6 for 152, 12 for 30,
        and 24 for the identity alone; the weighted sum is 1,296,
        giving exactly 1 orbit                       (Section 5.3.2)
      * orbit decomposition of the 24 patterns under the five
        canonical subgroups, reproducing TABLE 2 of the paper

Usage
-----
  python3 DR27.py

Requires only the Python 3 standard library (Python 3.8+).

Authors: Wiwat Sriphum, Thawatchai Chomsiri (2026)
Extends: W. Sriphum, "DR Code: The Two Dimensions Barcode Supporting
         High Rate Data Recovery", IEEE CSE 2013.
"""

import math
import random
import time

# ======================================================================
# Lattice geometry: cells, indexing, and the 27 line constraints
# ======================================================================

def xyz_to_idx(x, y, z):
    """Map a (x, y, z) coordinate to a flat cell index (z-major order)."""
    return z * 9 + y * 3 + x


def idx_to_xyz(i):
    """Inverse of xyz_to_idx."""
    z = i // 9
    y = (i % 9) // 3
    x = i % 3
    return x, y, z


def block_class(b):
    """Class (0 = A, 1 = B, 2 = C) of block index b in 0..26."""
    return b // 9


def block_name(b):
    """Human-readable block name, e.g. block 13 -> 'B4'."""
    cls = ['A', 'B', 'C'][b // 9]
    sub = b % 9
    return f"{cls}{sub}"


def build_lines():
    """Build the 27 line constraints (9 per axis).

    A line is obtained by fixing two coordinates and varying the third
    over {0, 1, 2}.  Returns a list of 27 tuples of 3 cell indices.
    """
    lines = []
    for z in range(3):                                   # X-lines (rows)
        for y in range(3):
            lines.append(tuple(xyz_to_idx(x, y, z) for x in range(3)))
    for z in range(3):                                   # Y-lines (columns)
        for x in range(3):
            lines.append(tuple(xyz_to_idx(x, y, z) for y in range(3)))
    for y in range(3):                                   # Z-lines (depth)
        for x in range(3):
            lines.append(tuple(xyz_to_idx(x, y, z) for z in range(3)))
    return lines


LINES = build_lines()
assert len(LINES) == 27

# For each cell, the indices of the three lines passing through it.
CELL_TO_LINES = [[] for _ in range(27)]
for line_idx, line in enumerate(LINES):
    for cell in line:
        CELL_TO_LINES[cell].append(line_idx)


# ======================================================================
# Part 1 - Class-level enumeration (Algorithm 1 of the paper)
# ======================================================================

def enumerate_class_patterns(verbose=True):
    """Enumerate all class-level patterns (Latin cubes of order 3).

    Backtracking with constraint propagation: per-line counters give an
    O(1) feasibility test per line.  A class may be placed at a cell
    only if no line through that cell already contains that class;
    this single check suffices because the line constraint requires
    exactly one block of each class per line.
    """
    grid = [-1] * 27
    class_remaining = [9, 9, 9]
    line_class_count = [[0, 0, 0] for _ in range(27)]
    patterns = []

    def backtrack(pos):
        if pos == 27:
            patterns.append(tuple(grid))
            return
        for cls in range(3):
            if class_remaining[cls] == 0:
                continue
            ok = True
            for li in CELL_TO_LINES[pos]:
                if line_class_count[li][cls] >= 1:
                    ok = False
                    break
            if not ok:
                continue
            grid[pos] = cls
            class_remaining[cls] -= 1
            for li in CELL_TO_LINES[pos]:
                line_class_count[li][cls] += 1
            backtrack(pos + 1)
            grid[pos] = -1
            class_remaining[cls] += 1
            for li in CELL_TO_LINES[pos]:
                line_class_count[li][cls] -= 1

    if verbose:
        print("Enumerating Latin cubes of order 3 (class patterns)...")
    start = time.time()
    backtrack(0)
    elapsed = time.time() - start
    if verbose:
        print(f"  Found {len(patterns)} class patterns in {elapsed:.4f}s")
    return patterns


# ======================================================================
# Full templates: expansion, verification, display
# ======================================================================

def make_full_template_from_class(class_pattern, seed=None):
    """Expand a class pattern into a full template by assigning a random
    within-class ordering of block indices to each class (one of the
    (9!)^3 possible expansions)."""
    if seed is not None:
        random.seed(seed)
    positions_by_class = [[], [], []]
    for i, c in enumerate(class_pattern):
        positions_by_class[c].append(i)

    template = [-1] * 27
    for cls in range(3):
        block_offset = cls * 9
        block_indices = list(range(block_offset, block_offset + 9))
        random.shuffle(block_indices)
        for pos_idx, pos in enumerate(positions_by_class[cls]):
            template[pos] = block_indices[pos_idx]
    return tuple(template)


def verify_template(template):
    """Check that a full template is a valid 3D DR Code: every line
    contains all three distinct classes."""
    for line in LINES:
        classes = set(block_class(template[c]) for c in line)
        if len(classes) != 3:
            return False
    return True


def template_to_3d_str(template):
    """Render a full template as a 3x3x3 cube, one Z-layer at a time."""
    out = []
    for z in range(3):
        out.append(f"  Layer z={z}:")
        for y in range(3):
            row = "    "
            for x in range(3):
                idx = xyz_to_idx(x, y, z)
                row += f"{block_name(template[idx]):>3} "
            out.append(row)
        out.append("")
    return "\n".join(out)


def class_pattern_to_3d_str(pattern):
    """Render a class pattern as a 3x3x3 cube, one Z-layer at a time."""
    out = []
    for z in range(3):
        out.append(f"  Layer z={z}:")
        for y in range(3):
            row = "    "
            for x in range(3):
                idx = xyz_to_idx(x, y, z)
                row += f"{['A', 'B', 'C'][pattern[idx]]} "
            out.append(row)
        out.append("")
    return "\n".join(out)


def get_recovery_cases():
    """Return the recoverable damage cases: 27 rods (the lines
    themselves) and 9 slabs (axis-aligned 3x3x1 planes)."""
    rods = LINES
    slabs = []
    for x_val in range(3):
        slabs.append(tuple(xyz_to_idx(x_val, y, z)
                           for y in range(3) for z in range(3)))
    for y_val in range(3):
        slabs.append(tuple(xyz_to_idx(x, y_val, z)
                           for x in range(3) for z in range(3)))
    for z_val in range(3):
        slabs.append(tuple(xyz_to_idx(x, y, z_val)
                           for x in range(3) for y in range(3)))
    return rods, slabs


# ======================================================================
# Part 2 - The symmetry group G = (C3 x C3 x C3) x| O_h  (Section 5)
# ======================================================================

CELLS = [idx_to_xyz(i) for i in range(27)]
IDENTITY = tuple(range(27))


def perm_from_cellmap(f):
    """Build a permutation of cell indices from a coordinate map f:
    p[i] = index of f(cell_i)."""
    return tuple(xyz_to_idx(*f(x, y, z)) for (x, y, z) in CELLS)


# The nine geometric generators of G (Section 5.1 of the paper):
# rotations by 90 degrees about each axis ...
ROT_X = perm_from_cellmap(lambda x, y, z: (x, 2 - z, y))
ROT_Y = perm_from_cellmap(lambda x, y, z: (z, y, 2 - x))
ROT_Z = perm_from_cellmap(lambda x, y, z: (2 - y, x, z))
# ... mirror reflections across the planes perpendicular to each axis ...
MIR_X = perm_from_cellmap(lambda x, y, z: (2 - x, y, z))
MIR_Y = perm_from_cellmap(lambda x, y, z: (x, 2 - y, z))
MIR_Z = perm_from_cellmap(lambda x, y, z: (x, y, 2 - z))
# ... and cyclic translations along each axis.
SH_X = perm_from_cellmap(lambda x, y, z: ((x + 1) % 3, y, z))
SH_Y = perm_from_cellmap(lambda x, y, z: (x, (y + 1) % 3, z))
SH_Z = perm_from_cellmap(lambda x, y, z: (x, y, (z + 1) % 3))


def compose(p, q):
    """Composition (p o q)[i] = p[q[i]] - apply q first, then p."""
    return tuple(p[q[i]] for i in range(27))


def inverse(p):
    """Inverse permutation of p."""
    inv = [0] * 27
    for i, v in enumerate(p):
        inv[v] = i
    return tuple(inv)


def closure(generators):
    """Breadth-first closure of a generator set into the full group."""
    group = {IDENTITY}
    frontier = [IDENTITY]
    while frontier:
        nxt = []
        for g in frontier:
            for s in generators:
                h = compose(s, g)
                if h not in group:
                    group.add(h)
                    nxt.append(h)
        frontier = nxt
    return group


def act(g, pattern):
    """Action of a cell permutation g on a class pattern:
    (g . p)(cell) = p(g^{-1}(cell)).  With g as a forward cell map,
    this is new[g[i]] = old[i]."""
    out = [0] * 27
    for i in range(27):
        out[g[i]] = pattern[i]
    return tuple(out)


def orbits(group, patterns):
    """Partition the given patterns into orbits under the group action.
    Asserts closure: the action must map patterns to patterns
    (Theorem 2: recoverability is preserved)."""
    pat_set = set(patterns)
    seen, orbs = set(), []
    for p in patterns:
        if p in seen:
            continue
        orb = {act(g, p) for g in group}
        assert orb <= pat_set, "group action must preserve recoverability"
        orbs.append(orb)
        seen |= orb
    return orbs


def verify_group_theory(patterns):
    """Run all the group-theoretic verifications of Section 5 and
    raise AssertionError if any claim of the paper fails."""

    # --- Theorem 3: group orders and semi-direct product structure ---
    O_h = closure([ROT_X, ROT_Y, ROT_Z, MIR_X, MIR_Y, MIR_Z])
    N = closure([SH_X, SH_Y, SH_Z])
    G = closure([ROT_X, ROT_Y, ROT_Z, MIR_X, MIR_Y, MIR_Z,
                 SH_X, SH_Y, SH_Z])
    print(f"  |O_h| = {len(O_h)} (expected 48)")
    print(f"  |N|   = {len(N)} (expected 27)")
    print(f"  |G|   = {len(G):,} (expected 1,296)")
    assert (len(O_h), len(N), len(G)) == (48, 27, 1296)

    def conj(g, h):
        """Conjugation g h g^{-1}."""
        return compose(compose(g, h), inverse(g))

    n_normal = all(conj(g, h) in N for g in G for h in N)
    oh_normal = all(conj(g, h) in O_h for g in G for h in O_h)
    trivial_int = (N & O_h == {IDENTITY})
    print(f"  N normal in G:        {n_normal} (expected True)")
    print(f"  O_h normal in G:      {oh_normal} (expected False)")
    print(f"  N intersect O_h = id: {trivial_int} (expected True)")
    print("  => G is the internal semi-direct product N x| O_h "
          "(Theorem 3)")
    assert n_normal and (not oh_normal) and trivial_int

    # --- Theorem 4: single orbit of the 24 patterns, stabilizer 54 ---
    orbs_G = orbits(G, patterns)
    stab = len(G) // len(orbs_G[0])
    print(f"  Orbits of the 24 patterns under G: {len(orbs_G)} "
          f"(expected 1)")
    print(f"  Orbit size {len(orbs_G[0])}, stabilizer order {stab} "
          f"(expected 54)  (Theorem 4)")
    assert len(orbs_G) == 1 and stab == 54

    # --- Burnside verification (Section 5.3.2) ---
    pat_set = set(patterns)
    dist = {}
    for g in G:
        k = sum(1 for p in pat_set if act(g, p) == p)
        dist[k] = dist.get(k, 0) + 1
    total_fix = sum(k * v for k, v in dist.items())
    print(f"  Fixed-point distribution: {dict(sorted(dist.items()))}")
    print(f"    (expected {{0: 1113, 6: 152, 12: 30, 24: 1}})")
    print(f"  Sum |Fix(g)| = {total_fix} = |G| "
          f"=> Burnside gives {total_fix // len(G)} orbit")
    assert dist == {0: 1113, 6: 152, 12: 30, 24: 1}
    assert total_fix == len(G)

    # --- TABLE 2: orbit decomposition under canonical subgroups ---
    subgroups = [
        ("<Mx,My,Mz> (mirrors only)", closure([MIR_X, MIR_Y, MIR_Z])),
        ("<Rx,Ry,Rz> (rotations only)", closure([ROT_X, ROT_Y, ROT_Z])),
        ("O_h (full octahedral)", O_h),
        ("<Cx,Cy,Cz> (cyclic only)", N),
        ("single C3 (e.g. <Cx>)", closure([SH_X])),
        ("G = (C3xC3xC3) x| O_h (full)", G),
    ]
    expected = [(8, 3, {8: 3}), (24, 3, {8: 3}), (48, 3, {8: 3}),
                (27, 8, {3: 8}), (3, 8, {3: 8}), (1296, 1, {24: 1})]
    print("  Orbit decomposition under subgroups (TABLE 2):")
    print(f"    {'Subgroup':32s} {'Order':>6s} {'Orbits':>7s}  Orbit sizes")
    for (name, H), (eo, en, es) in zip(subgroups, expected):
        os_ = orbits(H, patterns)
        sizes = {}
        for o in os_:
            sizes[len(o)] = sizes.get(len(o), 0) + 1
        print(f"    {name:32s} {len(H):>6,d} {len(os_):>7d}  "
              f"{dict(sorted(sizes.items()))}")
        assert (len(H), len(os_), sizes) == (eo, en, es)


# ======================================================================
# Main
# ======================================================================

def main():
    print("=" * 70)
    print("DR Code 3D (3x3x3) Pattern Enumerator and Verifier")
    print("=" * 70)

    print("\n[Step 1] Class-level pattern enumeration (Algorithm 1)")
    class_patterns = enumerate_class_patterns(verbose=True)
    n_class = len(class_patterns)
    assert n_class == 24, "expected 24 Latin cubes (OEIS A076389)"

    print("\n[Step 2] Total template count (Theorem 1)")
    fact9 = math.factorial(9)
    total = n_class * (fact9 ** 3)
    print(f"  Each class pattern expands to (9!)^3 = {fact9**3:,} "
          f"full templates")
    print(f"  Total DR Code 3D templates: {n_class} x (9!)^3 = {total:,}")
    print(f"                            ~ {total:.3e}")
    assert total == 1_146_833_420_156_928_000

    print("\n[Step 3] Sample class pattern (#1):")
    print(class_pattern_to_3d_str(class_patterns[0]))

    print("[Step 4] Sample full DR Code 3D template (one of ~1.15e18):")
    sample = make_full_template_from_class(class_patterns[0], seed=42)
    print(template_to_3d_str(sample))
    print(f"  Verified valid: {verify_template(sample)}")
    assert verify_template(sample)

    print("\n[Step 5] Recovery capability:")
    rods, slabs = get_recovery_cases()
    print(f"  Rod (1D line) recovery cases:   {len(rods)}")
    print(f"  Slab (2D plane) recovery cases: {len(slabs)}")
    print(f"  Total recovery cases:           {len(rods) + len(slabs)} "
          f"(versus 6 in 2D)")
    assert len(rods) + len(slabs) == 36

    print("\n[Step 6] Group-theoretic verification (Section 5):")
    verify_group_theory(class_patterns)

    print("\n[Step 7] Writing class patterns to file...")
    with open("DR27_class_patterns.txt", "w", encoding="utf-8") as f:
        f.write("DR Code 3D Class-Level Patterns "
                "(Latin cubes of order 3)\n")
        f.write("=" * 60 + "\n")
        f.write(f"Total: {n_class} class patterns\n")
        f.write(f"Each expands to (9!)^3 = {fact9**3:,} full DR "
                f"templates\n")
        f.write(f"Grand total: {total:,}\n\n")
        for i, pat in enumerate(class_patterns):
            f.write(f"Pattern #{i + 1}:\n")
            f.write(class_pattern_to_3d_str(pat))
            f.write("\n")
    print("  Saved to DR27_class_patterns.txt")

    print("\n" + "=" * 70)
    print("SUMMARY - all values verified against the paper")
    print("=" * 70)
    print(f"  Class-level patterns (Latin cubes, A076389):      "
          f"{n_class:>20}")
    print(f"  Full DR Code 3D templates 24 x (9!)^3:            "
          f"{total:>20,}")
    print(f"  Recovery cases (27 rods + 9 slabs):               "
          f"{36:>20}")
    print(f"  Symmetry group order |G| (computed, not assumed): "
          f"{1296:>20,}")
    print(f"  Orbits of class patterns under G:                 "
          f"{1:>20}")
    print(f"  Full-template orbits |V_3D| / |G|:                "
          f"{total // 1296:>20,}")
    print("=" * 70)
    print("ALL CHECKS PASSED")


if __name__ == '__main__':
    main()
