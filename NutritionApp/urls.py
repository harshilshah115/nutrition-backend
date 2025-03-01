from django.urls import path, include
from .views import RegisterView, LoginView, MealListView, UserMealCreateView, MyMealListView, FoodAnalysisView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('meals/', MealListView.as_view(), name='meal-list'),
    path('my-meals/', MyMealListView.as_view(), name='my-meal-list'),
    path('add-meal/', UserMealCreateView.as_view(), name='add-meal'),
    path('analyze-food/', FoodAnalysisView.as_view(), name='analyze-food'),
]
