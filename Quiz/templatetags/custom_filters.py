from django import template
from Quiz.models import Result

register = template.Library()


def mul(value, arg):
    return value*arg


def convert(seconds, arg):
    seconds *= arg
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%dh:%02dm:%02ds" % (hour, minutes, seconds)


def get_by_question(user_answers, question, user_choice):
    try:
        return Result.objects.get(question=question, user_choice=user_choice)
    except Result.DoesNotExist:
        return None


register.filter('mul', mul)
register.filter('toTime', convert)
register.filter('get_by_question', get_by_question)
