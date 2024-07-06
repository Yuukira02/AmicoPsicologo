from django.db import models
from django.contrib.auth.models import User

class ANS_TYPES(models.TextChoices):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"

class PsyTest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(default=None)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.title}"

class Question(models.Model):
    question = models.CharField(max_length=200, unique=True)
    rel_test = models.ForeignKey(PsyTest, on_delete=models.CASCADE, related_name="questions")

    def __str__(self):
        return f"{self.rel_test}: {self.question}"

class Answer(models.Model): 
    rel_question = models.ForeignKey(Question, to_field="question", on_delete=models.CASCADE, related_name="answers")
    answer = models.CharField(max_length=500)
    answer_type = models.CharField(
        max_length=1,
        choices=ANS_TYPES.choices,
    )

    # DI DEBUG DA ADMIN: 
    # def __str__(self):
    #     return f"{self.rel_question.rel_test} - {self.answer_type}: {self.answer}"
    def __str__(self):
        return f"{self.answer_type}: {self.answer}"
    
class TestResult(models.Model):
    rel_test = models.ForeignKey(PsyTest, on_delete=models.CASCADE, related_name="ori_test")
    title = models.CharField(max_length=200)
    answer_type = models.CharField(
        max_length=1,
        choices=ANS_TYPES.choices,
    )
    content = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['rel_test', 'answer_type'], name='unique_res_per_quest'
            )
        ]

    def __str__(self):
        return f"{self.rel_test} {self.answer_type}: {self.title}"
    

class MyTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_tests")
    result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name="my_users")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'result'], name='unique_test_result_per_user'
            )
        ]
    def __str__(self):
        return f"{self.result}"