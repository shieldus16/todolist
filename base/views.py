from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from django.views import View
from django.shortcuts import redirect
from django.db import transaction

from .models import Task
from .forms import PositionForm
from django.contrib.auth.models import User

from django.http import FileResponse
import mimetypes
from django.core.files.storage import default_storage

class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    
    def get_queryset(self):
        # 현재 사용자와 flag가 True인 Task만 필터링하여 반환
        return Task.objects.filter(user=self.request.user, flag=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__contains=search_input)

        context['search_input'] = search_input

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete', 'file_upload']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        if self.request.FILES:
            form.instance.attached = self.request.FILES['file_upload']
        
        form.save()
        return super().form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete', 'file_upload']
    success_url = reverse_lazy('tasks')

class SoftDeleteTaskView(DeleteView):
    template_name ='base/task_confirm_delete.html'

    def get(self, request, pk):
        model = Task.objects.get(pk=pk)
        return render(request, self.template_name, {'task': model})

    def post(self, request, pk):
        task = Task.objects.get(pk=pk)
        task.flag = False
        task.save()
        return redirect('tasks')

class TaskReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        if form.is_valid():
            positionList = form.cleaned_data["position"].split(',')

            with transaction.atomic():
                self.request.user.set_task_order(positionList)

        return redirect(reverse_lazy('tasks'))
    

class FileDownloadView(View):
    def get(self, request, pk):
        task = Task.objects.get(pk=pk)
        file_path = task.file_upload.path

        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or 'application/octet-stream'

        response = FileResponse(default_storage.open(file_path, 'rb'), content_type=mime_type)
        response['Content-Disposition'] = f'attachment; filename={task.file_upload.name}'
        return response

        # 파일을 다운로드할 파일이 없는 경우 처리
        return HttpResponse("파일을 찾을 수 없습니다.", status=404)
    
class OtherUserTaskList(ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'base/other_user_task_list.html'

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        context['user'] = user
        # 현재 로그인한 사용자를 제외한 모든 사용자를 가져와 템플릿에 전달
        context['other_users'] = User.objects.exclude(id=self.request.user.id)
        context['is_admin'] = self.request.user.is_staff
        return context
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        # flag 값이 True이고 해당 사용자의 투두리스트만 가져오기
        return Task.objects.filter(user=user, flag=True)





