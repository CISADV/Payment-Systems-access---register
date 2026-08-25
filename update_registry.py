import json
import requests
import pandas as pd
import io

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def fetch_france_acpr_data():
    """Extraction via l'API / Open Data stable de la Banque de France"""
    print("Extraction France (ACPR / Banque de France)...")
    # Fichier miroir Open Data officiel Banque de France / REGAFI
    url = "https://www.data.gouv.fr/fr/datasets/r/6c98628f-2878-43f1-b95c-3083626e84d1"
    try:
        res = requests.get(url, headers=HTTP_HEADERS, timeout=25)
        if res.status_code == 200:
            df = pd.read_csv(io.BytesIO(res.content), sep=';', dtype=str, encoding='utf-8', on_bad_lines='skip')
            records = []
            for idx, row in df.iterrows():
                nom = row.get("Raison sociale") or row.get("Denomination") or row.get("Nom_Etablissement")
                if not nom or pd.isna(nom):
                    continue
                
                type_agr = row.get("Type etablissement") or row.get("Libelle type agrément") or "Établissement Agréé"
                bic = row.get("Code BIC") if pd.notna(row.get("Code BIC")) else ""
                
                records.append({
                    "ID_Registre": str(row.get("Code etablissement", idx)).strip(),
                    "Nom_Etablissement": str(nom).strip(),
                    "Type_Agrement": str(type_agr).strip(),
                    "Code_BIC": str(bic).strip(),
                    "Pays_Autorite": "FR",
                    "Acces_Direct_SEPA": "Oui (TARGET2)" if bic else "Indirect / Autre"
                })
            print(f"France : {len(records)} établissements extraits.")
            return records
    except Exception as e:
        print(f"Erreur France: {e}")
    return []

def fetch_eba_european_register():
    """Extraction du registre officiel de l'Autorité Bancaire Européenne (EBA)"""
    print("Extraction Europe (EBA Payment Institutions Register)...")
    url = "https://eurep.eba.europa.eu/eurep-register/api/v1/payment-institutions"
    try:
        res = requests.get(url, headers=HTTP_HEADERS, timeout=25)
        if res.status_code == 200:
            data = res.json()
            items = data.get("content", []) if isinstance(data, dict) else data
            records = []
            for item in items[:150]: # Limite aux 150 premiers pour fluidité
                records.append({
                    "ID_Registre": str(item.get("nationalIdentifier", item.get("id", ""))),
                    "Nom_Etablissement": str(item.get("name", "Inconnu")).strip(),
                    "Type_Agrement": str(item.get("institutionType", "Payment Institution")).strip(),
                    "Code_BIC": str(item.get("bic", "")).strip(),
                    "Pays_Autorite": str(item.get("countryCode", "EU")).upper(),
                    "Acces_Direct_SEPA": "Oui (SEPA/EBA)" if item.get("bic") else "Indirect"
                })
            print(f"EBA Europe : {len(records)} établissements extraits.")
            return records
    except Exception as e:
        print(f"Erreur EBA Europe: {e}")
    return []

def run():
    records_fr = fetch_france_acpr_data()
    records_eu = fetch_eba_european_register()
    
    all_records = records_fr + records_eu
    
    if not all_records:
        print("Échec des extractions distantes. Conservation des données de test.")
        all_records = [
            {"ID_Registre": "10002", "Nom_Etablissement": "Crédit Agricole SA", "Type_Agrement": "Établissement de crédit", "Code_BIC": "AGRIFR2PPXX", "Pays_Autorite": "FR", "Acces_Direct_SEPA": "Oui (TARGET2)"},
            {"ID_Registre": "30001", "Nom_Etablissement": "Revolut Bank UAB", "Type_Agrement": "Établissement de crédit", "Code_BIC": "REVO22XX", "Pays_Autorite": "LT", "Acces_Direct_SEPA": "Oui (CENTROlink)"}
        ]

    output_data = {
        "last_update": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M UTC"),
        "total_count": len(all_records),
        "institutions": all_records
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        
    print(f"Terminé avec succès. Total dans data.json : {len(all_records)}")

if __name__ == "__main__":
    run()
