# Verification scripts for the 3x3x3 DR Code

Repository: https://github.com/thawatchai2799/3D_DR_Code_20260714_2039

Reproduces every numerical and structural claim in

> T. Chomsiri and W. Sriphum,
> *Generalizing DR Code to Three Dimensions: Combinatorial Structure,
> Group-Theoretic Analysis, and Storage Implications of the 3x3x3 DR Code*,
> submitted to *Symmetry* (MDPI), 2026.

## Requirements

Python 3.9 or later. All three scripts use the standard library only, so there is
nothing to install.

## Run

```
./run_all.sh          # macOS / Linux
run_all.bat           # Windows
```

or individually

```
python3 verify_3d_recovery.py
python3 verify_3d_group.py
python3 verify_3d_round2.py
```

Combined runtime is about a minute. Each script compares every value it
computes against the figure quoted in the paper, prints `OK` or `MISMATCH`
for each, and exits with status 1 if anything fails to reproduce.

## Additional checks (`verify_3d_round2.py`)

`verify_3d_round2.py` adds the following checks without modifying the two
main scripts:

| check | paper |
|---|---|
| the non-role-balanced template of Corollary 1 recovers all 36 damage cases (erase-and-XOR) | Corollary 1 |
| 40 partitions into coordinate transversals when the role condition is dropped | Remark 1 |
| 27 parity transversals and 21 partitions for the canonical role pattern rho_0, and 21 for every one of the 24 patterns | Theorem 2 |
| the 21 partitions printed as the certificate of Appendix A | Appendix A |
| 24 Latin cubes = 12 Latin squares x 2 discordant symbol-shifts | Section 2.2 |

Composition convention: `verify_3d_group.py` composes permutations from left to
right (`compose(a, b)` applies `a` first and then `b`), which is the convention
stated in the paper and used by GAP; under this convention
`sigma_Rz sigma_Cx sigma_Rz^-1 = sigma_Cy^2`. Under right-to-left composition the
same identity reads `sigma_Rz sigma_Cx sigma_Rz^-1 = sigma_Cy`.

## Relation to `DR27.py`

`DR27.py` is the original role-pattern enumerator for the 3x3x3 DR Code. It
works at the *role level* only: it enumerates the 24 role patterns (Latin cubes
of order 3) in which every axis-parallel line carries one A-block, one B-block
and one C-block. That condition alone does not guarantee XOR recoverability.
Recovery depends on the nine parity triples `G_r = {A_r, B_r, C_r}`: a line
labelled `A0, B0, C0` is role-balanced yet destroys the whole of `G_0` when
erased. The paper therefore works with the labelled-block model, and the
verification scripts in this repository implement that model.

| | role-level model (`DR27.py`) | labelled-block model (the paper) |
|---|---|---|
| recoverability condition | every line carries each role once | the parity index is a bijection onto 0..8 on each of the nine slabs (Theorem 1) |
| recoverable templates | 24 x (9!)^3 = 1,146,833,420,156,928,000 | 24 x 21 x 9! = **182,891,520** (Theorem 2) |
| orbits under the symmetry group | 884,902,330,368,000 | **141,120** (Theorem 5) |
| storage, flat index | 62 bits | **28 bits** |
| verification of recovery | inferred from the combinatorics | every rod and slab erased and decoded |
| script | `DR27.py` (role patterns only) | `verify_3d_recovery.py`, `verify_3d_group.py`, `verify_3d_round2.py` |

The role-level results are common to both models: there are 24 role patterns,
the symmetry group is the semi-direct product `(C3 x C3 x C3) : O_h` of order
1,296, and the 24 role patterns form a single orbit with stabiliser of order 54.

`DR27.py` is kept in the repository for the record. It enumerates the 24 role
patterns correctly, but it does not test recoverability and its count of
`24 x (9!)^3` full templates is not a count of recoverable templates and should
not be cited as one.

## What each script checks

### `verify_3d_recovery.py`

The erasure model and the enumeration against it.

