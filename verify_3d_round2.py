#!/usr/bin/env python3
"""verify_3d_round2.py -- supplementary checks for the revised manuscript (round 2).

Adds to verify_3d_recovery.py / verify_3d_group.py, without modifying them:

  Part A  The non-role-balanced template of Corollary 1 recovers all 36 damage cases.
  Part B  The count 40 of Remark 1 (partitions into coordinate transversals, no role condition).
  Part C  The 27 parity transversals and the 21 partitions of Theorem 2 for the
          canonical role pattern rho_0(x,y,z) = (x+y+z) mod 3, printed as the certificate
          of Appendix A, and the value 21 recomputed for every one of the 24 role patterns.
  Part D  The Latin-cube count 24 = 12 x 2 by the discordant-layer argument of Section 2.2.

Standard library only.  Exits non-zero on any mismatch with the paper.
"""
import itertools, sys

CELLS = [(x, y, z) for x in range(3) for y in range(3) for z in range(3)]
IDX = {c: i for i, c in enumerate(CELLS)}
FAIL = []

def check(label, got, want):
    ok = (got == want)
    print(f"  [{'OK ' if ok else 'BAD'}] {label}\n           computed {got}   paper {want}")
    if not ok: FAIL.append(label)

def rods():
    out = []
    for a in range(3):
        for b in range(3):
            out.append([(a, b, z) for z in range(3)])
            out.append([(a, z, b) for z in range(3)])
            out.append([(z, a, b) for z in range(3)])
    return out

def slabs():
    return [[c for c in CELLS if c[k] == v] for k in range(3) for v in range(3)]

def decodable(template, erased):
    """Lemma 1: an erased set decodes iff it meets every parity triple at most once."""
    seen = set()
    for c in erased:
        r = template[c][1]
        if r in seen: return False
        seen.add(r)
    return True

def erase_and_decode(template, erased, payload):
    """Actual XOR recovery of every erased block from its two surviving partners."""
    by_index = {}
    for c, (role, r) in template.items(): by_index.setdefault(r, []).append(c)
    for c in erased:
        partners = [d for d in by_index[template[c][1]] if d != c]
        if any(d in erased for d in partners): return False
        if payload[partners[0]] ^ payload[partners[1]] != payload[c]: return False
    return True

# ---------------------------------------------------------------- Part A
print("=" * 74); print("Part A.  Corollary 1: a recoverable template that is not role balanced"); print("=" * 74)
LAYERS = {0: ["A0 A8 A4", "A3 B2 C7", "A6 B5 C1"],
          1: ["A1 B6 C5", "C4 B0 C8", "A7 B3 C2"],
          2: ["A2 B7 C3", "A5 B1 C6", "B8 B4 C0"]}
T = {}
for z, rows in LAYERS.items():
    for y, row in enumerate(rows):
        for x, tok in enumerate(row.split()):
            T[(x, y, z)] = (tok[0], int(tok[1]))
check("27 distinct blocks", len(set(T.values())), 27)
check("criterion (2): index bijective on every slab",
      all(sorted(T[c][1] for c in S) == list(range(9)) for S in slabs()), True)
check("role balance fails on rod (x,0,0)", [T[(x, 0, 0)][0] for x in range(3)], ['A', 'A', 'A'])
import random
rng = random.Random(2026)
pay = {c: rng.getrandbits(8) for c in CELLS}
for r in range(9):
    a = [c for c in CELLS if T[c] == ('A', r)][0]; b = [c for c in CELLS if T[c] == ('B', r)][0]
    cc = [c for c in CELLS if T[c] == ('C', r)][0]; pay[cc] = pay[a] ^ pay[b]
check("rods decoded by erase-and-XOR", sum(erase_and_decode(T, set(E), pay) for E in rods()), 27)
check("slabs decoded by erase-and-XOR", sum(erase_and_decode(T, set(E), pay) for E in slabs()), 9)

