import uuid

from django.db import models


class Flag(models.Model):
    name = models.CharField(max_length=1024)
    svg = models.TextField(help_text="The SVG string to render this flag")

    def __str__(self):
        return self.name


class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    voter_ip = models.GenericIPAddressField(null=True)
    choice_1 = models.ForeignKey(
        Flag, on_delete=models.CASCADE, related_name="first_choice"
    )
    choice_2 = models.ForeignKey(
        Flag, on_delete=models.CASCADE, related_name="second_choice"
    )
    choice = models.ForeignKey(
        Flag, on_delete=models.CASCADE, related_name="chosen_choice", null=True,
    )
    voted = models.BooleanField()

    def __str__(self):
        return f"{self.choice_1} vs {self.choice_2} => {self.choice}"
