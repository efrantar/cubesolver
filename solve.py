from subprocess import Popen, PIPE
import time

N_THREADS = 12 # number of threads to use for solving
TIME = 50 # solving time in milliseconds

# This is the move-order used by the solver
NAME_TO_MOVE = {m: i for i, m in enumerate([
    "U", "U2", "U'", "R", "R2", "R'", "F", "F2", "F'", 
    "D", "D2", "D'", "L", "L2", "L'"
])}

# Transforms a solution string returned from the solver into a sequence of moves to be executed 
# by the robot. This includes conversion of move names into IDs and merging of consecutive
# quarter-turns (also axial ones) into half-turns.
def convert_sol(sol):
    if sol == '': # catch easy case to avoid any trouble below
        return []
    splits = sol.replace('(', '').replace(')', '').split(' ')
    axial = [('(' in m) for m in sol.split(' ')] # where axial moves start

    # Perform the merging; note that we will never have to match a simple quarter turn
    # with a consecutive axial turn or a simple quarter turn with a non-adjacent simple 
    # quarter-turn as such solutions are never returned by the solver
    splits1 = []
    i = 0
    while i < len(splits):
        if axial[i] and i < len(splits) - 2:
            if axial[i + 2]: # `splits[i + 3]` must exist
                if splits[i] == splits[i + 2] and splits[i + 1] == splits[i + 3]:
                    splits1.append('%s2' % splits[i][:1])
                    splits1.append('%s2' % splits[i + 1][:1])
                    i += 4
                else:
                    splits1 += splits[i:(i + 2)]
                    i += 2
            else:
                if splits[i] == splits[i + 2]:
                    splits1.append('%s2' % splits[i][:1])
                    splits1 += splits[(i + 1):(i + 4):2] # in case there is no element `(i + 3)`
                    i += 4
                elif i < len(splits) - 3 and splits[i + 1] == splits[i + 2]:
                    splits1.append(splits[i])
                    splits1.append('%s2' % splits[i + 1][:1])
                    splits1.append(splits[i + 3])
                    i += 4
                else:
                    splits1 += splits[i:(i + 2)]
                    i += 2
        else:
            if i < len(splits) - 1 and splits[i] == splits[i + 1]:
                # We will never get into here if `axial[i + 1]`
                splits1.append(splits[i][:1] + '2')
                i += 2
            else:
                splits1.append(splits[i])
                i += 1

    return [NAME_TO_MOVE[m] for m in splits1] # finally convert names to move IDs

# Simple Python interface to the interactive mode of the "twophase" solver
class Solver:

    def __enter__(self):
        self.proc = Popen(
            ['./twophase', '-t', str(N_THREADS), 'interactive'], stdin=PIPE, stdout=PIPE
        )
        while 'Ready!' not in self.proc.stdout.readline().decode():
            pass # wait for everything to boot up
        return self # `__enter__` must retrun reference to initialized object

    def __exit__(self, exception_type, exception_value, traceback):
        self.proc.terminate()

    def solve(self, facecube):
        self.proc.stdin.write(('%s -1 %d\n' % (facecube, TIME)).encode())
        self.proc.stdin.flush() # command needs to be received instantly
        sol = self.proc.stdout.readline().decode()[:-1] # strip trailing '\n'
        self.proc.stdout.readline() # lear time taken message
        self.proc.stdout.readline() # clear "Ready!" message 
        return convert_sol(sol) if 'Error' not in sol else None

