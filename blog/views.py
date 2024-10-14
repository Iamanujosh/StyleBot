from django.shortcuts import render, redirect
from . import forms
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
import os
import requests
from django.core.files.storage import FileSystemStorage
# views.py
import os
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
import base64
from django.utils.safestring import mark_safe
from django.core.files.storage import default_storage
from .models import Profile

# Configure the API key
my_api_key = 'AIzaSyDwcpxJ34DnWKBEFPC78FAiQ5kKQd8yXC4'
genai.configure(api_key=my_api_key)


history = []

generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

system_prompt = """
  
 Youre an style suggestion chatbot
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings,
    system_instruction=system_prompt
)
def chat(request):
     
     context = {}

     if request.method == "POST":
        image_file = request.FILES.get('image', None)
        user_input = request.POST.get('user_input', None)

        # Check if an image was uploaded
        if image_file:
            # Save the uploaded image temporarily
            image_path = default_storage.save(f"temp/{image_file.name}", image_file)
            
            with open(image_path, "rb") as image:
                image_data = image.read()

            # Encode image data to Base64
            image_data_base64 = base64.b64encode(image_data).decode('utf-8')

            # Prepare image part
            image_part = {
                "mime_type": image_file.content_type,  # Ensure correct MIME type
                "data": image_data_base64  # Use Base64-encoded string
            }

            prompt_parts = [image_part, system_prompt] if not user_input else [user_input, image_part, system_prompt]

            # Generate response using the model
            response = model.generate_content(prompt_parts)
            
            if response:
                context['message'] = response.text
                print(response.text)
                return JsonResponse({'bot_response': response.text})

            # Clean up the temporary file
            os.remove(image_path)
        elif user_input:
            context['message'] = "No matching symptoms found. Please provide more details."
            chat_session = model.start_chat(history=history)
            response = chat_session.send_message(user_input)
            model_response = bold_asterisk_text(response.text)
            example_message = "<b>Hello!</b> This message is <i>italicized</i>."


            
            # Append user and bot messages to the history
            history.append({"role": "user", "parts": [user_input]})
            history.append({"role": "model", "parts": [model_response]})
            
            # Return JSON response for the bot's reply
            context = {
            'message': history,
            'example_message': mark_safe(example_message)  # Mark as safe for rendering
        }
            print(history)
            print("Doctor Card:", context.get('doctor_card'))  # Debug output

            return JsonResponse({
                'bot_response': model_response,
                'doctor_card': context.get('doctor_card'),  # Doctor details if found
                'history': history
            })
        
        else:
            # If neither image nor text is provided, show an error message
            context['error'] = "Please provide an image or text input for analysis."

     return render(request, 'blog/chat.html', context)

def bold_asterisk_text(sentence):
    # Replace *word* with <strong>word</strong>
   
    sentence = sentence.replace('\n','<br>')
    while '**' in sentence:
        start = sentence.find('**')
        end = sentence.find('**', start + 1)
        
        if start != -1 and end != -1:
            # Replace the asterisks and make it bold
            sentence = sentence[:start] + '<strong>' + sentence[start + 1:end] + '</strong>' + sentence[end + 1:]
        else:
            break
            
    return sentence








def chatbot(request):
    if request.method == "POST":
        user_input = request.POST.get("user_input")

        if not user_input:
            return JsonResponse({'error': 'No user input provided'}, status=400)

        try:
            chat_session = model.start_chat(history=history)
            response = chat_session.send_message(user_input)
            model_response = response.text

            # Append user and bot messages to the history
            history.append({"role": "user", "parts": [user_input]})
            history.append({"role": "model", "parts": [model_response]})

            # Return JSON response for the bot's reply
            return JsonResponse({'bot_response': model_response, 'history': history})

        except Exception as e:
            # Log the exception
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    # Render the initial chat page with existing history
    return render(request, 'blog/chatbot.html', {'messages': history})

def home_view(request):
    return render(request,'blog/home.html')

def login_view(request):
    if request.method == 'POST':
        form = forms.LoginForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('chatbot')  # Redirect to home page after successful login
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid form submission.')

    else:
        form = forms.LoginForm()

    return render(request, 'blog/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            form.save()  # This saves the user to the database
            return redirect('login')  # Redirect to login page after registration
    else:
        form = forms.RegisterForm()
    
    return render(request, 'blog/register.html', {'form': form})
   
def profile_view(request):
    profile = Profile.objects.get(user=request.user)  # Get the profile linked to the logged-in user
    return render(request, 'profile.html', {'profile': profile})

# Edit Profile view
# @login_required
def edit_profile(request):
    profile = form.Profile.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = form.ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()  # Save the updated profile information
            return redirect('profile')  # Redirect to profile view after saving
    else:
        form = form.ProfileForm(instance=profile)  # Pre-fill form with existing data

    return render(request, 'user_info.html', {'form': form})