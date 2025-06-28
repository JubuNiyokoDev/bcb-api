import os
import json
from difflib import get_close_matches
from django.conf import settings
import google.generativeai as client

# Configure Gemini client
client.configure(api_key=settings.GOOGLE_API_KEY)
model = client.GenerativeModel("gemini-2.0-flash")

# Session chat memory
session_chats = {}  # {session_key: chat}


def load_json_dataset():
    json_path = os.path.join(settings.BASE_DIR, "bcb_dataset.json")
    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)


def find_intent(text):
    """
    Identifies the most likely intent and extracts relevant entities (like service name)
    based on the user's input.
    """
    dataset = load_json_dataset()
    intents = dataset.get("intents", [])

    # First, try to find a direct match for general greetings/thanks
    # This avoids unnecessary processing for simple conversational cues
    for intent_data in intents:
        if intent_data["intent_name"] == "support_general":
            for phrase in intent_data["training_phrases"]:
                # Lower cutoff for flexible matching, higher for exact greetings
                if get_close_matches(text.lower(), [phrase.lower()], n=1, cutoff=0.8):
                    if "bonjour" in text.lower() or "salut" in text.lower():
                        return "support_general", "greeting", None
                    elif "merci" in text.lower() or "grâce" in text.lower():
                        return "support_general", "thanks", None

    # Iterate through all training phrases of all intents to find the best match
    best_match_score = 0.6  # Lower cutoff for broader matching
    matched_intent_name = None
    matched_service_name = None  # To store extracted service name

    # Get a list of all possible service names for entity extraction
    all_service_names = []
    if (
        intents and "responses" in intents[0]
    ):  # Assuming 'informations_service' is likely the first intent
        for service_key in intents[0]["responses"].keys():
            all_service_names.append(service_key.lower())

    for intent_data in intents:
        # Prioritize specific service-related intents first if they match strongly
        # This part of the logic needs to be more robust for entity extraction.
        # Let's simplify and rely more on general phrase matching for intent,
        # then extract service_key if present in the text.

        # Check for service name presence in the user's text for any intent
        current_service_key = None
        for s_name in all_service_names:
            if s_name in text.lower():
                current_service_key = s_name.replace(
                    " ", "_"
                ).title()  # Convert "compte individuel" to "Compte_Individuel"
                if (
                    "_" in current_service_key
                ):  # If multi-word, convert to exact key "Compte Individuel"
                    current_service_key = current_service_key.replace("_", " ")
                break

        for phrase in intent_data["training_phrases"]:
            # Replace placeholder for better matching if it's a specific service question
            temp_phrase = phrase
            if "{service_name_fr}" in temp_phrase:
                # Use a generic term for matching to find the intent
                temp_phrase = temp_phrase.replace(
                    "{service_name_fr}", "un service bancaire"
                )  # Or just "" if it makes sense

            matches = get_close_matches(
                text.lower(), [temp_phrase.lower()], n=1, cutoff=best_match_score
            )
            if matches:
                return (
                    intent_data["intent_name"],
                    current_service_key,
                    None,
                )  # Return intent and any found service key

    # Fallback if no specific intent is found
    return "general_inquiry", None, None  # Default to general inquiry


