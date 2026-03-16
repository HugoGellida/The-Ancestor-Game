#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <optional>
#include <stack>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

template <class State, class Action> struct GameState {
    virtual ~GameState() = default;
    virtual float getScore() const = 0;
    virtual State getNextState(const Action &action, int player) const = 0;
    virtual bool isFinal() const = 0;
    virtual vector<Action> getAllActions() const = 0;
    virtual bool isPlayable(const Action &action) const = 0;

    vector<Action> getActions() const {
        vector<Action> possibles;

        for (Action action : this->getAllActions()) {
            if (this->isPlayable(action)) {
                possibles.push_back(action);
            }
        }

        return possibles;
    }
};

enum AncAct {
    Flag,
    Capture,
    Parent,
};

template <size_t N> struct AncestorAction {
    static const vector<AncestorAction> allActions;

    int player;
    AncAct action;
    size_t node1;
    size_t node2;

    AncestorAction() {}
    AncestorAction(int player, AncAct action, size_t node1)
        : player(player), action(action), node1(node1) {}
    AncestorAction(int player, AncAct action, size_t node1, size_t node2)
        : player(player), action(action), node1(node1), node2(node2) {}
};

template <size_t N>
const std::vector<AncestorAction<N>> AncestorAction<N>::allActions = []() {
    std::vector<AncestorAction<N>> actions;

    for (size_t i = 0; i < N; ++i) {
        actions.push_back(AncestorAction<N>(1, AncAct::Flag, i));
    }

    for (size_t i = 0; i < N; ++i) {
        for (size_t j = 0; j < N; ++j) {
            if (i != j) {
                actions.push_back(AncestorAction<N>(1, AncAct::Parent, i, j));
            }
        }
    }

    for (size_t i = 0; i < N; ++i) {
        for (size_t j = i; j < N; ++j) {
            actions.push_back(AncestorAction<N>(1, AncAct::Capture, i, j));
        }
    }

    for (size_t i = 0; i < N; ++i) {
        actions.push_back(AncestorAction<N>(-1, AncAct::Flag, i));
    }

    for (size_t i = 0; i < N; ++i) {
        for (size_t j = 0; j < N; ++j) {
            if (i != j) {
                actions.push_back(AncestorAction<N>(-1, AncAct::Parent, i, j));
            }
        }
    }

    for (size_t i = 0; i < N; ++i) {
        for (size_t j = i; j < N; ++j) {
            actions.push_back(AncestorAction<N>(-1, AncAct::Capture, i, j));
        }
    }

    return actions;
}();

template <size_t N> struct AncestorState;

template <size_t N>
struct AncestorState : public GameState<AncestorState<N>, AncestorAction<N>> {
    int whichPlayer;

    std::array<bool, N> flagged_p1;
    std::array<bool, N> flagged_p2;

    std::array<bool, N> captured_p1;
    std::array<bool, N> captured_p2;

    std::array<std::optional<size_t>, N> parents;

    AncestorState()
        : whichPlayer(1), flagged_p1{}, flagged_p2{}, captured_p1{},
          captured_p2{}, parents{} {}

    std::vector<size_t> getAncestors(size_t node) const {
        size_t current = node;

        std::vector<size_t> ancestors;
        ancestors.push_back(current);

        while (this->parents[current].has_value()) {
            current = this->parents[current].value();
            ancestors.push_back(current);
        }

        return ancestors;
    }

    bool hasFlag(int player, size_t node) const {
        return (player == 1 && this->flagged_p1[node]) ||
               (player == -1 && this->flagged_p2[node]);
    }

    bool isCaptured(size_t node) const {
        return this->captured_p1[node] || this->captured_p2[node];
    }

    size_t getNbCapturedNodes(int player) const {
        size_t score = 0;

        if (player == 1) {
            for (bool captured : this->captured_p1) {
                if (captured) {
                    score++;
                }
            }
        } else {
            for (bool captured : this->captured_p2) {
                if (captured) {
                    score++;
                }
            }
        }

        return score;
    }

    float getScore() const override {
        return this->getNbCapturedNodes(1) - this->getNbCapturedNodes(-1);
    }

    AncestorState<N> getNextState(const AncestorAction<N> &action,
                                  int player) const override {
        AncestorState<N> next(*this);
        next.whichPlayer = -player;

        switch (action.action) {
        case AncAct::Flag:
            if (player == 1) {
                next.flagged_p1[action.node1] = true;
            } else {
                next.flagged_p2[action.node1] = true;
            }
            break;
        case AncAct::Capture: {
            std::vector<size_t> ancestors1 = next.getAncestors(action.node1);
            std::vector<size_t> ancestors2 = next.getAncestors(action.node2);

            std::unordered_set<size_t> ancestors1_set(ancestors1.begin(),
                                                      ancestors1.end());

            size_t lca = *std::find_if(
                ancestors2.begin(), ancestors2.end(),
                [&](size_t node) { return ancestors1_set.count(node) > 0; });

            size_t current = action.node1;
            while (current != lca) {
                if (player == 1 && !isCaptured(current)) {
                    next.captured_p1[current] = true;
                    next.flagged_p1[current] = false;
                    next.flagged_p2[current] = false;
                } else if (player == -1 && !isCaptured(current)) {
                    next.captured_p2[current] = true;
                    next.flagged_p1[current] = false;
                    next.flagged_p2[current] = false;
                }
                current = next.parents[current].value();
            }

            current = action.node2;
            while (current != lca) {
                if (player == 1 && !isCaptured(current)) {
                    next.captured_p1[current] = true;
                    next.flagged_p1[current] = false;
                    next.flagged_p2[current] = false;
                } else if (player == -1 && !isCaptured(current)) {
                    next.captured_p2[current] = true;
                    next.flagged_p1[current] = false;
                    next.flagged_p2[current] = false;
                }
                current = next.parents[current].value();
            }

            if (player == 1 && !isCaptured(lca)) {
                next.captured_p1[lca] = true;
                next.flagged_p1[lca] = false;
                next.flagged_p2[lca] = false;
            } else if (player == -1 && !isCaptured(lca)) {
                next.captured_p2[lca] = true;
                next.flagged_p1[lca] = false;
                next.flagged_p2[lca] = false;
            }
            break;
        }
        case AncAct::Parent:
            next.parents[action.node1] = action.node2;
            break;
        }

        return next;
    }

