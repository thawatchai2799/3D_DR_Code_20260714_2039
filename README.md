# Verification scripts for the 3x3x3 DR Code

Repository: https://github.com/thawatchai2799/3D_DR_Code_20260714_2039

Reproduces every numerical and structural claim in

> T. Chomsiri and W. Sriphum,
> *Generalizing DR Code to Three Dimensions: Combinatorial Structure,
> Group-Theoretic Analysis, and Storage Implications of the 3x3x3 DR Code*,
> Mathematics (MDPI), manuscript mathematics-4471756, major revision.

## Requirements

Python 3.9 or later. Both scripts use the standard library only, so there is
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
```

Combined runtime is under a minute. Each script compares every value it
computes against the figure quoted in the paper, prints `OK` or `MISMATCH`
for each, and exits with status 1 if anything fails to reproduce.

## What changed in the major revision

The submitted version of the paper defined a recoverable template by a
*role-level* condition: every axis-parallel line carries one A-block, one
B-block and one C-block. The third referee showed that this condition does not
guarantee XOR recoverability. Recovery depends on the nine parity triples
`G_r = {A_r, B_r, C_r}`, and a line labelled `A0, B0, C0` is role-balanced yet
destroys the whole of `G_0` when erased. The revision replaces the model, and
the scripts in this repository replace the enumerator that accompanied the
submitted version.

| | submitted version | major revision |
|---|---|---|
| recoverability condition | every line carries each role once | the parity index is a bijection onto 0..8 on each of the nine slabs (Theorem 1) |
| recoverable templates | 24 x (9!)^3 = 1,146,833,420,156,928,000 | 24 x 21 x 9! = **182,891,520** (Theorem 2) |
| orbits under the symmetry group | 884,902,330,368,000 | **141,120** (Theorem 5) |
| storage, flat index | 62 bits | **28 bits** |
| verification of recovery | inferred from the combinatorics | every rod and slab erased and decoded |
| enumerator released | `DR27.py` (role patterns only) | `verify_3d_recovery.py` and `verify_3d_group.py` |

The role-level results are unchanged and are retained: there are 24 role
patterns (Latin cubes of order 3), the symmetry group is the semi-direct
product `(C3 x C3 x C3) : O_h` of order 1,296, and the 24 role patterns form a
single orbit with stabiliser of order 54.

`DR27.py` is kept in the repository for the record. It enumerates the 24 role
patterns correctly, but it does not test recoverability and its count of
`24 x (9!)^3` full templates should no longer be cited.

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
- **Part 4** samples 20,000 templates drawn as the old Theorem 1 describes and
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
| `DR27.py` | the role-pattern enumerator of the submitted version, kept for the record |
| `run_all.sh`, `run_all.bat` | run both verification scripts in order |
| `requirements.txt` | records that there are no dependencies |
| `LICENSE` | MIT |
| `README.md` | this document |

## Licence

MIT. See `LICENSE`.
