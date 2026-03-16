from typing import List, Optional
import math


class GameState:
    def getScore(self) -> float:
        raise NotImplementedError

    def getNextState(self, action, player):
        raise NotImplementedError

    def isFinal(self) -> bool:
        raise NotImplementedError

    def getAllActions(self):
        raise NotImplementedError

    def isPlayable(self, action) -> bool:
        raise NotImplementedError

    def getActions(self):
        possibles = []
        if not self.isFinal():
            for action in self.getAllActions():
                if self.isPlayable(action):
                    possibles.append(action)
        return possibles


class AncAct:
    Flag = "Flag"
    Capture = "Capture"
    Parent = "Parent"


class AncestorAction:
    allActions = []

    def __init__(self, player, action, node1, node2=None):
        self.player = player
        self.action = action
        self.node1 = node1
        self.node2 = node2


def generate_all_actions(N):
    actions = []

    for i in range(N):
        actions.append(AncestorAction(1, AncAct.Flag, i))

    for i in range(N):
        for j in range(N):
            if i != j:
                actions.append(AncestorAction(1, AncAct.Parent, i, j))

    for i in range(N):
        for j in range(i, N):
            actions.append(AncestorAction(1, AncAct.Capture, i, j))

    for i in range(N):
        actions.append(AncestorAction(-1, AncAct.Flag, i))

    for i in range(N):
        for j in range(N):
            if i != j:
                actions.append(AncestorAction(-1, AncAct.Parent, i, j))

    for i in range(N):
        for j in range(i, N):
            actions.append(AncestorAction(-1, AncAct.Capture, i, j))

    return actions


class AncestorState(GameState):

    def __init__(self, N):
        self.N = N
        self.whichPlayer = 1

        self.flagged_p1 = [False] * N
        self.flagged_p2 = [False] * N
        self.captured_p1 = [False] * N
        self.captured_p2 = [False] * N

        self.parents: List[Optional[int]] = [None] * N

        if not AncestorAction.allActions:
            AncestorAction.allActions = generate_all_actions(N)

    def copy(self):
        new = AncestorState(self.N)

        new.whichPlayer = self.whichPlayer
        new.flagged_p1 = self.flagged_p1[:]
        new.flagged_p2 = self.flagged_p2[:]
        new.captured_p1 = self.captured_p1[:]
        new.captured_p2 = self.captured_p2[:]
        new.parents = self.parents[:]

        return new

    def getAncestors(self, node):
        current = node
        ancestors = [current]

        while self.parents[current] is not None:
            current = self.parents[current]
            ancestors.append(current)

        return ancestors

    def hasFlag(self, player, node):
        return (player == 1 and self.flagged_p1[node]) or (
            player == -1 and self.flagged_p2[node]
        )

    def isCaptured(self, node):
        return self.captured_p1[node] or self.captured_p2[node]

    def getNbCapturedNodes(self, player):
        arr = self.captured_p1 if player == 1 else self.captured_p2
        return sum(arr)

    def getScore(self):

        CAPTURE_WEIGHT = 1.0
        FLAG_WEIGHT = 0.3
        WIN_SCORE = 1000.0

        p1Captures = self.getNbCapturedNodes(1)
        p2Captures = self.getNbCapturedNodes(-1)

        if p1Captures >= self.N / 2:
            return WIN_SCORE * self.N
        if p2Captures >= self.N / 2:
            return -WIN_SCORE * self.N

        p1Flags = 0
        p2Flags = 0

        for i in range(self.N):
            if not self.isCaptured(i):
                if self.flagged_p1[i]:
                    p1Flags += 1
                if self.flagged_p2[i]:
                    p2Flags += 1

        return CAPTURE_WEIGHT * (p1Captures - p2Captures) + FLAG_WEIGHT * (
            p1Flags - p2Flags
        )

    def getNextState(self, action, player):

        next_state = self.copy()
        next_state.whichPlayer = -player

        if action.action == AncAct.Flag:

            if player == 1:
                next_state.flagged_p1[action.node1] = True
            else:
                next_state.flagged_p2[action.node1] = True

        elif action.action == AncAct.Parent:

            next_state.parents[action.node1] = action.node2

        elif action.action == AncAct.Capture:

            ancestors1 = next_state.getAncestors(action.node1)
            ancestors2 = next_state.getAncestors(action.node2)

            set1 = set(ancestors1)

            lca = next(node for node in ancestors2 if node in set1)

            def capturePath(start):
                current = start

                while current != lca:

                    if not self.isCaptured(current):

                        if player == 1:
                            next_state.captured_p1[current] = True
                        else:
                            next_state.captured_p2[current] = True

                        next_state.flagged_p1[current] = False
                        next_state.flagged_p2[current] = False

                    current = next_state.parents[current]

            capturePath(action.node1)
            capturePath(action.node2)

            if not self.isCaptured(lca):

                if player == 1:
                    next_state.captured_p1[lca] = True
                else:
                    next_state.captured_p2[lca] = True

                next_state.flagged_p1[lca] = False
                next_state.flagged_p2[lca] = False

        return next_state

    def isFinal(self):

        return (
            self.getNbCapturedNodes(1) >= self.N / 2
            or self.getNbCapturedNodes(-1) >= self.N / 2
        )

    def getAllActions(self):

        return AncestorAction.allActions

    def isPlayable(self, action):

        if self.whichPlayer != action.player:
            return False

        if action.action == AncAct.Flag:

            return (
                not self.isCaptured(action.node1)
                and not self.hasFlag(action.player, action.node1)
            )

        if action.action == AncAct.Capture:

            ancestors1 = self.getAncestors(action.node1)
            ancestors2 = self.getAncestors(action.node2)

            return (
                self.hasFlag(action.player, action.node1)
                and self.hasFlag(action.player, action.node2)
                and ancestors1[-1] == ancestors2[-1]
            )

        if action.action == AncAct.Parent:

            ancestors = self.getAncestors(action.node2)

            return (
                self.parents[action.node1] is None
                and action.node1 not in ancestors
            )

        return False

    def toString(self):

        total = ""

        total += "Player 1 flags: "
        total += ", ".join(str(i) for i in range(self.N) if self.flagged_p1[i])
        total += "\n"

        total += "Player 2 flags: "
        total += ", ".join(str(i) for i in range(self.N) if self.flagged_p2[i])
        total += "\n"

        total += "Player 1 captured: "
        total += ", ".join(str(i) for i in range(self.N) if self.captured_p1[i])
        total += "\n"

        total += "Player 2 captured: "
        total += ", ".join(str(i) for i in range(self.N) if self.captured_p2[i])
        total += "\n"

        total += "Parents: "

        for i in range(self.N):
            parent = self.parents[i]
            total += f"{i}->{parent if parent is not None else 'None'}, "

        total += "\n"

        return total


