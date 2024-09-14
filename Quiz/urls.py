from django.urls import path
from . import views
# create urls here..
urlpatterns = [
    path('', views.index, name='home'),
    path('create_quiz/', views.createQuiz, name='createQuiz'),
    path('quiz/<slug>', views.quizDetails, name="quizDetails"),
    path('quiz/participant/<slug>', views.quizParticipant, name="quizParticipant"),
    path('quiz/<slug>/<id>', views.deleteQuestion, name="quizQuesDelete"),
    path('view/quiz/<slug>', views.overview, name="overview"),
    path('exam/<slug>', views.quiz_participation, name="exam"),
    path('quiz_result/<slug>', views.quiz_result, name="quiz_result"),

]
