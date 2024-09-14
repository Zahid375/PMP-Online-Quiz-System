from django.http import JsonResponse
from django.utils import timezone
import uuid
from django.shortcuts import render, HttpResponseRedirect, redirect, get_object_or_404
from django.urls import reverse
from .models import *
from .forms import *
from django.db import transaction, IntegrityError
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.contrib import messages
from django.core.paginator import Paginator
from .utils import send_custom_email
# Create your views here.


@login_required
def index(request):
    user = Result.objects.filter(user=request.user)
    result_quiz = user.values('quiz__id')
    quiz = Quiz.objects.all().exclude(id__in=result_quiz)
    return render(request, 'index.html', context={'quiz': quiz})


@login_required
def createQuiz(request):
    if request.POST:
        name = request.POST.get('quiz_name')
        description = request.POST.get('quiz_description')
        quiz = Quiz.objects.create(name=name, description=description)
        title = quiz.name
        quiz.slug = title.replace(' ', '-') + '-' + str(uuid.uuid1())
        quiz.save()
        return HttpResponseRedirect(reverse('quizDetails', kwargs={'slug': quiz.slug}))
    return render(request, 'quiz.html')


@login_required
def quizDetails(request, slug):
    quiz = Quiz.objects.get(slug=slug)
    all_question = Question.objects.filter(quiz=quiz.id)
    ChoiceFormSet = modelformset_factory(Choice, form=ChoiceForm)
    question_form = QuestionForm(request.POST or None)
    formset = ChoiceFormSet(request.POST or None, request.FILES or None,
                            queryset=Choice.objects.none(), prefix='marks')
    if request.method == 'POST':
        # QUESION FORM SAVE
        if question_form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    question = question_form.save(commit=False)
                    question.quiz = quiz
                    question.save()
                    for choice in formset:
                        data = choice.save(commit=False,)
                        data.question = question
                        data.save()

            except IntegrityError:
                print("Error Encountered")
            return HttpResponseRedirect(reverse('quizDetails', kwargs={'slug': quiz.slug}))
        else:
            messages.warning(request, "Something Wrong")
    return render(request, 'quiz_details.html', context={'quiz': quiz, 'question': question_form, 'formset': formset, 'allquestion': all_question})

# Delete quiz question


@login_required
def deleteQuestion(request, slug, id):
    quiz = Quiz.objects.get(slug=slug)
    question = Question.objects.filter(quiz=quiz, id=id)
    question.delete()
    messages.success(request, "Question delete succesfully")
    return HttpResponseRedirect(reverse('quizDetails', kwargs={'slug': slug}))


# @login_required
def takeExam(request, slug):
    quiz = Quiz.objects.get(slug=slug)
    all_question = Question.objects.filter(quiz=quiz.id)
    if request.method == 'POST':
        quiz = get_object_or_404(Quiz, slug=slug)
        total_questions = quiz.question.count()
        user_responses = []
        for question in quiz.question.all():
            user_choice_id = request.POST.get(f"question_{question.id}")
            if user_choice_id:
                user_choice = get_object_or_404(Choice, pk=user_choice_id)
                result = Result.objects.filter(
                    quiz=quiz, user=request.user, question=question).exists()
                if result:
                    messages.success(request, "Your Alreay attend exam")
                    return render(request, 'exam.html', context={'quiz': quiz, 'allquestion': all_question})
                else:
                    Result.objects.update_or_create(
                        quiz=quiz, user=request.user, question=question, user_choice=user_choice, defaults=None)

        # Save user responses to the database
        # for response in user_responses:
        #     try:
        #         response.save()
        #     except Exception as e:
        #         print(e)

        return HttpResponseRedirect(reverse('quiz_result', kwargs={'slug': quiz.slug}))

    return render(request, 'exam.html', context={'quiz': quiz, 'allquestion': all_question})


