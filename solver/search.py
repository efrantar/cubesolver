from face import face_to_cubie
from coord import *
from coord import _N_COORDS, _PHASE2_MOVES


_PHASE1_COORDS = [TWIST, FLIP, FRBR]
_PHASE2_COORDS = [FRBR, URFDLF, URDF, PAR]
_PHASE12_COORDS1 = [URFDLF, PAR]
_PHASE12_COORDS2 = [URUL, UBDF]

_PHASE2_DMAX = 10

_DMAX = 50
_coords = [[-1] * len(_N_COORDS) for _ in range(_DMAX)]
_moves = [-MAX_MOVE_COUNT] * _DMAX # make sure that the last entry // MAX_MOVE_COUNT is always -1

COUNT = [0]

def phase1(d, dmax):
    prun = max(
        get_prun(FRBR_TWIST_PRUN, phase1_prun_idx(_coords[d][TWIST], _coords[d][FRBR])),
        get_prun(FRBR_FLIP_PRUN, phase1_prun_idx(_coords[d][FLIP], _coords[d][FRBR]))
    )

    if prun > dmax - d:
        return -1
    if prun == 0:
        dmax = min(d + _PHASE2_DMAX, _DMAX)

        for i in range(d):
            _move(i, _moves[i], _PHASE12_COORDS1)

        if get_prun(
            FRBR_URFDLF_PAR_PRUN, phase2_prun_idx(_coords[d][URFDLF], _coords[d][FRBR], _coords[d][PAR])
        ) > dmax - d:
            return -1

        for i in range(d):
            _move(i, _moves[i], _PHASE12_COORDS2)
        _coords[d][URDF] = URDF_MERG[_coords[d][URUL]][_coords[d][UBDF]]

        return phase2(d, dmax)

    for m in range(N_MOVES):
        if m // MAX_MOVE_COUNT != _moves[d-1] // MAX_MOVE_COUNT:
            _move(d, m, _PHASE1_COORDS)
            tmp = phase1(d + 1, dmax)
            if tmp != -1:
                return tmp
    return -1

def phase2(d, dmax):
    prun = max(
        get_prun(FRBR_URFDLF_PAR_PRUN, phase2_prun_idx(_coords[d][URFDLF], _coords[d][FRBR], _coords[d][PAR])),
        get_prun(FRBR_URDF_PAR_PRUN, phase2_prun_idx(_coords[d][URDF], _coords[d][FRBR], _coords[d][PAR]))
    )
    if prun > dmax - d:
        return -1
    if prun == 0:
        return d

    for m in _PHASE2_MOVES:
        if m // MAX_MOVE_COUNT != _moves[d-1] // MAX_MOVE_COUNT:
            _move(d, m, _PHASE2_COORDS)
            tmp = phase2(d + 1, dmax)
            if tmp != -1:
                return tmp
    return -1

def search(s, max):
    c = face_to_cubie(s)

    _coords[0] = [c.get_coord(i) if i != URDF else -1 for i in range(len(_N_COORDS))]

    global _DMAX
    _DMAX = max
    for i in range(max + 1):
        if phase1(0, i) != -1:
            print('Solved!')
            return

def _move(d, m, cs):
    for c in cs:
        _coords[d+1][c] = MOVE[c][_coords[d][c]][m]
    _moves[d] = m


# search('UUUUUUUUUBBBRRRRRRRRRFFFFFFDDDDDDDDDFFFLLLLLLLLLBBBBBB', 21)
# search('UUUUUULLLURRURRURRFFFFFFFFFRRRDDDDDDLLDLLDLLDBBBBBBBBB', 21)
# search('BLDBURUDBLBBBRRLFURRDDFDFUDRLFRDULLLRUFLLFUFDRFUUBDFBB', 21)

import time
t = time.time()
search('BLDBURUDBLBBBRRLFURRDDFDFUDRLFRDULLLRUFLLFUFDRFUUBDFBB', 21)
search('UDDUUBFUUFRBURBBDBRFLDFRLFDFRLBDFULLBLDFLLFUDRRRDBLUBR', 21)
search('BDLBUDBRDBBFURFBRLRDLBFFFLRRBDUDUFFDUUUFLRRLDULLDBRFLU', 21)
search('LBLLUUUBDFRDLRLFFDBURRFUBFRURUFDUFRBDBRFLBUDLFDBDBLRDL', 21)
search('LLDRUUFDDRBFRRFLFFUBBUFBUFFBLURDULLDBDRFLLBURLDUDBRRBD', 21)
print(time.time() - t)