import json
import os
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('fr_FR')

# 1. Création du dossier de réception des webhooks bruts (Landing Zone)
output_dir = "data/raw_webhooks"
os.makedirs(output_dir, exist_ok=True)

carriers = ["Chronopost", "Mondial Relay", "Colissimo", "DHL"]
promo_codes = ["WELCOME10", "SUMMER20", "VIP50", "", "   ", None]
tags_pool = ["fragile", "express", "eco_friendly", "heavy", "high_value"]

events = []

for order_id in range(1, 501):
    base_time = fake.date_time_between(start_date='-90d', end_date='-5d')
    event_id = f"EVT-{order_id:05d}"
    
    # Simulation d'un retard réseau (Late-arriving data sur 10% des événements)
    delay_days = random.choice([0, 0, 0, 0, 2, 5])
    ingested_at = base_time + timedelta(days=delay_days, minutes=random.randint(1, 120))

    # Structure JSON complexe (Nested JSON + Arrays + Dirty Data sur promo_code)
    event = {
        "event_id": event_id,
        "order_id": order_id,
        "carrier": random.choice(carriers),
        "promo_code": random.choice(promo_codes), # Contient des "", "   " et None !
        "shipping_cost_raw": f"{round(random.uniform(3.99, 19.99), 2)} EUR", # Texte à nettoyer avec Regex/CAST !
        "package_tags": random.sample(tags_pool, k=random.randint(1, 3)), # Array à aplatir avec UNNEST !
        "checkpoints": [ # JSON imbriqué pour notre futur PIVOT SQL !
            {"step": "CREATED", "timestamp": base_time.isoformat()},
            {"step": "PACKED", "timestamp": (base_time + timedelta(hours=random.randint(2, 12))).isoformat()},
            {"step": "SHIPPED", "timestamp": (base_time + timedelta(hours=random.randint(13, 36))).isoformat()},
            {"step": "DELIVERED", "timestamp": (base_time + timedelta(hours=random.randint(37, 96))).isoformat()}
        ],
        "ingested_at": ingested_at.isoformat()
    }
    events.append(event)

    # 2. ANOMALIE 1 : Injection de DOUBLONS réseau (sur 8% des événements)
    if random.random() < 0.08:
        duplicate_event = event.copy()
        # Le doublon arrive quelques secondes plus tard sur le serveur
        duplicate_event["ingested_at"] = (ingested_at + timedelta(seconds=random.randint(5, 60))).isoformat()
        events.append(duplicate_event)

# 3. ANOMALIE 2 : Injection de DONNÉES CORROMPUES (pour tester notre futur contrat Pydantic !)
corrupted_event = {
    "event_id": "EVT-99999",
    "order_id": "ID_INVALIDE", # <- Devrait être un int !
    "carrier": "Transporteur Fantôme",
    "promo_code": None,
    "shipping_cost_raw": "GRATUIT",
    "package_tags": [],
    "checkpoints": [],
    "ingested_at": datetime.now().isoformat()
}
events.append(corrupted_event)

# On mélange la liste pour simuler l'arrivée désordonnée des fichiers
random.shuffle(events)

# 4. Écriture du fichier JSON (format JSON Lines : 1 événement JSON par ligne, le standard Data Lake)
output_file = os.path.join(output_dir, "logistics_events.jsonl")
with open(output_file, "w", encoding="utf-8") as f:
    for e in events:
        f.write(f"{json.dumps(e)}\n")
        

print(f" {len(events)} événements Webhooks générés dans {output_file} (incluant doublons et anomalies) !")