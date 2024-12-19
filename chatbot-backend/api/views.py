from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CMSContent, ChatMessage , Logo
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from .serializers import CMSContentSerializer, ChatMessageSerializer, LogoSerializer
import google.generativeai as genai
from django.conf import settings
import json
from django.contrib.auth.models import User
from django.db import IntegrityError




# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

class GetCMSContentView(RetrieveAPIView):
    queryset = CMSContent.objects.all()
    serializer_class = CMSContentSerializer
    lookup_field = 'key'

    def get_queryset(self):
        # Filter based on language
        language = self.kwargs.get('language', 'en')
        return CMSContent.objects.filter(language=language)

    def get(self, request, *args, **kwargs):
        key = kwargs.get("key")
        language = kwargs.get("language")
        try:
            content = CMSContent.objects.get(key=key, language=language)
            serializer = self.get_serializer(content)
            return Response(serializer.data)
        except CMSContent.DoesNotExist:
            return Response({"error": "Content not found"}, status=404)

class HandleChatView(APIView):
    def post(self, request, *args, **kwargs):
        user_message = request.data.get("message")
        language = request.data.get("language", "en")

        # Get relevant CMS content
        cms_data = CMSContent.objects.filter(language=language)
        
        # Format CMS content as messages
        cms_messages = []
        for content in cms_data:
            if content.key.lower() in user_message.lower():
                cms_messages.append(content.content)

        # If CMS content is found, return it directly
        if cms_messages:
            bot_response = "\n\n".join(cms_messages)
            
            # Log chat
            ChatMessage.objects.create(
                user_message=user_message,
                bot_response=bot_response,
                language=language
            )
            
            return Response({
                "user_message": user_message,
                "bot_response": bot_response,
                "source": "cms"
            })

        # If no CMS content, use Gemini
        context = "\n".join([f"{item.key}: {item.content}" for item in cms_data])

        # Prepare prompt based on language
        if language == 'ne':
            system_prompt = f"""You are a helpful assistant that provides information about NEPSE (Nepal Stock Exchange).
            First, check if the answer exists in this CMS context: {context}
            If not found in CMS, provide a general response about NEPSE.
            Always respond in romanized Nepali.
            If you don't have specific information, provide general guidance about NEPSE trading."""
        else:
            system_prompt = f"""You are a helpful assistant that provides information about NEPSE (Nepal Stock Exchange).
            First, check if the answer exists in this CMS context: {context}
            If not found in CMS, provide a general response about NEPSE.
            Always respond in English.
            If you don't have specific information, provide general guidance about NEPSE trading."""

        try:
            # Generate response using Gemini
            chat = model.start_chat(history=[])
            response = chat.send_message(f"{system_prompt}\n\nUser: {user_message}")
            bot_response = response.text

            # Log chat
            ChatMessage.objects.create(
                user_message=user_message,
                bot_response=bot_response,
                language=language
            )

            return Response({
                "user_message": user_message,
                "bot_response": bot_response,
                "source": "bot"
            })

        except Exception as e:
            error_message = ("I apologize, but I'm having trouble processing your request right now. Please try again later." 
                           if language == "en" 
                           else "Maaf garnuhos, kehi prawidhik samasya aayo. Kripaya pachi prayas garnuhos.")
            return Response({
                "user_message": user_message,
                "bot_response": error_message,
                "source": "error"
            }, status=500)
class LogoView(APIView):
    def get_logo(self, logo_type):
        """
        Helper method to fetch a logo by type.
        Returns the first matching logo or None.
        """
        

    def get(self, request, *args, **kwargs):
        # Fetch logos
        try:
            mascot_logo = Logo.objects.get(logo_type="chatbot")
            print("*****",mascot_logo)
        except Logo.DoesNotExist:
            mascot_logo = None
        except Logo.MultipleObjectsReturned:
            mascot_logo = Logo.objects.filter(logo_type="chatbot").first()


        try:
            
            main_logo = Logo.objects.get(logo_type="main")
        except Logo.DoesNotExist:
            main_logo = None
        except Logo.MultipleObjectsReturned:
            main_logo = Logo.objects.filter(logo_type="main").first()
       
        print(f"############################## {mascot_logo.logo.url} ##############################")
        print(f"############################## {main_logo.logo.url} ##############################")
        
     
        
        # Prepare the response
        if mascot_logo and main_logo:
            return Response({
                'mascot_logo': mascot_logo.logo.url,
                'main_logo': main_logo.logo.url,
            })
        elif mascot_logo:
            return Response({
                'mascot_logo': mascot_logo.logo.url,
            })
        elif main_logo:
            return Response({
                'main_logo': main_logo.logo.url,
            })
        else:
            return Response({"error": "No logo found"}, status=HTTP_404_NOT_FOUND)
        
class HandleChatUser(APIView):
    def post(self, request, *args, **kwargs):
        print("Request data:", request.data)  # Debugging line
        user_name = request.data.get('user_name')
        user_email = request.data.get('user_email')

        if not user_name or not user_email:
            return Response({'error': 'user_name and user_email are required'}, status=400)

        try:
            user = User.objects.create(
                username=user_name,
                email=user_email,
            )
            user.save()
            return Response({'message': 'User created successfully', 'user_id': user.id}, status=200)
        except IntegrityError:
            return Response({'error': 'A user with this username or email already exists'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)