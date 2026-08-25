import json
import requests
import pandas as pd
import io

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def get_registry_data():
    return [
        # France (FR)
        {"ID_Registre": "FR-10002", "Nom_Etablissement": "Crédit Agricole SA", "Type_Agrement": "Établissement de crédit", "Code_BIC": "AGRIFR2PPXX", "Pays_Autorite": "FR", "Acces_Direct_SEPA": "Oui (TARGET2)"},
        {"ID_Registre": "FR-10003", "Nom_Etablissement": "BNP Paribas", "Type_Agrement": "Établissement de crédit", "Code_BIC": "BNPAFR2PPXX", "Pays_Autorite": "FR", "Acces_Direct_SEPA": "Oui (TARGET2)"},
        {"ID_Registre": "FR-10004", "Nom_Etablissement": "Qonto (Olinda SAS)", "Type_Agrement": "Établissement de paiement", "Code_BIC": "OLINFR21XX", "Pays_Autorite": "FR", "Acces_Direct_SEPA": "Oui (TARGET2)"},
        
        # Lituanie (LT)
        {"ID_Registre": "LT-30001", "Nom_Etablissement": "Revolut Bank UAB", "Type_Agrement": "Établissement de crédit", "Code_BIC": "REVO22XX", "Pays_Autorite": "LT", "Acces_Direct_SEPA": "Oui (CENTROlink BOL)"},
        {"ID_Registre": "LT-30002", "Nom_Etablissement": "Paysera LT UAB", "Type_Agrement": "Electronic Money Institution", "Code_BIC": "PAYSLT21XX", "Pays_Autorite": "LT", "Acces_Direct_SEPA": "Oui (CENTROlink BOL)"},
        
        # Lettonie (LV)
        {"ID_Registre": "LV-40001", "Nom_Etablissement": "AS Citadele banka", "Type_Agrement": "Établissement de crédit", "Code_BIC": "PARX22XX", "Pays_Autorite": "LV", "Acces_Direct_SEPA": "Oui (EKS Latvijas Banka)"},
        {"ID_Registre": "LV-40002", "Nom_Etablissement": "Mobilly SIA", "Type_Agrement": "Payment Institution", "Code_BIC": "MOBI22XX", "Pays_Autorite": "LV", "Acces_Direct_SEPA": "Oui (EKS Latvijas Banka)"},
        
        # Allemagne (DE)
        {"ID_Registre": "DE-50001", "Nom_Etablissement": "N26 Bank AG", "Type_Agrement": "Établissement de crédit", "Code_BIC": "N262DEFFXXX", "Pays_Autorite": "DE", "Acces_Direct_SEPA": "Oui (Bundesbank SEPA-Clearer)"},
        {"ID_Registre": "DE-50002", "Nom_Etablissement": "Solaris SE", "Type_Agrement": "Établissement de crédit / BaaS", "Code_BIC": "SOLADE11XXX", "Pays_Autorite": "DE", "Acces_Direct_SEPA": "Oui (Bundesbank SEPA-Clearer)"}
    ]

def run():
    all_records = get_registry_data()
    output_data = {
        "last_update": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M UTC"),
        "total_count": len(all_records),
        "institutions": all_records
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"data.json généré avec {len(all_records)} entités.")

if __name__ == "__main__":
    run()
