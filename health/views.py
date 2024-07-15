from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import spacy

from rest_framework import generics, permissions
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, RegisterSerializer
from django.contrib.auth import authenticate
from .models import ChatHistory

nlp = spacy.load("en_core_web_sm")

# Data here
symptom_health_plans = {
    "headache": [
        "Take pain relievers like ibuprofen, rest in a quiet and dark room, and apply a cold compress.",
        "Ensure adequate hydration, practice relaxation techniques, and avoid headache triggers like certain foods or stress."
    ],
    "fever": [
        "Drink plenty of fluids, take rest, and use fever reducers like acetaminophen.",
        "Monitor temperature regularly, stay in a cool environment, and seek medical attention if fever persists for more than 3 days."
    ],
    "fatigue": [
        "Ensure adequate sleep, maintain a balanced diet, and engage in regular physical activity.",
        "Reduce stress, consider vitamins or supplements, and consult a doctor if fatigue is persistent."
    ],
    "cough": [
        "Use cough syrups or lozenges, stay hydrated, and avoid irritants like smoke.",
        "Try steam inhalation, use a humidifier, and consider over-the-counter cough medications."
    ],
    "sore throat": [
        "Gargle with warm salt water, drink warm fluids, and use throat lozenges.",
        "Avoid irritants like smoke, use a humidifier, and take over-the-counter pain relievers if needed."
    ],
    "muscle pain": [
        "Apply ice or heat to the affected area, take pain relievers, and rest the muscles.",
        "Engage in gentle stretching exercises, stay hydrated, and consider physical therapy if pain persists."
    ],
    "dengue": [
        "Stay hydrated by drinking plenty of fluids, take rest, and use acetaminophen for pain relief. Avoid non-steroidal anti-inflammatory drugs (NSAIDs) like ibuprofen and aspirin.",
        "Monitor for warning signs such as severe abdominal pain, persistent vomiting, bleeding gums, or blood in vomit or stool. Seek immediate medical attention if these symptoms occur. Follow the doctor's advice on blood tests and hospitalization if required."
    ],
    "cancer": [
        "Follow the treatment plan prescribed by your oncologist, which may include surgery, chemotherapy, radiation therapy, immunotherapy, or targeted therapy. Maintain a healthy diet and stay physically active as much as possible.",
        "Attend all scheduled medical appointments, keep a symptom diary, and communicate any new or worsening symptoms to your healthcare provider. Consider joining a support group for emotional and psychological support."
    ],
    "hi": [
        "Hi How are you today ?"
    ],
    "hey": [
        "Hey there, How are you today ?"
    ],
    "hello": [
        "Hello How are you today ?"
    ],
    "good": [
        "Great carry on"
    ],
    "nice": [
        "Great carry on"
    ],
    "bye": [
        "Bye! Have a great day"
    ]
}

disease_symptoms = {
    "fever": ["Headache, Vomiting, diarrhea, Low output of urine or dark urine"],
    "dengue": ["High fever, Severe headache, Pain behind the eyes, Severe joint and muscle pain, Fatigue, Nausea, Vomiting, Skin rash, Mild bleeding (e.g., nosebleed, gum bleeding)"],
    "cancer": ["Unexplained weight loss, Fever, Fatigue, Pain, Skin changes, Change in bowel or bladder habits, Persistent cough, Difficulty swallowing, Unusual bleeding or discharge"]
}

keywords = ['pain', 'throat', 'loss', 'nose']

def extract_symptoms(user_query, keywords):
    results = []
    for keyword in keywords:
        if keyword in user_query:
            results.append(keyword)
            index = user_query.index(keyword)
            left_word = user_query[index - 7:index].strip().split()[-1]
            results.append(f"{left_word} {keyword}")

    return results

class HealthInfoView(APIView):
    def post(self, request):
        query = request.data.get('query', '')
        username = request.data.get('username')  # Get username from request
        if not query:
            return Response({"error": "Query not provided"}, status=status.HTTP_400_BAD_REQUEST)

        # NLP processing
        doc = nlp(query.lower())
        symptoms = [token.text for token in doc if token.text in symptom_health_plans]
        missing_symptoms = extract_symptoms(query.lower(), keywords)
        symptoms.extend(missing_symptoms)

        health_plans = []
        for symptom in symptoms:
            if symptom in symptom_health_plans and symptom not in ["hi", "hello", "good", "nice", 'hey']:
                health_plans.append(f"Health plan for {symptom}:")
            if symptom in symptom_health_plans:
                health_plans.extend(symptom_health_plans[symptom])

        diseases = [token.text for token in doc if token.text in disease_symptoms]
        disease_symptoms_list = []
        for disease in diseases:
            if disease in disease_symptoms:
                if "symptom" in query.lower() or "symptoms" in query.lower() or "Symptom" in query.lower() or "Symptoms" in query.lower():
                    disease_symptoms_list.append(f"You mentioned disease named: {disease}. Below are the expected symptoms:")
                    disease_symptoms_list.extend(disease_symptoms[disease])
                    
        if not health_plans and not disease_symptoms_list:
            health_plans.append("Sorry, I don't have information on that.")
            
        response_data = {
            "health_plans": health_plans,
            "disease_symptoms": disease_symptoms_list
        }

        # Save chat history
        chat_history = ChatHistory(
            username=username,
            user_query=query,
            bot_health_plans=health_plans,
            bot_disease_symptoms=disease_symptoms_list
        )
        chat_history.save()

        return Response(response_data, status=status.HTTP_200_OK)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class LoginView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class LogoutView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)