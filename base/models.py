from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse_lazy

class Task(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    flag=models.BooleanField(default=True)
    file_upload = models.FileField(upload_to='uploads/', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        order_with_respect_to = 'user'
    # 추가    
    def get_file_url(self):
        if self.file_upload:
            return reverse_lazy('file_download', kwargs={'pk': self.pk})
        return ''
