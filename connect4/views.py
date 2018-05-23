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
    start = State(blank_board, 0)

    start_state = State(blank_board, 0)
    x = copy.deepcopy(start_state.board)
    x[2][3] = 4
    following_state = State(x, 1)
    one = start_state.board
    two = following_state.board
    following_state.add_action(4)
    following_state.add_transition(4)
    following_state.add_next_state(start_state)
    what_are_the_next_states = following_state.next_states
    next_trans = following_state.transitions
    next_acts = following_state.actions
    somethingelse = following_state.reward = 5
    the_reward = following_state.reward

    one_last_breakpoint = "many more to come"

    all_states = ct.defaultdict()
    all_states[repr(blank_board)] = start_state
    state_id = 0
    with open(path) as f:
        test_list: List[Any] = list(csv.reader(f))
        for x in test_list:
            current_state = start_state
            starting_player = x[0]
            winning_player = x[1]
            won = starting_player == winning_player

            i = 3
            for item in x[2::2]:
                state_id = state_id + 1
                if not item:
                    break
                elif not x[i]:
                    board = copy.deepcopy(current_state.board)
                    player_x = int(item.split(',')[0])
                    player_y = int(item.split(',')[1])
                    board[player_x][player_y] = 1

                    if repr(board) in all_states:
                        new_state = all_states[repr(board)]
                        # Check to see if it's already been linked from current_state
                        if current_state.next_states.__contains__(new_state):
                            # We need to modify the transition accordingly
                            ind = current_state.next_states.index(new_state)
                            current_state.transitions[ind] = current_state.transitions[ind] + 1
                            breakItDownHere = "Wow, that state exists and has already been linked"
                        else:
                            current_state.add_next_state(new_state)
                            current_state.add_action(player_y)
                            current_state.add_transition(1)
                    else:
                        new_state = State(board, state_id)
                        new_state.reward = 1
                        current_state.add_next_state(new_state)
                        current_state.add_action(player_y)
                        current_state.add_transition(1)
                        all_states[repr(new_state.board)] = new_state
                else:
                    board = copy.deepcopy(current_state.board)
                    player_x = int(item.split(',')[0])
                    player_y = int(item.split(',')[1])
                    board[player_x][player_y] = 1
                    opponent_x = int(x[i].split(',')[0])
                    opponent_y = int(x[i].split(',')[1])
                    board[opponent_x][opponent_y] = 2

                    # If this board state already exists in our model, find it and make new_state it!
                    # Point our current_state to it, modify current_state's transition + action accordingly.
                    # Make our current_state this existing state (assigned to new_state) and continue.
                    if repr(board) in all_states:
                        new_state = all_states[repr(board)]
                        # Check to see if it's already been linked from current_state
                        if current_state.next_states.__contains__(new_state):
                            # We need to modify the transition accordingly
                            ind = current_state.next_states.index(new_state)
                            current_state.transitions[ind] = current_state.transitions[ind] + 1
                            breakItDownHere = "Wow, that state exists and has already been linked"
                        else:
                            current_state.add_next_state(new_state)
                            current_state.add_action(player_y)
                            current_state.add_transition(1)
                    else:
                        new_state = State(board, state_id)
                        current_state.add_next_state(new_state)
                        current_state.add_action(player_y)
                        current_state.add_transition(1)
                        all_states[repr(new_state.board)] = new_state

                i = i + 2
                current_state = new_state
                breakPoint = "here"

            doneWithThefor = "wow"

    context = {'latest_question_list': latest_question_list,
               'test_list': test_list}
    return render(request, 'connect4/index.html', context)


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

    # TODOs:
    # - Make it so it logs every other turn
    # - Setup State object correctly
    # - Populate state props correctly
    # - State for "win", "lose", and "tie"
    # - Work on back propagating...
    # -

    # State Specs:
    # - ID
    # - State: In this case it's the 2d array representing the board
    # - Array that's an Actions tuple (Action Id, State, Probability)
    # - Calculate each action as -1, back propagate from goal state
    # - State Array - an array of all states that link from this
    # - Probability - an array of the probability corresponding to a state


class State:
    def __init__(self, board, num):
        self._board = board
        self._id = num
        self._next_states = []
        self._actions = []
        self._transitions = []
        self._reward = 0

        # def set_id(self, num):
        # self.id = num

    # def set_reward(self, num):
    #   self.reward = num

    def add_transition(self, num):
        self._transitions.append(num)

    def add_next_state(self, state):
        self._next_states.append(state)

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
