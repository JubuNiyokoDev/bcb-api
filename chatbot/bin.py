# # import os
# # import json
# # from difflib import get_close_matches
# # from django.conf import settings
# # import google.generativeai as client
# # from sentence_transformers import SentenceTransformer, util
# # import torch

# # # --- Configuration Gemini Client ---
# # client.configure(api_key=settings.GOOGLE_API_KEY)
# # model = client.GenerativeModel("gemini-2.0-flash")

# # # --- Global variables for Sentence-Transformers Model and Dataset ---
# # embedding_model = None
# # DATASET = {}
# # TRAINING_PHRASES_EMBEDDINGS = {}
# # INTENT_PHRASE_MAPPING = {}
# # ALL_SERVICE_NAMES = []

# # # --- Session Chat Memory & Context Management ---
# # session_chats = {}
# # session_context = {}


# # def load_sentence_transformer_model():
# #     """
# #     Loads the Sentence-Transformer model. This function is called once.
# #     """
# #     global embedding_model
# #     try:
# #         # It's crucial to ensure this model is accessible or downloaded.
# #         # 'paraphrase-multilingual-MiniLM-L12-v2' is a good choice for multilingual support.
# #         embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
# #         print("Sentence-Transformers model loaded successfully.")
# #     except Exception as e:
# #         print(f"Error loading Sentence-Transformers model: {e}")
# #         print(
# #             "Please ensure you have an internet connection or the model files are cached locally."
# #         )
# #         print(
# #             "You can try downloading it manually: https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# #         )
# #         embedding_model = None  # Ensure it's None if loading fails


# # # Load the model immediately when the module is imported
# # load_sentence_transformer_model()


# # def load_json_dataset():
# #     """
# #     Loads the dataset and pre-calculates embeddings for training phrases.
# #     This should ideally run once at application startup.
# #     """
# #     global DATASET, TRAINING_PHRASES_EMBEDDINGS, INTENT_PHRASE_MAPPING, ALL_SERVICE_NAMES

# #     json_path = os.path.join(settings.BASE_DIR, "bcb_dataset.json")
# #     try:
# #         with open(json_path, "r", encoding="utf-8") as file:
# #             DATASET = json.load(file)
# #     except FileNotFoundError:
# #         print(
# #             f"Error: bcb_dataset.json not found at {json_path}. Please ensure the file exists."
# #         )
# #         DATASET = {"intents": []}  # Initialize as empty to prevent further errors
# #         return
# #     except json.JSONDecodeError:
# #         print(f"Error: bcb_dataset.json is not a valid JSON file at {json_path}.")
# #         DATASET = {"intents": []}
# #         return

# #     # Pre-calculate embeddings only if the embedding model loaded successfully
# #     if embedding_model:
# #         for intent_data in DATASET.get("intents", []):
# #             intent_name = intent_data["intent_name"]
# #             phrases = intent_data["training_phrases"]

# #             INTENT_PHRASE_MAPPING[intent_name] = phrases

# #             processed_phrases = []
# #             for phrase in phrases:
# #                 processed_phrase = phrase.replace(
# #                     "{service_name_fr}", "un service bancaire"
# #                 )
# #                 processed_phrases.append(processed_phrase)

# #             try:
# #                 TRAINING_PHRASES_EMBEDDINGS[intent_name] = embedding_model.encode(
# #                     processed_phrases, convert_to_tensor=True
# #                 )
# #             except Exception as e:
# #                 print(
# #                     f"Warning: Could not encode phrases for intent '{intent_name}': {e}"
# #                 )
# #                 TRAINING_PHRASES_EMBEDDINGS[intent_name] = torch.tensor(
# #                     []
# #                 )  # Set as empty tensor

# #     # Collect all service names for entity extraction
# #     service_info_intent = next(
# #         (
# #             intent
# #             for intent in DATASET.get("intents", [])
# #             if intent["intent_name"] == "informations_service"
# #         ),
# #         None,
# #     )
# #     if service_info_intent:
# #         for service_key, service_details in service_info_intent["responses"].items():
# #             ALL_SERVICE_NAMES.append(
# #                 {
# #                     "key": service_key,
# #                     "fr": service_details.get("fr"),
# #                     "rn": service_details.get("rn"),
# #                     "en": service_details.get("en"),
# #                 }
# #             )


# # # Load the dataset and pre-calculate embeddings at module import
# # load_json_dataset()


# # def extract_entities(text, user_language):
# #     """
# #     Extracts entities (like service names) from the user's text.
# #     This is a more robust version than simple string search.
# #     """
# #     extracted_service_key = None
# #     text_lower = text.lower()

