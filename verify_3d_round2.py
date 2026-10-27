#!/usr/bin/env python3
"""verify_3d_round2.py -- supplementary checks for the 3x3x3 DR Code paper.

Adds to verify_3d_recovery.py / verify_3d_group.py, without modifying them:

  Part A  The non-role-balanced template of Corollary 1 recovers all 36 damage cases.
  Part B  The count 40 of Remark 1 (partitions into coordinate transversals, no role condition).
  Part C  The 27 parity transversals and the 21 partitions of Theorem 2 for the
          canonical role pattern rho_0(x,y,z) = (x+y+z) mod 3, printed as the certificate
          of Appendix A, and the value 21 recomputed for every one of the 24 role patterns.
  Part D  The Latin-cube count 24 = 12 x 2 by the discordant-layer argument of Section 2.2.
  Part F  Lemma 3 / Theorem 2(b): every parity transversal of rho_0 is an affine line (9 per direction),
          the 21 partitions split 3 + 18 by direction, and the count 21 equals the number of rod tilings
          of the 3x3x3 array (1 + 12 + 8).
  Part E  Proposition 2: Stab_G(rho_0) = T_0 : S_3 of order 54, its orbits of sizes 3 and 18 on the
          21 partitions, the three single-direction partitions (rows 1, 11, 21 of Table A1), and
          141,120 = 20,160 + 120,960.
  Part H  Lemma 4 (the 12 Latin squares of order 3: affine form, one orbit under the planar group, three
          under D_4, the 72 Graeco-Latin pairs and the free action), Corollary 4 (two classes of templates under
          G x S_3 x S_9, of sizes 72 x 9! and 432 x 9!) and the damage statistics of Section 6.7 beyond the 36
          designed cases (two rods 162/351, rod + slab 54/243, two slabs never, k random cells).
  Part G  Section 6.5: the wall-clock cost of the canonical form (lexicographic minimum of the 1,296
          images under G, and of the 48 images under O_h) on 200 random templates, with the platform.

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

# ---------------------------------------------------------------- Part E
print("=" * 74); print("Part E.  Proposition 2: stabiliser of rho_0 and the orbits 3 + 18 on the 21 partitions"); print("=" * 74)
def gen_maps():
    Rx = lambda c: (c[0], 2 - c[2], c[1]);  Ry = lambda c: (c[2], c[1], 2 - c[0]);  Rz = lambda c: (2 - c[1], c[0], c[2])
    Mx = lambda c: (2 - c[0], c[1], c[2])
    Cx = lambda c: ((c[0] + 1) % 3, c[1], c[2]); Cy = lambda c: (c[0], (c[1] + 1) % 3, c[2]); Cz = lambda c: (c[0], c[1], (c[2] + 1) % 3)
    return [Rx, Ry, Rz, Mx, Cx, Cy, Cz]
def perm_of(f): return tuple(IDX[f(c)] for c in CELLS)
GENS = [perm_of(f) for f in gen_maps()]
IDENT = tuple(range(27)); G = {IDENT}; frontier = [IDENT]
while frontier:
    nxt = []
    for p in frontier:
        for g in GENS:
            q = tuple(g[p[i]] for i in range(27))
            if q not in G: G.add(q); nxt.append(q)
    frontier = nxt
check("|G| (closure from the generators)", len(G), 1296)
def image_pattern(p, pat):
    out = [None] * 27
    for i in range(27): out[p[i]] = pat[i]
    return tuple(out)
STAB = [p for p in G if image_pattern(p, rho0) == rho0]
check("|Stab_G(rho_0)|", len(STAB), 54)
shifts = [p for p in STAB if all(((CELLS[p[i]][k] - CELLS[i][k]) % 3) == ((CELLS[p[0]][k] - CELLS[0][k]) % 3) for i in range(27) for k in range(3))]
check("shifts in the stabiliser (u+v+w = 0 mod 3)", len(shifts), 9)
check("all 9 stabilising shifts have u+v+w = 0", all(sum(CELLS[p[0]]) % 3 == 0 for p in shifts), True)
fix0 = [p for p in STAB if p[0] == 0]
check("origin-fixing elements of the stabiliser (axis permutations)", len(fix0), 6)
check("they are exactly the six coordinate permutations",
      sorted(tuple(CELLS[p[IDX[e]]] for e in [(1,0,0),(0,1,0),(0,0,1)]) for p in fix0)
      == sorted(itertools.permutations([(1,0,0),(0,1,0),(0,0,1)])), True)
def act(p, part): return frozenset(frozenset(CELLS[p[IDX[c]]] for c in t) for t in part)
PSET = {frozenset(frozenset(t) for t in part) for part in P0}
orbits = []; seen = set()
for part in PSET:
    if part in seen: continue
    orb = {act(p, part) for p in STAB}
    assert orb <= PSET
    seen |= orb; orbits.append(orb)
check("orbit sizes of Stab_G(rho_0) on the 21 partitions", sorted(len(o) for o in orbits), [3, 18])
small = [o for o in orbits if len(o) == 3][0]
def is_line(t):
    t = sorted(t); d = tuple((t[1][k] - t[0][k]) % 3 for k in range(3))
    return all(((t[0][k] + 2 * d[k]) % 3) == t[2][k] for k in range(3)), d
line_dirs = set()
all_lines = True
for part in small:
    for t in part:
        ok_, d = is_line(t); all_lines &= ok_
        if ok_: line_dirs.add(min(d, tuple((-x) % 3 for x in d)))
check("the 3 partitions of the small orbit consist of affine lines", all_lines, True)
check("their directions (up to sign)", sorted(line_dirs), [(1, 1, 2), (1, 2, 1), (1, 2, 2)])
rows = sorted(n for n, part in enumerate(P0, 1) if frozenset(frozenset(t) for t in part) in small)
check("rows of Table A1 in the small orbit", rows, [1, 11, 21])
check("141,120 = 3 x 9!/54 + 18 x 9!/54 = 20,160 + 120,960", (3 * 362880 // 54, 18 * 362880 // 54, 3 * 362880 // 54 + 18 * 362880 // 54), (20160, 120960, 141120))

# ---------------------------------------------------------------- Part F
print("=" * 74); print("Part F.  Lemma 3 / Theorem 2(b): parity transversals are affine lines; the 21 partitions are rod tilings"); print("=" * 74)
def line_dir(t):
    t = sorted(t); d = tuple((t[1][k] - t[0][k]) % 3 for k in range(3))
    ok = all(((t[0][k] + 2 * d[k]) % 3) == t[2][k] for k in range(3))
    return min(d, tuple((-x) % 3 for x in d)) if ok else None
DIRS = [(1, 1, 2), (1, 2, 1), (1, 2, 2)]      # (1,2,2) = -(2,1,1)
from collections import Counter
dcount = Counter(line_dir(t) for t in PT0)
check("every parity transversal of rho_0 is an affine line", None not in dcount, True)
check("nine lines in each of the three directions", dict(dcount), {d: 9 for d in DIRS})
kinds = Counter(tuple(sorted(Counter(line_dir(t) for t in part).values())) for part in P0)
check("partitions by direction multiset: 3 single-direction, 18 two-direction (3 + 6)", dict(kinds), {(9,): 3, (3, 6): 18})
# the rod-tiling count of Theorem 2(b), done directly on the 3x3x3 array
RODS = [frozenset((x, y, z) for x in range(3)) for y in range(3) for z in range(3)] + \
       [frozenset((x, y, z) for y in range(3)) for x in range(3) for z in range(3)] + \
       [frozenset((x, y, z) for z in range(3)) for x in range(3) for y in range(3)]
def tilings(rem):
    if not rem: return 1
    c = min(rem); return sum(tilings(rem - r) for r in RODS if c in r and r <= rem)
check("rod tilings of the 3x3x3 array (1 + 12 + 8)", tilings(frozenset(CELLS)), 21)
check("1 + 12 + 8", 1 + 12 + 8, 21)
# change of basis d_i -> e_i is a bijection of the cells
M = [(1, 1, 2), (1, 2, 1), (2, 1, 1)]
imgs = {tuple(sum(a[j] * M[j][i] for j in range(3)) % 3 for i in range(3)) for a in itertools.product(range(3), repeat=3)}
check("d1, d2, d3 span F_3^3 (change of basis is a bijection)", len(imgs), 27)

# ---------------------------------------------------------------- Part G
print("=" * 74); print("Part G.  Section 6.5: measured cost of the canonical form (lexicographic minimum over G and over O_h)"); print("=" * 74)
import time, platform
GL = sorted(G)
OH = [p for p in GL if CELLS[p[IDX[(1, 1, 1)]]] == (1, 1, 1)]       # elements fixing the centre cell
check("|O_h| (elements of G fixing the centre cell)", len(OH), 48)
def random_template(rng):
    """A uniformly random DR-recoverable template with role pattern rho_0: a random partition of
    Theorem 2 and a random labelling of its nine parts; the block at a cell is encoded as role*9 + index."""
    part = rng.choice(P0); lab = list(range(9)); rng.shuffle(lab)
    out = [None] * 27
    for k, t in enumerate(part):
        for c in t: out[IDX[c]] = rho0[IDX[c]] * 9 + lab[k]
    return tuple(out)
def apply(p, t):
    """(g.t)(g(c)) = t(c): the block at cell i moves to cell p[i]."""
    img = [None] * 27
    for i in range(27): img[p[i]] = t[i]
    return tuple(img)
def canon(t, group):
    best = t
    for p in group:
        img = apply(p, t)
        if img < best: best = img
    return best
rng = random.Random(3)
SAMPLE = [random_template(rng) for _ in range(200)]
check("canonical form under G is G-invariant on a sample",
      all(canon(apply(g, t), GL) == canon(t, GL) for g in rng.sample(GL, 20) for t in SAMPLE[:10]), True)
check("canonical form under O_h is O_h-invariant on a sample",
      all(canon(apply(g, t), OH) == canon(t, OH) for g in OH for t in SAMPLE[:10]), True)
for name, grp in (("G, 1,296 permutations", GL), ("O_h, 48 permutations", OH)):
    reps = 3; best = None
    for _ in range(reps):
        t0 = time.perf_counter()
        for t in SAMPLE: canon(t, grp)
        dt = (time.perf_counter() - t0) / len(SAMPLE)
        best = dt if best is None else min(best, dt)
    print(f"  canonical form under {name}: {best * 1e3:.2f} ms per template (best of {reps} runs over {len(SAMPLE)} templates)")
print(f"  platform: Python {platform.python_version()}, {platform.system()} {platform.machine()}, {platform.processor() or 'processor not reported'}")

# ---------------------------------------------------------------- Part H
print("=" * 74); print("Part H.  Lemma 4, Corollary 4 and Section 6.7: planar Latin squares, two classes up to all relabellings, damage beyond the 36 cases"); print("=" * 74)
from math import comb
SQ = [(x, y) for x in range(3) for y in range(3)]
LS = set()
for v in itertools.product(range(3), repeat=9):
    L = dict(zip(SQ, v))
    if all(len({L[(x, y)] for x in range(3)}) == 3 for y in range(3)) and all(len({L[(x, y)] for y in range(3)}) == 3 for x in range(3)): LS.add(v)
AFF = {tuple((s * x + t * y + c) % 3 for x, y in SQ) for s in (1, 2) for t in (1, 2) for c in range(3)}
check("Latin squares of order 3 are exactly the 12 affine squares sx + ty + c", LS == AFF and len(LS) == 12, True)
def closure2(gens):
    idt = tuple(SQ); H = {idt}; fr = [idt]
    while fr:
        nx = []
        for p in fr:
            pm = dict(zip(SQ, p))
            for g in gens:
                q = tuple(g(pm[c]) for c in SQ)
                if q not in H: H.add(q); nx.append(q)
        fr = nx
    return H
XS_ = lambda c: ((c[0] + 1) % 3, c[1]); YS_ = lambda c: (c[0], (c[1] + 1) % 3); XR_ = lambda c: (2 - c[0], c[1]); RT_ = lambda c: (c[1], 2 - c[0])
PLANAR = closure2([XS_, YS_, XR_, RT_]); D4 = closure2([XR_, RT_])
check("|planar group| = 72 and |D_4| = 8", (len(PLANAR), len(D4)), (72, 8))
def act2(p, v):                      # (g.L)(g(c)) = L(c)
    pm = dict(zip(SQ, p)); L = dict(zip(SQ, v)); out = {pm[c]: L[c] for c in SQ}; return tuple(out[c] for c in SQ)
def orbits2(group, objs):
    seen = set(); sizes = []
    for o in objs:
        if o in seen: continue
        orb = {act2(p, o) for p in group}; seen |= orb; sizes.append(len(orb))
    return sorted(sizes)
check("12 Latin squares: one orbit under the planar group", orbits2(PLANAR, LS), [12])
check("12 Latin squares: three orbits of size 4 under D_4", orbits2(D4, LS), [4, 4, 4])
check("the D_4-orbit of a square is determined by its centre symbol", len({(frozenset({act2(p, v) for p in D4}), v[SQ.index((1, 1))]) for v in LS}), 3)
GL = [(a, b) for a in LS for b in LS if len({(a[i], b[i]) for i in range(9)}) == 9]
check("Graeco-Latin (orthogonal) ordered pairs", len(GL), 72)
def params(v):
    for s in (1, 2):
        for t in (1, 2):
            for c in range(3):
                if tuple((s * x + t * y + c) % 3 for x, y in SQ) == v: return (s, t, c)
check("orthogonal iff (s', t') != +-(s, t)", all((len({(a[i], b[i]) for i in range(9)}) == 9) == ((params(b)[:2] != params(a)[:2]) and (params(b)[:2] != tuple((-u) % 3 for u in params(a)[:2]))) for a in LS for b in LS), True)
check("the planar group acts on the 72 pairs freely: every orbit has size 72 (one orbit)", {len({(act2(p, a), act2(p, b)) for p in PLANAR}) for a, b in GL}, {72})
# Corollary 4: (G x S_3)-orbits on the 504 pairs (rho, P)
PAIRS = set()
for p in G:
    r = image_pattern(p, rho0)
    for part in P0: PAIRS.add((r, act(p, part)))
check("pairs (rho, P)", len(PAIRS), 504)
S3 = list(itertools.permutations(range(3)))
seen = set(); sizes = []
for pr in PAIRS:
    if pr in seen: continue
    orb = set()
    for p in G:
        r = image_pattern(p, pr[0]); part = act(p, pr[1])
        for s in S3: orb.add((tuple(s[v] for v in r), part))
    assert orb <= PAIRS
    seen |= orb; sizes.append(len(orb))
check("(G x S_3)-orbits on the 504 pairs: sizes 72 and 432", sorted(sizes), [72, 432])
check("72 x 9! + 432 x 9! = |V*3D|", 72 * 362880 + 432 * 362880, 182891520)
check("two classes of templates under G x S_3 x S_9", len(sizes), 2)
# Section 6.7: damage beyond the 36 designed cases, for every (rho, P)
RODS = [frozenset(r) for r in rods()]; SLABS = [frozenset(s) for s in slabs()]
def index_of(part):
    return {c: k for k, t in enumerate(part) for c in t}
def decodable_set(idx, E): return len({idx[c] for c in E}) == len(E)
two_rods = set(); in_slab = set(); out_slab = set(); rod_slab = set(); two_slabs = set()
rod_pairs = list(itertools.combinations(RODS, 2))
coplanar = [(a, b) for a, b in rod_pairs if any((a | b) <= s for s in SLABS)]
for _, part in PAIRS:
    idx = index_of(part)
    two_rods.add(sum(decodable_set(idx, a | b) for a, b in rod_pairs))
    in_slab.add(sum(decodable_set(idx, a | b) for a, b in coplanar))
    out_slab.add(sum(decodable_set(idx, a | b) for a, b in rod_pairs if (a, b) not in coplanar))
    rod_slab.add(sum(decodable_set(idx, a | s) for a in RODS for s in SLABS))
    two_slabs.add(sum(decodable_set(idx, a | b) for a, b in itertools.combinations(SLABS, 2)))
check("two erased rods decodable, out of 351 pairs (same for every (rho, P))", (two_rods, len(rod_pairs)), ({162}, 351))
check("  of which pairs in a common slab (all decodable)", (in_slab, len(coplanar)), ({135}, 135))
check("  and pairs not in a common slab", (out_slab, len(rod_pairs) - len(coplanar)), ({27}, 216))
check("rod + slab decodable = pairs with the rod inside the slab", (rod_slab, sum(1 for a in RODS for s in SLABS if a <= s)), ({54}, 54))
check("two erased slabs: never decodable", two_slabs, {0})
idx0 = index_of(P0[0])
check("k random cells decodable: C(9,k) 3^k / C(27,k) in %, k = 1..6, 9",
      [round(100 * comb(9, k) * 3 ** k / comb(27, k), 1) for k in (1, 2, 3, 4, 5, 6, 9)], [100.0, 92.3, 77.5, 58.2, 37.9, 20.7, 0.4])
check("  k = 2: the 27 pairs of cells in a common parity triple are the only undecodable pairs", comb(27, 2) - comb(9, 2) * 9, 27)
check("  checked directly for k = 2 on a template: decodable 2-sets", sum(decodable_set(idx0, set(E)) for E in itertools.combinations(CELLS, 2)), 324)
check("  checked directly for k = 3 on a template: decodable 3-sets", sum(decodable_set(idx0, set(E)) for E in itertools.combinations(CELLS, 3)), comb(9, 3) * 27)

print("\n" + ("All checks passed." if not FAIL else f"FAILED: {FAIL}"))
sys.exit(1 if FAIL else 0)
