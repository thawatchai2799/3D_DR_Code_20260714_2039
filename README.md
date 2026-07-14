# DR27 — DR Code 3D Pattern Enumerator and Verifier

Companion code for the paper:

> W. Sriphum and T. Chomsiri, **"Generalizing DR Code to Three Dimensions:
> Combinatorial Structure, Group-Theoretic Analysis, and Storage Implications
> of the 3×3×3 DR Code"**, 2026.

The DR Code (Data Restorable Code) is an XOR-parity barcode originally
proposed as a 2D 3×3 grid (Sriphum, IEEE CSE 2013). This repository contains
`DR27.py`, which generalizes the structure to a 3×3×3 cube of 27 logical
blocks in three classes (A, B, C with Cᵢ = Aᵢ ⊕ Bᵢ), enumerates all valid
class-level patterns, and verifies every combinatorial and group-theoretic
claim made in the paper by exhaustive computation.

## What the script computes and verifies

**Enumeration (Section 4 of the paper)**

| Quantity | Value |
|---|---|
| Class-level patterns (Latin cubes of order 3, [OEIS A076389](https://oeis.org/A076389)) | **24** |
| Full 3D DR Code templates, 24 × (9!)³ (Theorem 1) | **1,146,833,420,156,928,000 ≈ 1.15 × 10¹⁸** |
| Recoverable damage cases (27 rods + 9 slabs) | **36** |

The enumerator uses backtracking with constraint propagation (Algorithm 1):
per-line class counters give an O(1) feasibility test, completing the
class-level enumeration in well under 0.01 s — versus an infeasible direct
search over 27! ≈ 1.09 × 10²⁸ placements.

**Group-theoretic verification (Section 5 of the paper)**

The symmetry group is constructed explicitly as a permutation group on the
27 cells from nine generators (three 90° rotations, three mirrors, three
cyclic shifts), and the following are verified exhaustively:

- |O_h| = 48, |N| = |C₃×C₃×C₃| = 27, **|G| = 1,296** — computed, not assumed
- N is normal in G, O_h is not, N ∩ O_h = {id} ⟹ **G ≅ (C₃×C₃×C₃) ⋊ O_h**
  (Theorem 3)
- All 24 class patterns form a **single orbit** under G with stabilizer of
  order 54 (Theorem 4)
- Burnside fixed-point distribution |Fix(g)|: 0 for 1,113 elements, 6 for
  152, 12 for 30, 24 for the identity alone; Σ|Fix(g)| = 1,296 = |G| ⟹
  exactly 1 orbit (Section 5.3.2)
- Orbit decomposition of the 24 patterns under five canonical subgroups,
  reproducing TABLE 2 of the paper
- Full-template orbit count |V₃D| / |G| = **884,902,330,368,000 ≈ 8.85 × 10¹⁴**

Every check is enforced with `assert`; the script exits successfully only if
all results match the paper.

## Usage

```bash
python3 DR27.py
```

Requires Python 3.8+ and only the standard library. Runtime is a few seconds
(dominated by the Burnside check over all 1,296 group elements). The script
also writes `DR27_class_patterns.txt` listing all 24 class-level patterns
layer by layer.

## Reproducibility note

The results of this script have additionally been cross-validated by an
independently written implementation (different cell indexing and constraint
check), which produced the same 24 patterns and identical values for every
group-theoretic quantity.

## Related work

- 2D DR Code: W. Sriphum, "DR Code: The Two Dimensions Barcode Supporting
  High Rate Data Recovery", in *Proc. IEEE CSE*, 2013, pp. 1214–1219.
- Companion 2D analysis: W. Sriphum and T. Chomsiri, "On the Equivalence
  Classes of Recoverable Patterns in DR Code: A Group-Theoretic Analysis
  with Applications to Storage Optimization" (under review).

## License

MIT — see [LICENSE](LICENSE).