# #     for service_info in ALL_SERVICE_NAMES:
# #         names_to_check = [service_info["key"].lower()]
# #         if service_info.get(user_language):
# #             names_to_check.append(service_info[user_language].lower())
# #         if service_info.get("fr") and user_language != "fr":
# #             names_to_check.append(service_info["fr"].lower())
# #         if service_info.get("en") and user_language != "en":
# #             names_to_check.append(service_info["en"].lower())
# #         if service_info.get("rn") and user_language != "rn":
# #             names_to_check.append(service_info["rn"].lower())

# #         for name_variant in set(names_to_check):
# #             if name_variant and name_variant in text_lower:
# #                 extracted_service_key = service_info["key"]
# #                 break
# #         if extracted_service_key:
# #             break

# #     return {"service_key": extracted_service_key}


# # def find_intent_and_confidence(text, chat_session_context):
# #     """
# #     Identifies the most likely intent using Sentence-Transformers for semantic similarity,
# #     and returns a confidence score.
# #     Also handles greetings and simple thank yous first using exact match.
# #     """
# #     # If the embedding model failed to load, we cannot perform semantic search.
# #     # Fallback to general inquiry or simpler matching.
# #     if embedding_model is None:
# #         print(
# #             "Warning: Embedding model not loaded. Falling back to basic intent detection."
# #         )
# #         # Basic fallback: try exact matches for greetings/thanks
# #         for intent_data in DATASET.get("intents", []):
# #             if intent_data["intent_name"] == "support_general":
# #                 for phrase in intent_data["training_phrases"]:
# #                     if get_close_matches(
# #                         text.lower(), [phrase.lower()], n=1, cutoff=0.9
# #                     ):
# #                         if "bonjour" in text.lower() or "salut" in text.lower():
# #                             return {
# #                                 "intent_name": "support_general",
# #                                 "score": 1.0,
# #                                 "service_key": "greeting",
# #                             }
# #                         elif "merci" in text.lower() or "grâce" in text.lower():
# #                             return {
# #                                 "intent_name": "support_general",
# #                                 "score": 1.0,
# #                                 "service_key": "thanks",
# #                             }
# #         return {
# #             "intent_name": "general_inquiry",
# #             "score": 0.0,
# #             "service_key": None,
# #         }  # Default fallback

# #     user_embedding = embedding_model.encode(text, convert_to_tensor=True)
# #     best_match = {"intent_name": "general_inquiry", "score": 0.0, "service_key": None}

# #     # 1. Prioritize exact matches for greetings/thanks (high confidence)
# #     for intent_data in DATASET.get("intents", []):
# #         if intent_data["intent_name"] == "support_general":
# #             for phrase in intent_data["training_phrases"]:
# #                 if get_close_matches(text.lower(), [phrase.lower()], n=1, cutoff=0.9):
# #                     if "bonjour" in text.lower() or "salut" in text.lower():
# #                         return {
# #                             "intent_name": "support_general",
# #                             "score": 1.0,
# #                             "service_key": "greeting",
# #                         }
# #                     elif "merci" in text.lower() or "grâce" in text.lower():
# #                         return {
# #                             "intent_name": "support_general",
# #                             "score": 1.0,
# #                             "service_key": "thanks",
# #                         }

# #     # 2. Semantic Search for Intents
# #     for intent_name, embeddings in TRAINING_PHRASES_EMBEDDINGS.items():
# #         if embeddings.numel() > 0:
# #             similarities = util.cos_sim(user_embedding, embeddings)[0]
# #             max_similarity = torch.max(similarities).item()

# #             if max_similarity > best_match["score"]:
# #                 best_match["score"] = max_similarity
# #                 best_match["intent_name"] = intent_name

# #     # 3. Handle contextual follow-ups
# #     if best_match["score"] < 0.5 and chat_session_context["last_intent"]:
# #         last_intent = chat_session_context["last_intent"]
# #         if last_intent == "informations_service":
# #             general_follow_up_phrases = [
# #                 "comment ça marche",
# #                 "plus de détails",
# #                 "quels sont les avantages",
# #                 "conditions",
# #             ]
# #             for phrase in general_follow_up_phrases:
# #                 if phrase in text.lower():
# #                     best_match["intent_name"] = last_intent
# #                     if chat_session_context["last_service_key"]:
# #                         best_match["service_key"] = chat_session_context[
# #                             "last_service_key"
# #                         ]
# #                     best_match["score"] = 0.7
# #                     break

# #     return best_match