def get_response_for_intent(intent_name, service_key, lang, dataset):
    """
    Retrieves the specific response for a given intent, service, and language.
    Handles 'default' and 'steps' responses within intents.
    """
    for intent_data in dataset["intents"]:
        if intent_data["intent_name"] == intent_name:
            responses = intent_data["responses"]

            if intent_name == "processus_ouverture_compte":
                default_response = responses.get("default", {}).get(lang, "")
                steps_response = responses.get("steps", [])

                # Replace placeholder for service_name in the default response
                # Ensure the service_key is used consistently for replacement
                if service_key:
                    placeholder_fr = "{service_name_fr}"
                    placeholder_rn = "{service_name_rn}"
                    placeholder_en = "{service_name_en}"

                    # Find the actual service name from the dataset in the target language if service_key is not None
                    actual_service_name_in_lang = service_key  # Default to service_key
                    if (
                        intent_name == "informations_service"
                    ):  # Only for information_service intent's responses
                        for svc_intent in dataset["intents"]:
                            if svc_intent["intent_name"] == "informations_service":
                                if service_key in svc_intent["responses"]:
                                    actual_service_name_in_lang = svc_intent[
                                        "responses"
                                    ][service_key].get(lang, service_key)
                                    break

                    # Refine this logic to use the actual service name in the target language
                    # For `processus_ouverture_compte` we just need the service name in the target language
                    # We can fetch it from the 'informations_service' intent's responses
                    if service_key:
                        service_details_for_lang = None
                        for info_intent in dataset["intents"]:
                            if info_intent["intent_name"] == "informations_service":
                                service_details_for_lang = info_intent["responses"].get(
                                    service_key
                                )
                                break
                        if service_details_for_lang:
                            service_name_in_target_lang = service_details_for_lang.get(
                                lang, service_key
                            )  # Fallback to key
                            default_response = default_response.replace(
                                placeholder_fr, service_name_in_target_lang
                            )
                            default_response = default_response.replace(
                                placeholder_rn, service_name_in_target_lang
                            )
                            default_response = default_response.replace(
                                placeholder_en, service_name_in_target_lang
                            )
                        else:  # If service details not found, remove placeholder
                            default_response = (
                                default_response.replace(placeholder_fr, "")
                                .replace(placeholder_rn, "")
                                .replace(placeholder_en, "")
                            )

                full_response = default_response
                if steps_response:
                    for step in steps_response:
                        full_response += "\n" + step.get(lang, "")
                return full_response

            elif intent_name == "support_general" and service_key in responses:
                return responses[service_key].get(lang, "")

            elif service_key and service_key in responses:
                return responses[service_key].get(lang, "")
            elif "default" in responses:
                return responses["default"].get(lang, "")

    return None


def find_language(text, chat):
    """Detect language using Gemini."""
    # Instruct Gemini to respond ONLY with the language name
    prompt = f"What is the language of this sentence: '{text}'? Respond with only one word: 'French', 'English', or 'Kirundi'."
    try:
        language_response = chat.send_message(prompt).text.strip().lower()
        if "french" in language_response:
            return "fr"
        elif "kirundi" in language_response:
            return "rn"
        elif "english" in language_response:
            return "en"
        else:
            return "fr"  # Default to French if detection is ambiguous
    except Exception:
        return "fr"  # Default to French on error


def start_new_chat(session_key):
    """Start a new Gemini chat session."""
    chat = model.start_chat()
    session_chats[session_key] = chat
    return chat


def get_chat(session_key):
    """Retrieve or create chat for session."""
    return session_chats.get(session_key) or start_new_chat(session_key)


def send_message(text, session_key):
    """Main logic: find intent and respond based on dataset or Gemini's general knowledge."""
    chat = get_chat(session_key)
    dataset = load_json_dataset()

    try:
        user_language = find_language(text, chat)

        intent_name, service_key, _ = find_intent(text)

        dataset_response = get_response_for_intent(
            intent_name, service_key, user_language, dataset
        )

        # Craft the prompt to Gemini to ensure single-language and good formatting
        if dataset_response:
            prompt = (
                f"L'utilisateur a posé la question suivante en {user_language_to_full_name(user_language)} : '{text}'. "
                f"Voici la réponse de référence de notre base de données bancaire, déjà dans la langue de l'utilisateur : '{dataset_response}'. "
                f"Veuillez reformuler cette réponse de manière naturelle, utile et empathique, en tant qu'assistant virtuel pour 'BCB EasyBank'. "
                f"Assurez-vous que la réponse est UNIQUEMENT en {user_language_to_full_name(user_language)}. "
                f"Évitez les traductions entre parenthèses. Soyez concis et direct."
            )
        else:
            prompt = (
                f"L'utilisateur a posé la question suivante en {user_language_to_full_name(user_language)} : '{text}'. "
                f"Veuillez répondre en tant qu'assistant virtuel utile pour 'BCB EasyBank'. "
                f"Assurez-vous que la réponse est UNIQUEMENT en {user_language_to_full_name(user_language)}. "
                f"Évitez les traductions entre parenthèses. Si vous n'avez pas d'informations spécifiques, "
                f"proposez de rediriger l'utilisateur vers des ressources pertinentes ou un agent humain."
            )

        response = chat.send_message(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Erreur lors du traitement du message : {str(e)}"


def user_language_to_full_name(lang_code):
    """Helper function to convert language code to full name for prompts."""
    if lang_code == "fr":
        return "français"
    elif lang_code == "rn":
        return "kirundi"
    elif lang_code == "en":
        return "anglais"
    return "français"  # Default
