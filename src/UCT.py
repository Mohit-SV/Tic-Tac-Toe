# The purpose of this class is to provide a layout to play the game
import math
import random
from copy import deepcopy


class Layout:
    def __init__(self, layout=None):
        # initializing the player's tic symbols
        self.playerOne = 'X'
        self.playerTwo = 'O'
        self.blank = '_'
        # assigning the board position
        # There are nine possible positions in the game
        # 1,2,3,4,5,6,7,8,9
        # Every position represents a grid in a matrix
        self.position = {}

        # create an empty layout
        self.emptyLayout(emptyValue=self.blank)

        # clone the previous board state if available
        if layout is not None:
            self.__dict__ = deepcopy(layout.__dict__)

    def randomMove(self):
        values = []
        for pos in range(1, len(self.position) + 1):
            if self.position.get(pos) == self.blank:
                values.append(pos)
        return random.choice(values)

    def start(self):
        print(self)
        solver = Solver()
        while True:
            # ip = input("Your chance: ")
            try:
                # self = self.newMove(int(ip))
                self = self.newMove(int(self.randomMove()))
                print(self)
                optimalChance: TreeNode = solver.find(self)
                try:
                    self = optimalChance.layout
                except:
                    pass
                print(self)
                if self.isWin():
                    print('%s' % self.playerTwo)
                    break
                elif self.isMatchDrawn():
                    print('Bruhhhh Drawn\n')
                    break
            except Exception as e:
                print('Something went wrrong', e)

    def emptyLayout(self, emptyValue='_'):
        for row in range(3):
            for col in range(1, 4):
                pos = (3 * row) + col
                self.position[pos] = emptyValue

    def newMove(self, newPosition):
        layout = Layout(self)

        # Player one's move
        layout.position[newPosition] = self.playerOne

        # After every new move the layout should be swapped
        (layout.playerOne, layout.playerTwo) = (layout.playerTwo, layout.playerOne)
        return layout

    # Terminal case: if the match is drawn
    def isMatchDrawn(self):
        for pos in range(1, len(self.position) + 1):
            if self.position[pos] == self.blank:
                return False
        return True

    # In the terminology of game, states are nothing but moves
    # In the terminology of MCTS these are states.
    def createStates(self):
        acts = []
        # lay = layout
        for pos in range(len(self.position)):
            if self.position[pos + 1] == self.blank:
                # index starts from 0. So, adding 1 to it
                # lay = lay.newMove(pos + 1)
                acts.append(self.newMove(pos + 1))
        return acts

    def isWin(self):
        # The win can be derived in cases:
        # If any of the rows are marked with same sign,
        # If any of the column is marked by the same sign or
        # if any of the diagonal is marked with same sign.

        # Horizontal watch
        count = 0
        for row in range(3):
            for col in range(1, 4):
                pos = (3 * row) + col
                if self.position[pos] == self.playerTwo:
                    count += 1
            if count == 3:
                return True
            else:
                count = 0
        # Vertical watch
        count = 0
        for col in range(1, 4):
            for row in range(3):
                pos = (3 * row) + col
                if self.position[pos] == self.playerTwo:
                    count += 1
            if count == 3:
                return True
            else:
                count = 0

        count = 0
        for pos in range(1, 4):
            row = pos - 1
            col = pos
            position = (3 * row) + col
            if self.position[position] == self.playerTwo:
                count += 1

        if count == 3:
            return True

        count = 0
        row = 0
        col = 3
        while row < 3:
            position = (3 * row) + col
            if self.position[position] == self.playerTwo:
                count += 1
            row += 1
            col -= 1
        if count == 3:
            return True

        return False

    def __str__(self):
        output = ''
        for position in range(1, len(self.position) + 1):
            output += ' %s' % self.position[position]
            if position % 3 == 0:
                output += '\n'

        if self.playerOne == 'X':
            output = '\n--------------\n "X" to move:\n--------------\n\n' + output
        elif self.playerOne == 'O':
            output = '\n--------------\n "O" to move:\n--------------\n\n' + output

        return output


class TreeNode():
    def __init__(self, layout: Layout, parent):
        self.layout = layout
        self.isTerminal = True if self.layout.isWin() or self.layout.isMatchDrawn() else False
        self.isExpanded = self.isTerminal
        self.parent = parent
        self.countOfVisits = 0
        self.score = 0
        self.children = {}


class Solver():
    PLAYER_X = 'X'
    PLAYER_O = 'O'

    def find(self, currentState):
        self.root = TreeNode(currentState, None)
        for iteration in range(1000):
            treeNode: TreeNode = self.select(self.root)
            score = self.simulation(treeNode.layout)
            print(str(score) + '\n')
            self.reversePropagation(treeNode, score)

        try:
            return self.optimalMove(self.root, 0)
        except:
            pass

    def select(self, treeNode: TreeNode):
        while not treeNode.isTerminal:
            if treeNode.isExpanded:
                treeNode = self.optimalMove(treeNode, 2)
            else:
                return self.expand(treeNode)
        return treeNode

    def expand(self, treeNode: TreeNode):
        states = treeNode.layout.createStates()
        output: TreeNode
        for state in states:
            if str(state.position) not in treeNode.children:
                output = TreeNode(state, treeNode)
                treeNode.children[str(state.position)] = output
                if len(states) == len(treeNode.children):
                    treeNode.isExpanded = True
                return output
        return output

    def simulation(self, layout: Layout):
        while not layout.isWin():
            try:
                layout = random.choice(layout.createStates())
            except:
                return 0
        return 1 if layout.playerTwo == Solver.PLAYER_X else -1

    def reversePropagation(self, treeNode: TreeNode, score):
        while treeNode is not None:
            treeNode.countOfVisits += 1
            treeNode.score += score
            treeNode = treeNode.parent

    def optimalMove(self, treeNode: TreeNode, ec):
        optimalScore = float("-inf")
        optimalMoves = []
        output: TreeNode
        if len(treeNode.children) > 0:
            for child in treeNode.children.values():
                player = 1 if child.layout.playerTwo == Solver.PLAYER_X else -1
                actionScore = player * child.score / child.countOfVisits + ec * math.sqrt(
                    math.log(treeNode.countOfVisits / child.countOfVisits))
                if actionScore > optimalScore:
                    optimalScore = actionScore
                    optimalMoves = [child]
                elif actionScore == optimalScore:
                    optimalMoves.append(child)
            output = random.choice(optimalMoves)
            print(str(actionScore) + "\n")
            return output
        return output


if __name__ == '__main__':
    layout = Layout()
    layout.position = {1: '_', 2: 'O', 3: '_', 4: 'X', 5: 'X', 6: 'O', 7: '_', 8: '_', 9: '_'}
    print(layout)
    layout.start()
