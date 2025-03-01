from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    GOAL_CHOICES = [
        ('Athletic Body', 'Athletic Body'),
        ('Weight Loss', 'Weight Loss'),
        ('Weight Gain', 'Weight Gain'),
        ('Healthy Body', 'Healthy Body'),
    ]

    name = models.CharField(max_length=250)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    email = models.EmailField(max_length=250, unique=True)
    phone_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES)
    target_weight = models.FloatField(null=True, blank=True)
    username = models.CharField(max_length=250, unique=True)
    password = models.CharField(max_length=250)  # Manually handle hashing

    def __str__(self):
        return self.name

class Meal(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='meal_images/')
    calories = models.FloatField()
    protein = models.FloatField()
    fats = models.FloatField()

    def __str__(self):
        return self.title
    
class UserMeal(models.Model):
    DAY_CHOICES = [
        ('Sunday', 'Sunday'), ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),('Friday', 'Friday'), 
        ('Saturday', 'Saturday')
    ]

    CATEGORY_CHOICES = [
        ('Breakfast', 'Breakfast'), 
        ('Lunch', 'Lunch'), 
        ('Dinner', 'Dinner')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.meal.title} ({self.day}, {self.category})"
    
class FoodAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='food_images/')
    protein = models.FloatField()
    fat = models.FloatField()
    carbohydrates = models.FloatField()
    result = models.CharField(max_length=255)  # "Good" or "Bad" for the goal
    