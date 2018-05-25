import copy
from typing import List, Any
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
import csv
import os.path
import collections as ct
from .models import Question, Choice


def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]

    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "../data/datasetone.csv")

    blank_board = [[0 for x in range(7)] for y in range(6)]
    start_state = State(blank_board, 0)

    # Make a dictionary, create the first entry to be the blank (starting) board state.
    # Keys are string representations of the 2D array representing the board, since you can't have a 2D arr as a key
    all_states = ct.defaultdict()
    all_states[repr(blank_board)] = start_state
    state_id = 0
    with open(path) as f:
        data_rows: List[Any] = list(csv.reader(f))
        for x in data_rows:
            current_state = start_state
            starting_player = x[0]
            winning_player = x[1]
            if '' in x:
                moves_this_game = (x.index('') - 2) // 2  # Remove 2 for the first 2 columns (who started, who won), and -1 for arr
            else:
                moves_this_game = 42  # Max amount of moves in a 6x7 game of Connect-4

            if winning_player == 3:
                won = 0  # Tie game
            elif winning_player == starting_player:
                won = 100  # Starting player won
            else:
                won = -100  # Starting player lost

            i = 3  # Start i at 3 since the first two columns are who started and won. The third column is x from below.
            for item in x[2::2]:
                state_id = state_id + 1
                if not item:  # Games have a variable number of turns, with at most 42, so there will be blank values.
                    break
                else:
                    board = copy.deepcopy(current_state.board)
                    add_piece_to_board(board, item, 1)
                    action = int(item.split(',')[1])
                    reward = won - moves_this_game
                    if x[i]:
                        add_piece_to_board(board, x[i], 2)
                    current_state = existing_board_state(board, current_state, all_states, action, state_id, reward)
                i = i + 2  # Increment by 2 since x is the players move and i is getting the following (opp) move
                moves_this_game = moves_this_game - 1
            # END: for item in x[2::2]:
        # END: for x in test_list:

    context = {'latest_question_list': latest_question_list,
               'test_list': data_rows}
    return render(request, 'connect4/index.html', context)


def add_piece_to_board(board, coords, piece):
    player_x = int(coords.split(',')[0])
    player_y = int(coords.split(',')[1])
    board[player_x][player_y] = piece


# If this board state already exists in our model, find it and make new_state it.
# Point our current_state to it, modify current_state's transition + action accordingly.
# Make our current_state this existing state (assigned to new_state) and continue.
def existing_board_state(board, current_state, all_states, action, state_id, reward):
    if repr(board) in all_states:
        new_state = all_states[repr(board)]
        # Check to see if it's already been linked from current_state
        if current_state.next_states.__contains__(new_state):
            # We need to modify the transition accordingly
            ind = current_state.next_states.index(new_state)
            current_state.transitions[ind] = current_state.transitions[ind] + 1
            # Since this action is already linked to the new_state, see if this reward is bigger and overwrite
            if current_state.rewards[ind] < reward:
                current_state.rewards[ind] = reward
        else:
            current_state.add_next_state(new_state)
            current_state.add_action(action)
            current_state.add_reward(reward)
            current_state.add_transition(1)
    else:
        new_state = State(board, state_id)
        #  new_state.reward = 1
        current_state.add_next_state(new_state)
        current_state.add_action(action)
        current_state.add_reward(reward)
        current_state.add_transition(1)
        # TODO: Set the current_states value to be the max reward from rewards
        all_states[repr(new_state.board)] = new_state

    return new_state


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'connect4/detail.html', {'question': question})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'connect4/results.html', {'question': question})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'connect4/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('connect4:results', args=(question.id,)))


class State:
    def __init__(self, board, num):
        self._board = board
        self._id = num
        self._next_states = []
        self._actions = []
        self._transitions = []
        self._rewards = []
        self._reward = 0

    def add_transition(self, num):
        self._transitions.append(num)

    def add_next_state(self, state):
        self._next_states.append(state)

    def add_reward(self, reward):
        self._rewards.append(reward)

    # At most times there's always ONLY 7 moves (column 0 - 6)
    def add_action(self, num):
        self._actions.append(num)

    @property
    def actions(self):
        return self._actions

    @property
    def next_states(self):
        return self._next_states

    @property
    def transitions(self):
        return self._transitions

    @property
    def rewards(self):
        return self._rewards

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def reward(self):
        return self._reward

    @reward.setter
    def reward(self, value):
        self._reward = value

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, value):
        self._board = value
