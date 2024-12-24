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

        # Define stop words to filter out
        stop_words = {
            'is', 'what', 'how', 'why', 'when', 'where', 'who', 'which', 'the', 
            'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
            'with', 'by', 'about', 'like', 'as', 'from', 'into', 'during', 'including',
            'until', 'against', 'among', 'throughout', 'despite', 'towards', 'upon',
            'tell', 'me', 'please', 'can', 'could', 'would', 'should', 'shall'
        }

        # Clean the message by removing stop words
        message_words = [word for word in message.split() if word not in stop_words]
        cleaned_message = ' '.join(message_words)

        try:
            # 1. First try exact query match with cleaned message
            cms_content = CMSContent.objects.filter(
                query__iexact=cleaned_message,
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

            # 2. Try keyword matching from query
            message_words_set = set(message_words)  # Using cleaned words
            cms_contents = CMSContent.objects.filter(language=language)
            
            matches = []
            
            for content in cms_contents:
                # Clean the query words as well
                query_words = set([word for word in content.query.lower().split() 
                                 if word not in stop_words])
                
                matching_words = len(message_words_set.intersection(query_words))
                
                if matching_words > 0:
                    matches.append({
                        'content': content,
                        'matches': matching_words
                    })

            if matches:
                best_matches = matches[:3]
                combined_response = "\n\n---\n\n".join(
                    [match['content'].content for match in best_matches]
                )

                ChatMessage.objects.create(
                    user_message=message,
                    bot_response=combined_response,
                    language=language
                )

                return Response({
                    'bot_response': combined_response,
                    'source': 'cms',
                    'multiple_matches': True,
                    'match_count': len(best_matches)
                })

            # 3. If no matches, use Gemini and learn from it
            prompt = f"""
            You are a Capital Max NEPSE (Nepal Stock Exchange) assistant. 
            Answer the following question in {'Nepali' if language == 'ne' else 'English'} language:
            {message}
            
            Keep the response concise and relevant to NEPSE only.
            If the question is not related to NEPSE, politely inform that you can only answer NEPSE-related queries.
            Provide accurate and factual information only.
            """

            response = model.generate_content(prompt)
            bot_response = response.text

            # Store the new query and response in CMS if it's a valid NEPSE-related query
            if "only answer NEPSE-related queries" not in bot_response.lower():
                try:
                    # Generate a unique key from the query
                    key = f"learned_{len(message_words)}_{hash(message)}"
                    
                    # Create new CMS content
                    CMSContent.objects.create(
                        key=key,
                        query=message,
                        content=bot_response,
                        language=language
                    )
                except Exception as e:
                    print(f"Learning error: {str(e)}")

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