from face import *
from cubie import *

from array import *
from collections import deque


_MAX_MOVE_COUNT = 3

def _gen_movetable(n, coord, mul):
    moves = [array('i', [-1] * _MAX_MOVE_COUNT * N_COLORS) for _ in range(n)]

    c = CubieCube.make_solved()
    for i in range(n):
        c.set_coord(coord, i)
        for face in range(N_COLORS):
            for cnt in range(_MAX_MOVE_COUNT):
                c.mul(mul, MOVES[face])
                moves[i][_MAX_MOVE_COUNT * face + cnt] = c.get_coord(coord)
            c.mul(mul, MOVES[face]) # restore original state

    print('Generated move table.')
    return moves

_N_COORDS = [
    2187, # 3^7; TWIST
    2048, # 2^11; FLIP
    11880, # 12!/(12-4)!; FRBR
    20160, # 8!/(8-6)!; URFDLF
    1320, # 12!/(12-3)!; URUL
    1320, # 12!/(12-3)!; UBDF
    20160 # 8!/(8-6)!; URDF
]
_MUL = [CORNERS, EDGES, EDGES, CORNERS, EDGES, EDGES, EDGES] # TWIST, FLIP, FRBR, URFDLF, URUL, UBDF, URDF

# TWIST, FLIP, FRBR, URFDLF, URUL, UBDF, URDF
MOVE = [_gen_movetable(_N_COORDS[i], i, _MUL[i]) for i in range(len(_N_COORDS))]

PAR = 7
MOVE.append([
    array('i', [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1]),
    array('i', [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0])
]) # ..., PAR
_N_COORDS.append(2) # ..., PAR


def _set_prun(table, i, v):
    table[i>>1] &= (v << 4) if i & 1 else v

def _get_prun(table, i):
    tmp = table[i>>1]
    return ((tmp & 0xf0) >> 4) if i & 1 else tmp & 0x0f

_N_FRBR_1 = 495 # 12 choose 4
_N_FRBR_2 = 24 # 4!

def _gen_phase1_pruntable(n, coord):
    # Make all bits on per default -> detect empty cells as 0xf
    prun = array('B', [255] * n)

    _set_prun(prun, 0, 0)
    _q = deque([0])

    while len(_q) != 0:
        i = _q.popleft()
        c = i // _N_FRBR_1
        frbr = i % _N_FRBR_1

        for m in range(_MAX_MOVE_COUNT * N_COLORS):
            # Permutation irrelevant for phase 1
            j = _N_FRBR_1 * MOVE[coord][c][m] + MOVE[FRBR][frbr * _N_FRBR_2][m] / _N_FRBR_2
            if _get_prun(prun, j) == 0x0f:
                _set_prun(prun, j, _get_prun(prun, i) + 1)
                _q.append(j)

    print('Generated phase 1 pruning table.')
    return prun

_N_PER_BYTE = 2

FRBR_TWIST_PRUN = _gen_phase1_pruntable(_N_COORDS[TWIST] * _N_FRBR_1 / _N_PER_BYTE + 1, TWIST)
FRBR_FLIP_PRUN = _gen_phase1_pruntable(_N_COORDS[FLIP] * _N_FRBR_1 / _N_PER_BYTE, FLIP)

_PHASE_2_MOVES = [0, 1, 2, 4, 7, 9, 10, 11, 13, 16] # U, U2, U', R2, F2, D, D2, D', L2, B2

def _gen_phase2_pruntable(coord):
    prun = array('B', [255] * (_N_FRBR_2 * _N_COORDS[coord] * _N_COORDS[PAR] / _N_PER_BYTE))

    _set_prun(prun, 0, 0)
    _q = deque([0])

    while len(_q) != 0:
        i = _q.popleft()
        par = i % _N_COORDS[PAR]
        c = (i // _N_COORDS[PAR]) // _N_FRBR_2
        frbr = (i // _N_COORDS[PAR]) % _N_FRBR_2

        for m in _PHASE_2_MOVES:
            j = (_N_FRBR_2 * MOVE[coord][c][m] + MOVE[FRBR][frbr][m]) * _N_COORDS[PAR] + MOVE[PAR][par][m]
            if _get_prun(prun, j) == 0x0f:
                _set_prun(prun, j, _get_prun(prun, i) + 1)
                _q.append(j)

    print('Generated phase 2 pruning table.')
    return prun

FRBR_URFDLF_PAR_PRUN = _gen_phase2_pruntable(URFDLF)
FRBR_URDF_PAR_PRUN = _gen_phase2_pruntable(URDF)

URDF_MERG = [merge_urdf(i, j) for i in range(_N_COORDS[URUL]) for j in range(_N_COORDS[UBDF])]
print('Generated merge table.')
