import copy
from typing import List, Any
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
import csv
import os.path
from .models import Question, Choice, State


def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]

    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "../data/datasetone.csv")

    blank_board = [[0 for x in range(7)] for y in range(6)]
    start = State(blank_board)

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

    all_states = []
    with open(path) as f:
        test_list: List[Any] = list(csv.reader(f))
        for x in test_list:
            current_state = copy.deepcopy(start);
            starting_player = x[0]
            winning_player = x[1]
            #Here you can easily grab condition for win/lose/tie
            # gross way, but for now...
            i = 3
            for item in x[2:]:
                if i % 2 == 1: #need an "else if last index.."
                    board = current_state.get_state()
                    try:
                        player_x = int(item.split(',')[0])
                        player_y = int(item.split(',')[1])
                        board[player_x][player_y] = 1
                        opponent_x = int(x[i].split(',')[0])
                        opponent_y = int(x[i].split(',')[1])
                        board[opponent_x][opponent_y] = 2
                        s = State(board)
                        current_state = s
                        all_states.append(s)
                    except ValueError as verr:
                        break
                    except IndexError as ie:
                        #Starting player wins
                        player_x = int(item.split(',')[0])
                        player_y = int(item.split(',')[1])
                        board[player_x][player_y] = 1
                        s = State(board)
                        current_state = s
                        all_states.append(s)

                i = i + 1
                breakPoint = "here"

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