def minMaxDFS(state, maxDepth):

    class StackFrame:

        def __init__(self, state, depth):
            self.state = state
            self.player = state.whichPlayer
            self.depth = depth

            self.actions = state.getActions()
            self.actionIndex = 0

            if self.player == 1:
                self.bestValue = -math.inf
            else:
                self.bestValue = math.inf

            self.bestAction = self.actions[0] if self.actions else None

            if not self.actions:
                self.bestValue = state.getScore()

        def setIfBetterValue(self, idx, score):

            if (
                self.player == 1
                and score > self.bestValue
                or self.player == -1
                and score < self.bestValue
            ):
                self.bestValue = score
                self.bestAction = self.actions[idx]

    stack = [StackFrame(state, 0)]

    rootActions = state.getActions()
    rootBestAction = rootActions[0] if rootActions else None

    while stack:

        frame = stack[-1]

        if frame.actionIndex >= len(frame.actions):

            resultValue = frame.bestValue
            resultAction = frame.bestAction

            stack.pop()

            if stack:

                parent = stack[-1]
                parent.setIfBetterValue(parent.actionIndex - 1, resultValue)

            else:

                rootBestAction = resultAction

        else:

            action = frame.actions[frame.actionIndex]
            nextState = frame.state.getNextState(action, frame.player)

            if nextState.isFinal() or frame.depth >= maxDepth - 1:

                score = nextState.getScore()
                frame.setIfBetterValue(frame.actionIndex, score)
                frame.actionIndex += 1

            else:

                frame.actionIndex += 1
                stack.append(StackFrame(nextState, frame.depth + 1))

    return rootBestAction


def doAncestor(N):

    node = AncestorState(N)

    print(node.toString())

    while not node.isFinal():

        action = minMaxDFS(node, 5)
        node = node.getNextState(action, node.whichPlayer)

        print(node.toString())


if __name__ == "__main__":

    doAncestor(2)