# Robot control.

from cmd import *
from collections import namedtuple
import time
import ev3


# We also consider inverted half-moves here

def are_parallel(m1, m2):
    return abs(m1 // 4 - m2 // 4) == 3

def is_axial(move):
    return isinstance(move, tuple)

def is_half(move):
    if is_axial(move):
        return is_half(move[0]) or is_half(move[1])
    return (move % 4) % 2 == 1

def is_clock(move):
    return move % 4 <= 1

# All possible corner cutting situations
CUT = 0
ANTICUT = 1
AX_CUT1 = 2 # simple -> axial
AX_CUT2 = 3 # axial -> simple
AX_PARTCUT1 = 4
AX_PARTCUT2 = 5
AX_ANTICUT1 = 6
AX_ANTICUT2 = 7
AXAX_CUT = 8
AXAX_PARTCUT = 9
AXAX_ANTICUT = 10

def cut(m1, m2, inverted=False):
    if is_axial(m1) and not is_axial(m2):
        return cut(m2, m1, inverted=True) + 1
    if is_axial(m1) and is_axial(m2):
        return AXAX_CUT + (max(cut(m1, m2[0]), cut(m1, m2[1])) // 2 - 1)
    
    if not is_axial(m2):
        return CUT if is_clock(m1) != is_clock(m2) else ANTICUT
    
    m21, m22 = m2
    clock1 = is_clock(m21)
    clock2 = is_clock(m22)

    # Note that a special axial move only yields a simple incoming cut but not
    # an outcoming one
    if not inverted:
        if is_half(m21):
            if not is_half(m22):
                return CUT if clock1 != is_clock(m1) else ANTICUT
        else:
            if is_half(m22):
                return CUT if clock2 != is_clock(m1) else ANTICUT

    if clock1 == clock2:
        return AX_CUT1 if clock1 != is_clock(m1) else AX_ANTICUT1
    return AX_PARTCUT1

def is_clock(m):
    return m % 4 <= 1

def optim_halfdirs(sol):
    def inv(m):
        return (m // 4) * 4 + ((m + 2) % 4)

    options = [[] for _ in range(len(sol))]
    for i in range(len(sol)):
        if is_axial(sol[i]):
            m1, m2 = sol[i]
            options[i].append(sol[i])
            if is_half(m1):
                options[i].append((inv(m1), m2))
            if is_half(m2):
                options[i].append((m1, inv(m2)))
            if is_half(m1) and is_half(m2):
                options[i].append((inv(m1), inv(m2)))
        else:
            options[i].append(sol[i])
            if is_half(sol[i]):
                options[i].append(inv(sol[i]))

    DP = [[float('inf')] * 4 for _ in range(len(sol))]
    PD = [[-1] * 4 for _ in range(len(sol))]

    DP[0] = [0] * 4
    for i in range(1, len(sol)):
        for j, op2 in enumerate(options[i]):
            for k, op1 in enumerate(options[i - 1]):
                tmp = DP[i - 1][k] + WAITDEG[cut(op1, op2)]
                if tmp < DP[i][j]:
                    DP[i][j] = tmp
                    PD[i][j] = k

    j = 0
    for i in range(4):
        if DP[-1][i] < DP[-1][j]:
            j = i
    sol1 = [options[-1][j]]
    for i in range(len(sol) - 2, -1, -1):
        sol1.append(options[i][j])
        j = PD[i][j]
    sol1.reverse()
    return sol1


WAITDEG = [
    20, # CUT
    18, # ANTICUT
    24, # AX_CUT1
    24, # AX_CUT2
    22, # AX_PARTCUT1
    22, # AX_PARTCUT2
    20, # AX_ANTICUT1
    20, # AX_ANTICUT2
    24, # AXAX_CUT
    22, # AXAX_PARTCUT
    24  # AXAX_ANTICUT
]

WAITDEG_HALF = 41
SPECIAL_AX_WAITDEG = 5

Motor = namedtuple('Motor', ['brick', 'ports'])

DEGS = [0, -54, -108, 108, 54]
COUNT = [-1, -2, 1, -2] # we have to invert directions from the perspective of the motors

class Robot:

    HOSTS = [
        '00:16:53:7F:36:D9',
        '00:16:53:40:CE:B6',
        '00:16:53:4A:BA:BA'
    ]

    FACE_TO_MOTOR = [
        Motor(2, ev3.PORT_A + ev3.PORT_B),
        Motor(1, ev3.PORT_A + ev3.PORT_B),
        Motor(0, ev3.PORT_C + ev3.PORT_D),
        Motor(2, ev3.PORT_C + ev3.PORT_D),
        Motor(1, ev3.PORT_C + ev3.PORT_D)
    ]

    def __init__(self):
        self.bricks = [
            ev3.EV3(protocol='Usb', host=host) for host in Robot.HOSTS
        ]

    def move(self, m, prev, next):
        motor = Robot.FACE_TO_MOTOR[m // 4]
        deg = DEGS[COUNT[m % 4]]

        if next is None:
            # Cube can be considered solved once the final turn is < 45 degrees before completion
            waitdeg = abs(deg) - (27 - 1)
        else:
            waitdeg = WAITDEG[cut(m, next)]
            if is_half(m):
                waitdeg += WAITDEG_HALF

        print(waitdeg)
        rotate(self.bricks[motor.brick], motor.ports, deg, waitdeg)

    def move1(self, m, prev, next):
        m1, m2 = m
        motor1, motor2 = Robot.FACE_TO_MOTOR[m1 // 4], Robot.FACE_TO_MOTOR[m2 // 4]
        count1, count2 = COUNT[m1 % 4], COUNT[m2 % 4]
        deg1, deg2 = DEGS[count1], DEGS[count2]
    
        if next is None:
           waitdeg = max(deg1, deg2) - (27 - 1)
        else:
            waitdeg = WAITDEG[cut(m, next)]
            if is_half(m):
                waitdeg += WAITDEG_HALF

        # Half-turn + quarter-turn case
        if (abs(count1) == 2) != (abs(count2) == 2):
            if abs(count2) == 2:
                return self.move1((m2, m1), prev, next)
            rotate2(
                self.bricks[motor1.brick], motor1.ports, motor2.ports, deg1, deg2,
                SPECIAL_AX_WAITDEG, waitdeg
            )
        else:
            # We always want to wait on the move with the worse in-cutting
            if prev is not None and WAITDEG[cut(prev, m[0])] > WAITDEG[cut(prev, m[1])]:
                return self.move1((m2, m1), prev, next)
            rotate1(self.bricks[motor1.brick], motor1.ports, motor2.ports, deg1, deg2, waitdeg)

    def execute(self, sol):
        if len(sol) == 0:
            return

        # Convert to numbering that includes inverse half-turns
        sol = [(m // 3) * 4 + (m % 3) for m in sol]
        sol1 = []
        i = 0
        while i < len(sol):
            if i < len(sol) - 1 and are_parallel(sol[i], sol[i + 1]):
                sol1.append((sol[i], sol[i + 1]))
                i += 2
            else:
                sol1.append(sol[i])
                i += 1
        sol1 = optim_halfdirs(sol1)
        print(len(sol1), sol1)

        for i in range(len(sol1)):
            prev = sol1[i - 1] if i > 0 else None
            next = sol1[i + 1] if i < len(sol1) - 1 else None
            
            print(Robot.FACE_TO_MOTOR[sol[i] // 4].brick)
            tick = time.time()
            if is_axial(sol1[i]):
                self.move1(sol1[i], prev, next)
            else:
                self.move(sol1[i], prev, next)
            print(time.time() - tick)            

    def solve_pressed(self):
        return is_pressed(self.bricks[2], 3) # Right button

    def scramble_pressed(self):
        return is_pressed(self.bricks[0], 0) # Left button

