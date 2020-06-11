from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('revert/', views.revertvm, name='revertvm'),
    path('stopscenario/', views.cancel_scenario, name='stopscenario')
]