@login_required
def quiz_participation(request, slug):
    quiz = Quiz.objects.get(slug=slug)

    # Check if the user has already attended the quiz
    existing_results = Result.objects.filter(
        quiz=quiz, user=request.user).first()
    if existing_results:
        # You can redirect them to a page that informs them they've already attended
        return render(request, 'already_attended.html', {'quiz': quiz})

    questions = Question.objects.filter(quiz=quiz)

    if request.method == 'POST':
        for question in questions:
            # Get the selected choices (multiple can be selected)
            choice_ids = request.POST.getlist(f'question_{question.id}_choice')
            feedback = request.POST.get(f'question_{question.id}_feedback')
            print(choice_ids)

            for choice_id in choice_ids:
                user_choice = Choice.objects.get(pk=choice_id)
                Result.objects.create(
                    quiz=quiz, user=request.user, question=question, user_choice=user_choice, feedback=feedback)

        return HttpResponseRedirect(reverse('quiz_result', kwargs={'slug': quiz.slug}))

    return render(request, 'participation.html', {'quiz': quiz, 'questions': questions})


# @login_required
# def quiz_result(request, slug):
    # Get the quiz object based on the quiz_id
    quiz = Quiz.objects.get(slug=slug)
    ques = Question.objects.filter(quiz=quiz)

    # Get the user's results for the quiz
    user_results = Result.objects.filter(quiz=quiz, user=request.user)
    correct_answer = user_results.filter(user_choice__is_correct=True)
    answered_question_ids = user_results.values_list('question_id', flat=True)
    unanswered_questions = Question.objects.filter(
        quiz=quiz).exclude(id__in=answered_question_ids)

    score = sum([x['question__points'] for x in correct_answer.values(
        'question__points')])
    total_correct = correct_answer.count()
    total_wrong = user_results.filter(user_choice__is_correct=False).count()

    context = {
        'quiz': quiz,
        'total_correct': total_correct,
        'total_wrong': total_wrong,
        'score': score,
        'unanswered_questions': unanswered_questions,
        'user_results': user_results,
    }
    template_path = 'email_template.html'
    subject = quiz.name
    recipient_list = [request.user.email]
    try:
        send_custom_email(subject, recipient_list, template_path, context)
        messages.success(request, "Your Result Published.Check Your Mail.")
    except Exception as e:
        messages.warning(request, "Sorry ,we can't send mail.")
        print(e)
    return render(request, 'quiz_result.html', context)


@login_required
def quiz_result(request, slug):
    quiz = Quiz.objects.get(slug=slug)
    user = request.user

    # Get the user's results for the quiz
    user_results = Result.objects.filter(quiz=quiz, user=user)
    answered_question_ids = user_results.values_list('question_id', flat=True)
    unanswered_questions = Question.objects.filter(
        quiz=quiz).exclude(id__in=answered_question_ids)

    context = {
        'quiz': quiz,
        'user_results': user_results,
        'unanswered_questions': unanswered_questions,
    }

    # Count the number of correct answers and calculate the score
    total_correct = 0
    score = 0

    for result in user_results:
        correct_answers = result.question.choices.filter(is_correct=True)
        user_choices = [result.user_choice]
        print(correct_answers)
        print(user_choices)
        # Check if the user's choices match the correct answers
        if set(correct_answers) == set(user_choices):
            total_correct += 1
            score += result.question.points

    total_wrong = user_results.count() - total_correct

    context['total_correct'] = total_correct
    context['total_wrong'] = total_wrong
    context['score'] = score

    template_path = 'email_template.html'
    subject = quiz.name
    recipient_list = [request.user.email]
    try:
        send_custom_email(subject, recipient_list, template_path, context)
        messages.success(request, "Your results have been sent to your email.")
    except Exception as e:
        messages.warning(request, "Sorry, we couldn't send the email.")
        print(e)

    return render(request, 'quiz_result.html', context)


@login_required
def overview(request, slug):
    quiz = Quiz.objects.get(slug=slug)
    quiz_point = Question.objects.filter(
        quiz=quiz.id).aggregate(total=Sum('points'))['total']
    return render(request, 'overview.html', context={'quiz': quiz, 'points': quiz_point})


@login_required
def quizParticipant(request, slug):
    quiz = Quiz.objects.get(slug=slug)
    quiz_point = Question.objects.filter(
        quiz=quiz.id).aggregate(total=Sum('points'))['total']
    paricipant = quiz.get_participation_summary()
    print(paricipant)

    return render(request, 'participant.html', context={'user_results': paricipant, 'quiz': quiz, 'points': quiz_point})