# ---------------------------------------------------------------- Part B
print("=" * 74); print("Part B.  Remark 1: partitions into coordinate transversals"); print("=" * 74)
TRIP = [t for t in itertools.combinations(CELLS, 3)
        if all(len({c[k] for c in t}) == 3 for k in range(3))]
check("coordinate transversals", len(TRIP), 36)
MASK = {t: sum(1 << IDX[c] for c in t) for t in TRIP}

def covers(triples):
    masks = [MASK[t] for t in triples]; out = []
    def rec(used, chosen):
        if used == (1 << 27) - 1: out.append(chosen); return
        low = (~used) & ((1 << 27) - 1); f = (low & -low).bit_length() - 1
        for t, m in zip(triples, masks):
            if m & used or not (m >> f) & 1: continue
            rec(used | m, chosen + [t])
    rec(0, []); return out
check("partitions with no role condition", len(covers(TRIP)), 40)

# ---------------------------------------------------------------- Part C
print("=" * 74); print("Part C.  Theorem 2: 27 transversals and 21 partitions; certificate of Appendix A"); print("=" * 74)
def role_patterns():
    lines = [[IDX[(x, y, z)] for x in range(3)] for y in range(3) for z in range(3)] + \
            [[IDX[(x, y, z)] for y in range(3)] for x in range(3) for z in range(3)] + \
            [[IDX[(x, y, z)] for z in range(3)] for x in range(3) for y in range(3)]
    out = []; a = [-1] * 27
    def ok(i):
        for L in lines:
            if i in L:
                v = [a[j] for j in L if a[j] >= 0]
                if len(v) != len(set(v)): return False
        return True
    def rec(i):
        if i == 27: out.append(tuple(a)); return
        for r in range(3):
            a[i] = r
            if ok(i): rec(i + 1)
            a[i] = -1
    rec(0); return out
PATS = role_patterns()
check("role patterns (Latin cubes of order 3)", len(PATS), 24)
rho0 = tuple((c[0] + c[1] + c[2]) % 3 for c in CELLS)
check("rho_0 is one of the 24", rho0 in PATS, True)
def parity_transversals(pat):
    return [t for t in TRIP if len({pat[IDX[c]] for c in t}) == 3]
PT0 = parity_transversals(rho0)
check("parity transversals of rho_0", len(PT0), 27)
P0 = covers(PT0)
check("partitions of rho_0", len(P0), 21)
counts = {len(covers(parity_transversals(p))) for p in PATS}
check("partition count over all 24 patterns", counts, {21})
check("|V*3D| = 24 x 21 x 9!", 24 * 21 * 362880, 182891520)
print("\n  Certificate (Appendix A): each transversal {(0,s0,t0),(1,s1,t1),(2,s2,t2)} is written s0s1s2.t0t1t2")
def code(t):
    t = sorted(t); return ''.join(str(c[1]) for c in t) + '.' + ''.join(str(c[2]) for c in t)
for n, part in enumerate(P0, 1):
    print(f"  {n:2}  " + "  ".join(sorted(code(t) for t in part)))

# ---------------------------------------------------------------- Part D
print("=" * 74); print("Part D.  Section 2.2: 24 Latin cubes = 12 Latin squares x 2 discordant shifts"); print("=" * 74)
SQ = [rows for rows in itertools.product(itertools.permutations(range(3)), repeat=3)
      if all(len({rows[r][c] for r in range(3)}) == 3 for c in range(3))]
check("Latin squares of order 3", len(SQ), 12)
ok = True
for L0 in SQ:
    disc = {L1 for L1 in SQ if all(L1[r][c] != L0[r][c] for r in range(3) for c in range(3))}
    shifts = {tuple(tuple((L0[r][c] + k) % 3 for c in range(3)) for r in range(3)) for k in (1, 2)}
    ok &= (disc == shifts)
check("discordant squares of L0 are exactly L0+1 and L0+2", ok, True)
check("12 x 2 = 24", 12 * 2, len(PATS))

print("\n" + ("All checks passed." if not FAIL else f"FAILED: {FAIL}"))
sys.exit(1 if FAIL else 0)