    bool isFinal() const override {
        return this->getNbCapturedNodes(1) >= (N / 2.) ||
               this->getNbCapturedNodes(-1) >= (N / 2.);
    }

    vector<AncestorAction<N>> getAllActions() const override {
        return AncestorAction<N>::allActions;
    }

    bool isPlayable(const AncestorAction<N> &action) const override {
        if (this->whichPlayer != action.player) {
            return false;
        }

        switch (action.action) {
        case AncAct::Flag:
            return !isCaptured(action.node1) &&
                   !this->hasFlag(action.player, action.node1);
        case AncAct::Capture: {

            std::vector<size_t> ancestors1 = this->getAncestors(action.node1);
            std::vector<size_t> ancestors2 = this->getAncestors(action.node2);
            return this->hasFlag(action.player, action.node1) &&
                   this->hasFlag(action.player, action.node2) &&
                   ancestors1[ancestors1.size() - 1] ==
                       ancestors2[ancestors2.size() - 1];
        }
        case AncAct::Parent: {
            std::vector<size_t> ancestors = this->getAncestors(action.node2);
            return !this->parents[action.node1].has_value() &&
                   std::find(ancestors.begin(), ancestors.end(),
                             action.node1) == ancestors.end();
        }
        }

        return false;
    }

    string toString() const {
        string total = "";

        total += "Player 1 flags: ";
        for (size_t i = 0; i < N; i++) {
            if (this->flagged_p1[i]) {
                total += std::to_string(i) + ", ";
            }
        }
        total += "\n";

        total += "Player 2 flags: ";
        for (size_t i = 0; i < N; i++) {
            if (this->flagged_p2[i]) {
                total += std::to_string(i) + ", ";
            }
        }
        total += "\n";

        total += "Player 1 captured: ";
        for (size_t i = 0; i < N; i++) {
            if (this->captured_p1[i]) {
                total += std::to_string(i) + ", ";
            }
        }
        total += "\n";

        total += "Player 2 captured: ";
        for (size_t i = 0; i < N; i++) {
            if (this->captured_p2[i]) {
                total += std::to_string(i) + ", ";
            }
        }
        total += "\n";

        total += "Parents: ";
        for (size_t i = 0; i < N; i++) {
            total += std::to_string(i) + "->";
            if (this->parents[i].has_value()) {
                total += std::to_string(this->parents[i].value());
            } else {
                total += "None";
            }
            total += ", ";
        }
        total += "\n";

        return total;
    }
};

template <class State, class Action>
Action minMaxDFS(int player, const State &state, int maxDepth) {
    struct StackFrame {
        State state;
        int player;
        int depth;
        size_t actionIndex;
        std::vector<Action> actions;
        float bestValue;
        Action bestAction;

        StackFrame(const State &s, int p, int d)
            : state(s), player(p), depth(d), actionIndex(0),
              bestValue(p == 1 ? -std::numeric_limits<float>::infinity()
                               : std::numeric_limits<float>::infinity()) {

            actions = state.getActions();
            if (!actions.empty()) {
                bestAction = actions[0];
            }
        }

        void setIfBetterValue(size_t actionIndex, float score) {
            if ((this->player == 1 && score > this->bestValue) ||
                (this->player == -1 && score < this->bestValue)) {
                this->bestValue = score;
                this->bestAction = this->actions[actionIndex];
            }
        }
    };

    std::stack<StackFrame> pile;
    pile.push(StackFrame(state, player, 0));
    Action rootBestAction = state.getActions()[0];

    while (!pile.empty()) {
        StackFrame &frame = pile.top();

        if (frame.actionIndex >= frame.actions.size()) {
            float resultValue = frame.bestValue;
            Action resultAction = frame.bestAction;
            pile.pop();

            if (!pile.empty()) {
                StackFrame &parent = pile.top();
                parent.setIfBetterValue(parent.actionIndex - 1, resultValue);
            } else {
                rootBestAction = resultAction;
            }
        } else {
            Action currentAction = frame.actions[frame.actionIndex];
            State nextState =
                frame.state.getNextState(currentAction, frame.player);

            if (nextState.isFinal() || frame.depth >= maxDepth - 1) {
                float score = nextState.getScore();
                frame.setIfBetterValue(frame.actionIndex, score);
                frame.actionIndex++;
            } else {
                frame.actionIndex++;
                pile.push(
                    StackFrame(nextState, -frame.player, frame.depth + 1));
            }
        }
    }

    return rootBestAction;
}

template <size_t N> void doAncestor() {
    AncestorState<N> node;
    int player = 1;

    cout << node.toString() << endl;

    while (!node.isFinal()) {
        AncestorAction<N> action =
            minMaxDFS<AncestorState<N>, AncestorAction<N>>(player, node, 3);
        node = node.getNextState(action, player);
        cout << node.toString() << endl;
        player *= -1;
    }
}

int main(int argc, char **argv) {
    doAncestor<10>();
    return 0;
}