from control import *
import time

MOVES = [
    "U", "U2", "U'", "R", "R2", "R'", 
    "F", "F2", "F'", "D", "D2", "D'", 
    "L", "L2", "L'", "B", "B2", "B'"
]

def moves(s):
    return [MOVES.index(s) for s in s.split(' ')]

SEQ1 = [3, 14, 1, 10, 12, 1, 13, 6, 2, 11, 3, 8, 0, 11, 5, 12, 9, 8, 0, 5, 14, 6, 5, 14, 6, 5]
SEQ2 = [0, 9, 6, 11, 5, 2, 3, 2, 11, 5, 14, 6, 5, 14, 6, 2, 14, 7, 4, 7, 0, 11, 4]
SEQ3 = [3, 12, 1, 5, 13, 2, 11, 2, 11, 5, 6, 0, 11, 14, 9, 12, 11, 13, 0, 3, 2, 11, 3, 12, 8]

robot = Robot()
print('Connected.')

tick = time.time()

# robot.execute(moves("U D L"))
    
robot.execute(SEQ3)

# CUT 
# robot.execute(moves("L D' R U' F L' D R' U F' L D' R U' F L' D R' U F'"))
# ANTICUT
# robot.execute(moves("L D R U F L D R U F L D R U F L D R U F"))
# AX_CUT
# robot.execute(moves("L R U' L R F' L R D' L R U' L R F' L R"))
# AX_PARTCUT
# robot.execute(moves("L R' U L R' F L R' D"))
# AX_ANTICUT
# robot.execute(moves("L R U L R F L R D"))
# AXAX_CUT
# robot.execute(moves("L R U' D' L R U' D' L R U' D' L R"))
# AXAX_PARTCUT
# robot.execute(moves("L R' U D' L R' U D' L R' U D' L R'"))
# AXAX_ANTICUT
# robot.execute(moves("L R U D L R U D L R U D L R U D L R"))

print(time.time() - tick)

