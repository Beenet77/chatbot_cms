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
        message = request.data.get('message', '').lower()
        language = request.data.get('language', 'en')

        try:
            # 1. First try exact query match
            cms_content = CMSContent.objects.filter(
                query__iexact=message,
                language=language
            ).first()

            if cms_content:
                ChatMessage.objects.create(
                    user_message=message,
                    bot_response=cms_content.content,
                    language=language
                )
                return Response({
                    'bot_response': cms_content.content,
                    'source': 'cms'
                })

            # 2. Try key match
            cms_content = CMSContent.objects.filter(
                key__icontains=message,
                language=language
            ).first()

            if cms_content:
                ChatMessage.objects.create(
                    user_message=message,
                    bot_response=cms_content.content,
                    language=language
                )
                return Response({
                    'bot_response': cms_content.content,
                    'source': 'cms'
                })

            # 3. Try keyword matching from query only
            message_words = set(message.split())
            cms_contents = CMSContent.objects.filter(language=language)
            
            best_match = None
            max_matches = 0
            
            for content in cms_contents:
                # Only match with query words
                query_words = set(content.query.lower().split())
                matches = len(message_words.intersection(query_words))
                
                if matches > max_matches:
                    max_matches = matches
                    best_match = content

            # If we found a good query word match (at least one word matches)
            if best_match and max_matches > 0:
                ChatMessage.objects.create(
                    user_message=message,
                    bot_response=best_match.content,
                    language=language
                )
                return Response({
                    'bot_response': best_match.content,
                    'source': 'cms'
                })

            # 4. If no matches in CMS, use Gemini
            prompt = f"""
            You are a NEPSE (Nepal Stock Exchange) assistant. 
            Answer the following question in {'Nepali' if language == 'ne' else 'English'} language:
            {message}
            
            Keep the response concise and relevant to NEPSE only.
            If the question is not related to NEPSE, politely inform that you can only answer NEPSE-related queries.
            """

            response = model.generate_content(prompt)
            bot_response = response.text

            ChatMessage.objects.create(
                user_message=message,
                bot_response=bot_response,
                language=language
            )

            return Response({
                'bot_response': bot_response,
                'source': 'gemini'
            })

        except Exception as e:
            print(f"Error: {str(e)}")
            error_message = (
                "माफ गर्नुहोस्, केही समस्या आयो। कृपया फेरि प्रयास गर्नुहोस्।"
                if language == "ne"
                else "Sorry, I encountered an error. Please try again."
            )
            return Response({
                'bot_response': error_message,
                'source': 'error'
            })

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
        print(f"Request method: {request.method}")
        print("Request data:", request.data) 
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
            return Response({'message': 'A user with this username or email already exists'}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)