# # def get_response_for_intent(intent_name, service_key, lang, dataset):
# #     """
# #     Retrieves the specific response for a given intent, service, and language.
# #     Handles 'default' and 'steps' responses within intents.
# #     """
# #     for intent_data in dataset.get("intents", []):  # Use .get with default empty list
# #         if intent_data["intent_name"] == intent_name:
# #             responses = intent_data.get(
# #                 "responses", {}
# #             )  # Use .get with default empty dict

# #             if intent_name == "processus_ouverture_compte":
# #                 default_response = responses.get("default", {}).get(lang, "")
# #                 steps_response = responses.get("steps", [])

# #                 service_name_in_target_lang = service_key
# #                 if service_key:
# #                     for info_intent in dataset.get("intents", []):
# #                         if info_intent["intent_name"] == "informations_service":
# #                             svc_details = info_intent.get("responses", {}).get(
# #                                 service_key
# #                             )
# #                             if svc_details:
# #                                 service_name_in_target_lang = svc_details.get(
# #                                     lang, service_key
# #                                 )
# #                             break

# #                 full_response = (
# #                     default_response.replace(
# #                         "{service_name_fr}", service_name_in_target_lang
# #                     )
# #                     .replace("{service_name_rn}", service_name_in_target_lang)
# #                     .replace("{service_name_en}", service_name_in_target_lang)
# #                 )

# #                 if steps_response:
# #                     for step in steps_response:
# #                         full_response += "\n" + step.get(lang, "")
# #                 return full_response

# #             elif intent_name == "support_general" and service_key in responses:
# #                 return responses[service_key].get(lang, "")

# #             elif service_key and service_key in responses:
# #                 return responses[service_key].get(lang, "")
# #             elif "default" in responses:
# #                 return responses["default"].get(lang, "")

# #     return None


# # def find_language(text, chat):
# #     """Detect language using Gemini."""
# #     prompt = f"What is the language of this sentence: '{text}'? Respond with only one word: 'French', 'English', or 'Kirundi'."
# #     try:
# #         language_response = chat.send_message(prompt).text.strip().lower()
# #         if "french" in language_response:
# #             return "fr"
# #         elif "kirundi" in language_response:
# #             return "rn"
# #         elif "english" in language_response:
# #             return "en"
# #         else:
# #             return "fr"
# #     except Exception as e:
# #         print(f"Error during language detection: {e}. Defaulting to French.")
# #         return "fr"


# # def start_new_chat(session_key):
# #     """Start a new Gemini chat session and initialize context."""
# #     chat = model.start_chat()
# #     session_chats[session_key] = chat
# #     session_context[session_key] = {
# #         "last_intent": None,
# #         "last_service_key": None,
# #         "slots": {},
# #     }
# #     return chat


# # def get_chat(session_key):
# #     """Retrieve or create chat for session."""
# #     if session_key not in session_chats:
# #         return start_new_chat(session_key)
# #     return session_chats[session_key]


# # def get_session_context(session_key):
# #     """Retrieve or initialize context for session."""
# #     if session_key not in session_context:
# #         start_new_chat(session_key)
# #     return session_context[session_key]


# # def send_message(text, session_key):
# #     """Main logic: find intent and respond based on dataset or Gemini's general knowledge."""
# #     chat = get_chat(session_key)
# #     chat_context = get_session_context(session_key)

# #     try:
# #         user_language = find_language(text, chat)

# #         extracted_entities = extract_entities(text, user_language)
# #         service_key_from_entities = extracted_entities["service_key"]

# #         intent_result = find_intent_and_confidence(text, chat_context)
# #         intent_name = intent_result["intent_name"]
# #         intent_confidence = intent_result["score"]

# #         service_key_for_response = None
# #         if service_key_from_entities:
# #             service_key_for_response = service_key_from_entities
# #         elif intent_result["service_key"]:
# #             service_key_for_response = intent_result["service_key"]
# #         elif chat_context["last_service_key"] and intent_confidence < 0.7:
# #             service_key_for_response = chat_context["last_service_key"]

# #         dataset_response = get_response_for_intent(
# #             intent_name, service_key_for_response, user_language, DATASET
# #         )

# #         final_response_text = ""

# #         CONFIDENCE_THRESHOLD_HIGH = 0.8
# #         CONFIDENCE_THRESHOLD_MEDIUM = 0.6

# #         if intent_confidence < CONFIDENCE_THRESHOLD_MEDIUM:
# #             final_response_text = f"Je ne suis pas sûr de bien comprendre votre question. Pourriez-vous reformuler ou être plus précis ? "
# #             if chat_context["last_intent"]:
# #                 final_response_text += f"Étiez-vous en train de parler de nos services bancaires ou d'autre chose ?"