- **Part 1** builds a template from the role pattern of Figure 2, relabels one
  line `A0, B0, C0`, erases each of the 36 damage cases and runs the decoder:
  16 of 27 rods and 0 of 9 slabs decode. This is the counterexample of
  Corollary 1.
- **Part 2** checks criterion (2) of Theorem 1 against the decoder on 4,000
  random templates: the two agree on every one.
- **Part 3** constructs an explicit DR-recoverable template, prints it, erases
  each of the 36 damage cases and decodes them all.
- **Part 4** samples 20,000 templates that satisfy the role-level condition only and
  finds none that decodes all 36 cases.
- **Part 5** counts the DR-recoverable templates by two unrelated methods,
  exact cover by parity transversals and a cell-pairing search, both giving
  21 partitions per role pattern and hence `24 x 21 x 9! = 182,891,520`, and
  confirms the 27 transversals and 21 partitions for every one of the 24 role
  patterns.
- **Part 5** also counts the larger set of Remark 1, templates that satisfy
  criterion (2) alone with no role condition: 40 partitions, hence
  40 x 9! x 6^9 = 146,279,772,979,200, recorded for comparison.
- **Part 6** verifies that the group of order 1,296 permutes the slabs, that
  the orbit of the explicit template has size 1,296, and that the orbit count
  is 141,120.
- **Part 7** reproduces every storage figure of Section 6.1.

### `verify_3d_group.py`

The role-level and group-theoretic results.

- **Part 1** enumerates the 24 role patterns by Algorithm 1 and checks the
  27 lines, 9 slabs and the two-slabs-per-rod fact.
- **Part 2** checks that the coordinate formula printed in the paper for each
  of the nine generators matches the permutation it implements, and that the
  orders are 4, 2 and 3.
- **Part 3** builds `G` by breadth-first closure and confirms `|G| = 1,296`,
  `|O_h| = 48`, `|N| = 27` and the element orders of the rotation subgroup.
- **Part 4** verifies the hypotheses of the internal semi-direct-product
  theorem, the conjugation identity `sigma_Rz sigma_Cx sigma_Rz^-1 = sigma_Cy^2`,
  and that `O_h -> Aut(N)` is injective.
- **Part 5** recomputes all six rows of Table 2.
- **Part 6** verifies the single orbit and the stabiliser of order 54.
- **Part 7** prints the fixed-point distribution `0: 1,113  6: 152  12: 30
  24: 1`, the weighted sum 1,296, and the Burnside orbit count 1.
- **Part 8** reproduces the remaining arithmetic quoted in Sections 2 and 6.

## Files

| file | purpose |
|---|---|
| `verify_3d_recovery.py` | erasure model, decoder, enumeration, orbits, storage |
| `verify_3d_group.py` | role patterns, generators, group structure, Table 2, Burnside |
| `DR27.py` | the original role-pattern enumerator (role level only), kept for the record |
| `verify_3d_round2.py` | additional checks: Corollary 1 template, 40 partitions of Remark 1, 27/21 for every role pattern, Appendix A certificate, 24 = 12 x 2 |
| `run_all.sh`, `run_all.bat` | run the three verification scripts in order |
| `figures/` | the ten figures of the paper, each as a 600-dpi PNG and as a PDF (Figures 5, 6 and 9 are vector) |
| `requirements.txt` | records that there are no dependencies |
| `LICENSE` | MIT |
| `README.md` | this document |

## Figures

The `figures/` directory holds the ten figures of the manuscript submitted to
*Symmetry*, named `Figure_01_cube` to `Figure_10_2D_vs_3D`.
Every figure is provided as a 600-dpi PNG, identical to the image embedded in the
manuscript, and as a PDF; Figures 5, 6 and 9 are vector PDFs produced by
matplotlib, the others are the PNG embedded losslessly. Figures 5 and 6 were
redrawn for the Symmetry submission so that all block diagrams share one
style (role colours A blue, B red, C green; erased blocks grey); their content
is unchanged.

## Licence

MIT. See `LICENSE`.
