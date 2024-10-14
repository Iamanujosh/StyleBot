This project is a Gemini chatbot that allows users to upload a photo of their clothing and receive style suggestions, as well as interact via text for other styling tips.

Project Structure
The core of the project includes:

User Authentication (Login/Register) - Users can register or log in to use the chatbot.
Main Chat Screen - Once logged in, users can either send messages or upload photos to get fashion advice.

Key Files
views.py
Contains the core logic for handling user authentication, chatbot processing, and communication with the Gemini API.

urls.py
Defines the URL patterns for the project, routing requests to the appropriate views.

chat.html
The frontend chat interface where users can interact with the chatbot. Users can send messages and upload images for styling suggestions.

settings.py
The configuration file where the Gemini API key is stored securely and database settings are defined.

still there is no css i just want to create boiler for project.
