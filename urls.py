from django.urls import path
from . import views

urlpatterns = [
    path('', views.path_overview, name='path_overview'),
    path('ajax/load-schoolmajors/', views.load_schoolmajors, name='ajax_load_schoolmajors'), # AJAX
    path('path_detail/<int:id>', views.path_detail, name='path_detail'),
    path('add_course/<int:course_id>', views.add_course, name='add_course')
]
