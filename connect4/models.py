import copy

from django.core.validators import validate_comma_separated_integer_list
from django.db import models
import datetime
from django.utils import timezone


# Create your models here.

class Statex(models.Model):
    board = models.TextField(max_length = 100)
    actions = models.CharField(validators=[validate_comma_separated_integer_list], max_length=30, blank=True, null=True)

    def get_state(self):
        return copy.deepcopy(self.board)

    def add_piece(self):
        self.board

    def __init__(self, board):
        self.board = board

    def __str__(self):
        return self.board


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING, )
    choice_test = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_test
