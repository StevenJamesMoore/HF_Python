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
    current_state = start

    all_states = []
    with open(path) as f:
        test_list: List[Any] = list(csv.reader(f))
        for x in test_list:
            starting_player = x[0]
            winning_player = x[1]
            for item in x[2:]:
                board = current_state.get_state()
                #item is '5,4'
                board[int(item.split(',')[0])][int(item.split(',')[1])] = 2
                s = State(board)
                current_state = s
                all_states.append(s)
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
