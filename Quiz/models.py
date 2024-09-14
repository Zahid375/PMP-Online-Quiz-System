from django.db import models
from django.db.models import Count, Sum, Case, When, IntegerField, F
# Create your models here.

from Account.models import CustomUser


class Quiz(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=True)
    description = models.TextField(max_length=1000)

    def __str__(self):
        return self.name

    def get_participation_summary(self):
        return Result.objects.filter(quiz=self).values('user__email', 'user__first_name', 'user__last_name', 'user__profile_pic').annotate(
            total_questions=Count('question'),
            correct_answers=Sum(
                Case(
                    When(user_choice__is_correct=True, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            wrong_answers=Sum(
                Case(
                    When(user_choice__is_correct=False, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            score=Sum(
                Case(
                    When(user_choice__is_correct=True,
                         then=F('question__points')),
                    default=0,
                    output_field=IntegerField()
                )
            )
        )


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz, related_name="question", on_delete=models.CASCADE)
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, null=True, blank=True)
    QUESTION_TYPES = [
        ('single_choice', 'Single Choice'),
        ('image', 'image'),
        ('multiple_choice', 'Multiple Choice'),
        ('matching', 'Matching'),
    ]
    question_type = models.CharField(
        max_length=20, choices=QUESTION_TYPES, default='single_choice')
    points = models.IntegerField(default=1)
    time = models.TimeField(null=True)
    feedback = models.TextField(null=True, blank=True)
    ques_text = models.CharField(max_length=255)

    def __str__(self):
        return self.ques_text


class Choice(models.Model):
    question = models.ForeignKey(
        Question, related_name="choices", on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=255)
    choice_image = models.ImageField(upload_to="quiz/", null=True, blank=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text

    class Meta:
        db_table = "choices"


# class Result(models.Model):
#     quiz = models.ForeignKey(Quiz, related_name="quiz",
#                              on_delete=models.CASCADE)
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     user_choice = models.ForeignKey(
#         Choice, related_name="result_choice", on_delete=models.CASCADE)
#     # You can add more fields to store user information or timestamps if needed

#     def __str__(self):
#         return f"{self.quiz.name} - {self.user.email}"

#     class Meta:
#         unique_together = ('quiz', 'user')


class Result(models.Model):
    quiz = models.ForeignKey(Quiz, related_name="quiz",
                             on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_choice = models.ForeignKey(
        Choice, related_name="result_choice", on_delete=models.CASCADE)
    feedback = models.TextField(null=True, blank=True)  # Add feedback field

    def __str__(self):
        return f"{self.quiz.name} - {self.user.email}"
