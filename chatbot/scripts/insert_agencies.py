# chatbot/scripts/insert_agencies.py

from chatbot.models import Agency

agencies_data = [
    {
        "name": "Agence Centrale",
        "latitude": -3.3731,
        "longitude": 29.3644,
        "address": "Avenue E.Patrice Lumumba, BP 300, Bujumbura",
    },
    {
        "name": "Agence Kayanza",
        "latitude": -2.9219,
        "longitude": 29.6294,
        "address": "Kayanza, Burundi",
    },
    {
        "name": "Agence Gitega",
        "latitude": -3.4271,
        "longitude": 29.9246,
        "address": "Gitega, Burundi",
    },
    {
        "name": "Agence Kirundo",
        "latitude": -2.5847,
        "longitude": 30.0978,
        "address": "Kirundo, Burundi",
    },
    {
        "name": "Agence Ruyigi",
        "latitude": -3.4764,
        "longitude": 30.2503,
        "address": "Ruyigi, Burundi",
    },
    {
        "name": "Agence Place de l'Indépendance",
        "latitude": -3.3761,
        "longitude": 29.3594,
        "address": "Place de l'Indépendance, Bujumbura",
    },
    {
        "name": "Agence Kinanira",
        "latitude": -3.3831,
        "longitude": 29.3744,
        "address": "Kinanira, Bujumbura",
    },
    {
        "name": "Agence Centenaire",
        "latitude": -3.3631,
        "longitude": 29.3544,
        "address": "Centenaire, Bujumbura",
    },
    {
        "name": "Agence Karusi",
        "latitude": -3.1011,
        "longitude": 30.1608,
        "address": "Karusi, Burundi",
    },
    {
        "name": "Agence Umugenzi",
        "latitude": -3.3931,
        "longitude": 29.3844,
        "address": "Umugenzi, Bujumbura",
    },
    {
        "name": "Agence Centre d'Affaires",
        "latitude": -3.3531,
        "longitude": 29.3444,
        "address": "Centre d'Affaires, Bujumbura",
    },
    {
        "name": "Agence 1er Juillet",
        "latitude": -3.3431,
        "longitude": 29.3344,
        "address": "1er Juillet, Bujumbura",
    },
    {
        "name": "Agence Kirumara",
        "latitude": -3.4031,
        "longitude": 29.3944,
        "address": "Kirumara, Bujumbura",
    },
    {
        "name": "Agence Ngozi",
        "latitude": -2.9081,
        "longitude": 29.8306,
        "address": "Ngozi, Burundi",
    },
    {
        "name": "Agence Rumonge",
        "latitude": -3.9733,
        "longitude": 29.4386,
        "address": "Rumonge, Burundi",
    },
    {
        "name": "Agence Muyinga",
        "latitude": -2.8444,
        "longitude": 30.3419,
        "address": "Muyinga, Burundi",
    },
    {
        "name": "Agence Orée du Golf",
        "latitude": -3.3331,
        "longitude": 29.3244,
        "address": "Orée du Golf, Bujumbura",
    },
    {
        "name": "Agence Rugombo",
        "latitude": -2.7833,
        "longitude": 29.4167,
        "address": "Rugombo, Burundi",
    },
    {
        "name": "Agence Buyenzi",
        "latitude": -3.3231,
        "longitude": 29.3144,
        "address": "Buyenzi, Bujumbura",
    },
    {
        "name": "Agence Nyanza-Lac",
        "latitude": -4.2167,
        "longitude": 29.7500,
        "address": "Nyanza-Lac, Burundi",
    },
    {
        "name": "Agence Rutana",
        "latitude": -3.9333,
        "longitude": 29.9833,
        "address": "Rutana, Burundi",
    },
    {
        "name": "Agence Makamba",
        "latitude": -4.1333,
        "longitude": 29.8000,
        "address": "Makamba, Burundi",
    },
    {
        "name": "Agence Kigobe",
        "latitude": -3.3131,
        "longitude": 29.3044,
        "address": "Kigobe, Bujumbura",
    },
    {
        "name": "Agence Kamenge",
        "latitude": -3.3031,
        "longitude": 29.2944,
        "address": "Kamenge, Bujumbura",
    },
    {
        "name": "Agence Gihofi",
        "latitude": -3.2931,
        "longitude": 29.2844,
        "address": "Gihofi, Bujumbura",
    },
    {
        "name": "Agence Amahoro",
        "latitude": -3.2831,
        "longitude": 29.2744,
        "address": "Amahoro, Bujumbura",
    },
]

for data in agencies_data:
    Agency.objects.get_or_create(
        name=data["name"],
        defaults={
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "address": data["address"],
        },
    )

print("✅ Toutes les agences ont été insérées avec succès.")
