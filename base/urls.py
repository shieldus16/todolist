from django.urls import path
from .views import TaskList, TaskDetail, TaskCreate, TaskUpdate, CustomLoginView, RegisterPage, TaskReorder, FileDownloadView, SoftDeleteTaskView, OtherUserTaskList
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegisterPage.as_view(), name='register'),

    path('', TaskList.as_view(), name='tasks'),
    path('task/<int:pk>/', TaskDetail.as_view(), name='task'),
    path('task-create/', TaskCreate.as_view(), name='task-create'),
    path('task-update/<int:pk>/', TaskUpdate.as_view(), name='task-update'),
    path('task-reorder/', TaskReorder.as_view(), name='task-reorder'),
    path('file-download/<int:pk>/', FileDownloadView.as_view(), name="download"),
    path('task-soft-delete/<int:pk>/', SoftDeleteTaskView.as_view(), name='soft_delete_task'),
    path('other_user_tasks/<int:user_id>/', OtherUserTaskList.as_view(), name='other_user_tasks'),
]
