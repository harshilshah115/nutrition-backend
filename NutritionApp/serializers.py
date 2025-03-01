from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Profile, Meal, UserMeal, FoodAnalysis


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Profile
        fields = [
            'name', 'dob', 'gender', 'email', 'phone_number', 'height', 
            'weight', 'goal', 'target_weight', 'username', 'password', 'confirm_password'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match!"})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Remove confirm_password
        validated_data['password'] = make_password(validated_data['password'])  # Hash password
        return Profile.objects.create(**validated_data)

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = '__all__'  # Sends all meal fields in API response

class UserMealSerializer(serializers.ModelSerializer):
    meal_details = MealSerializer(source='meal', read_only=True)  # Nested meal details

    class Meta:
        model = UserMeal
        fields = ['id', 'user', 'meal', 'day', 'category', 'meal_details']
        extra_kwargs = {'user': {'read_only': True}}  # User is automatically assigned

class FoodAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodAnalysis
        fields = ['id', 'user', 'image', 'protein', 'fat', 'carbohydrates', 'result']
        read_only_fields = ['user', 'result', 'protein', 'fat', 'carbohydrates']

