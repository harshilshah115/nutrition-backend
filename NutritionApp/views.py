from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action
from django.contrib.auth import login
from rest_framework.permissions import IsAuthenticated
import pytesseract
from PIL import Image
import re
from .models import Profile, Meal, UserMeal, FoodAnalysis
from .serializers import RegisterSerializer, MealSerializer, UserMealSerializer, FoodAnalysisSerializer

# Register API
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            #token, _ = Token.objects.get_or_create(user_id=user.id)  # Use user.id instead of user
            return Response({
                #'token': token.key, 
                'message': 'User registered successfully!'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login API
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = Profile.objects.get(email=email)
        except Profile.DoesNotExist:
            return Response({
                'error': 'Invalid email or password'},
                status=status.HTTP_400_BAD_REQUEST)

        if check_password(password, user.password):  # Validate password
            return Response({
                'message': 'Login successful!',
                #'user_id': user.id,
                #'name': user.name,
                #'email': user.email,
                #'phone_number': user.phone_number,
                #'goal': user.goal
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid email or password'},
                status=status.HTTP_400_BAD_REQUEST)
        
# List all meals (for the suggestion page)
class MealListView(generics.ListAPIView):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer

# Save user's selected meal
class UserMealCreateView(generics.CreateAPIView):
    serializer_class = UserMealSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users can add meals

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Assign logged-in user

# List meals added by the user (for My Meal Page)
class MyMealListView(generics.ListAPIView):
    serializer_class = UserMealSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserMeal.objects.filter(user=self.request.user)  # Fetch only the logged-in user's meals
    
# Define nutrition goals for comparison
GOAL_NUTRITION = {
    "weight_loss": {"protein": (50, 75), "fat": (40, 70), "carbohydrates": (150, 250)},
    "weight_gain": {"protein": (75, 100), "fat": (50, 70), "carbohydrates": (300, 400)},
    "athletic_body": {"protein": (100, 150), "fat": (40, 60), "carbohydrates": (250, 350)},
    "healthy_body": {"protein": (50, 75), "fat": (40, 70), "carbohydrates": (200, 300)},
}

# extract nutrition from image
def extract_nutrition_from_image(image):
    """Extracts protein, fat, and carbohydrate values from an image using OCR"""
    text = pytesseract.image_to_string(Image.open(image))

    # Extract numbers using regex
    protein_match = re.search(r'Protein\s*[:=]\s*(\d+)', text, re.IGNORECASE)
    fat_match = re.search(r'Fat\s*[:=]\s*(\d+)', text, re.IGNORECASE)
    carbohydrates_match = re.search(r'Carbohydrates\s*[:=]\s*(\d+)', text, re.IGNORECASE)

    return {
        "protein": float(protein_match.group(1)) if protein_match else 0,
        "fat": float(fat_match.group(1)) if fat_match else 0,
        "carbohydrates": float(carbohydrates_match.group(1)) if carbohydrates_match else 0,
    }

# evaluate/compares with food
def evaluate_food(goal, protein, fat, carbohydrates):
    """Compares extracted nutrition data with the user's goal"""
    goal_ranges = GOAL_NUTRITION.get(goal, {})

    def in_range(value, range_tuple):
        return range_tuple[0] <= value <= range_tuple[1]

    if all([
        in_range(protein, goal_ranges.get("protein", (0, 0))),
        in_range(fat, goal_ranges.get("fat", (0, 0))),
        in_range(carbohydrates, goal_ranges.get("carbohydrates", (0, 0))),
    ]):
        return "Good"

    return "Bad"

# Food Analysis API
class FoodAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        # Assume the user's goal is stored in a profile model
        goal = user.profile.goal if hasattr(user, 'profile') else None
        if not goal:
            return Response({"error": "User goal not found. Please set a goal during registration."}, status=400)

        # Get uploaded image
        image = request.FILES.get("image")
        if not image:
            return Response({"error": "Image is required"}, status=400)

        # Step 2: Extract nutrition data
        nutrition_data = extract_nutrition_from_image(image)

        # Step 3: Compare with the user's goal
        result = evaluate_food(goal, nutrition_data["protein"], nutrition_data["fat"], nutrition_data["carbohydrates"])

        # Save analysis result in database
        food_analysis = FoodAnalysis.objects.create(
            user=user,
            image=image,
            protein=nutrition_data["protein"],
            fat=nutrition_data["fat"],
            carbohydrates=nutrition_data["carbohydrates"],
            result=result
        )

        # Return response
        serializer = FoodAnalysisSerializer(food_analysis)
        return Response(serializer.data, status=201)