# #         elif (
# #             dataset_response
# #         ):  # If dataset has a direct response and confidence is acceptable
# #             prompt = (
# #                 f"L'utilisateur a posé la question suivante en {user_language_to_full_name(user_language)} : '{text}'. "
# #                 f"Voici la réponse de référence de notre base de données bancaire, déjà dans la langue de l'utilisateur : '{dataset_response}'. "
# #                 f"Veuillez reformuler cette réponse de manière naturelle, utile et empathique, en tant qu'assistant virtuel pour 'BCB EasyBank'. "
# #                 f"Assurez-vous que la réponse est UNIQUEMENT en {user_language_to_full_name(user_language)}. "
# #                 f"Évitez les traductions entre parenthèses. Soyez concis et direct."
# #             )
# #             response = chat.send_message(prompt)
# #             final_response_text = response.text.strip()
# #         else:  # Fallback to general inquiry if no direct dataset response or medium/low confidence handled above
# #             prompt = (
# #                 f"L'utilisateur a posé la question suivante en {user_language_to_full_name(user_language)} : '{text}'. "
# #                 f"Veuillez répondre en tant qu'assistant virtuel utile pour 'BCB EasyBank'. "
# #                 f"Assurez-vous que la réponse est UNIQUEMENT en {user_language_to_full_name(user_language)}. "
# #                 f"Évitez les traductions entre parenthèses. Si vous n'avez pas d'informations spécifiques, "
# #                 f"proposez de rediriger l'utilisateur vers des ressources pertinentes ou un agent humain."
# #             )
# #             response = chat.send_message(prompt)
# #             final_response_text = response.text.strip()

# #         chat_context["last_intent"] = intent_name
# #         chat_context["last_service_key"] = service_key_for_response

# #         return final_response_text

# #     except Exception as e:
# #         chat_context["last_intent"] = None
# #         chat_context["last_service_key"] = None
# #         # Provide a user-friendly error message
# #         return "Je suis désolé, une erreur inattendue s'est produite. Veuillez réessayer plus tard ou contacter le support technique."


# # def user_language_to_full_name(lang_code):
# #     """Helper function to convert language code to full name for prompts."""
# #     if lang_code == "fr":
# #         return "français"
# #     elif lang_code == "rn":
# #         return "kirundi"
# #     elif lang_code == "en":
# #         return "anglais"
# #     return "français"


# # views.py (Pas de changements majeurs nécessaires, car la logique est dans bcbai.py)
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# import json
# import os
# from django.conf import settings
# from .bcbai import (
#     send_message,
#     get_chat,
#     load_json_dataset,  # load_json_dataset est appelé au démarrage de bcbai
#     ALL_SERVICE_NAMES,  # Importer pour ServiceListView
# )


# class ChatMessageView(APIView):
#     def post(self, request):
#         question = request.data.get("question")
#         if not question:
#             return Response(
#                 {"error": "Question is required"}, status=status.HTTP_400_BAD_REQUEST
#             )

#         session_key = request.session.session_key
#         if not session_key:
#             request.session.create()
#             session_key = request.session.session_key

#         try:
#             answer = send_message(question, session_key)
#             return Response({"reply": answer})
#         except Exception as e:
#             # Log the full exception for debugging in production
#             print(f"Error in ChatMessageView: {e}")
#             return Response(
#                 {"error": f"Erreur lors du traitement de la question : {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )


# class ServiceListView(APIView):
#     def get(self, request):
#         try:
#             # Utiliser la variable globale ALL_SERVICE_NAMES qui est chargée une seule fois
#             # Assurez-vous que load_json_dataset() a été appelé au moins une fois
#             if not ALL_SERVICE_NAMES:
#                 load_json_dataset()  # Fallback, devrait être chargé au démarrage

#             services_list = []
#             for service_info in ALL_SERVICE_NAMES:
#                 # Retourner les noms dans toutes les langues disponibles pour la liste
#                 services_list.append(
#                     {
#                         "key": service_info["key"],
#                         "name_fr": service_info.get("fr", ""),
#                         "name_rn": service_info.get("rn", ""),
#                         "name_en": service_info.get("en", ""),
#                     }
#                 )
#             return Response(services_list, status=status.HTTP_200_OK)
#         except Exception as e:
#             print(f"Error in ServiceListView: {e}")
#             return Response(
#                 {"error": f"Erreur lors de la récupération des services : {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )
