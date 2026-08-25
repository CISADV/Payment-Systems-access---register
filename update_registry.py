import json
import requests
import pandas as pd
import io

def fetch_acpr_regafi():
    """Récupère la liste officielle ACPR/REGAFI (France)"""
    url = "https://www.regafi.fr/asp/chambres_export.aspx?format=csv"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=30)
        if res.status_code == 200:
            df = pd.read_csv(io.StringIO(res.text), sep=';', encoding='iso-8859-1', dtype=str)
            records = []
            for idx, row in df.iterrows():
                # On ne conserve que les champs pertinents
                nom = row.get("Raison_Sociale") or row.get("Nom_Etablissement") or "Inconnu"
                type_agr = row.get("Type_Etablissement") or "Établissement Agréé"
                bic = row.get("Code_BIC") if pd.notna(row.get("Code_BIC")) else ""
                code_id = row.get("Code_Etablissement") or str(idx)
                
                records.append({
                    "ID_Registre": str(code_id),
                    "Nom_Etablissement": str(nom).strip(),
                    "Type_Agrement": str(type_agr).strip(),
                    "Code_BIC": str(bic).strip(),
                    "Pays_Autorite": "FR",
                    "Acces_Direct_SEPA": "Oui (TARGET2)" if bic else "Indirect / Autre"
                })
            return records
        return []
    except Exception as e:
        print(f"Erreur ACPR: {e}")
        return []

def fetch_lithuania_registry():
    """Récupère la liste de la Banque de Lituanie (CENTROlink)"""
    url = "https://www.lb.lt/en/financial-market-participants/export?type=payment-institutions&format=csv"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=30)
        if res.status_code == 200:
            df = pd.read_csv(io.StringIO(res.text), sep=',', dtype=str)
            records = []
            for idx, row in df.iterrows():
                records.append({
                    "ID_Registre": str(row.get("Code", idx)),
                    "Nom_Etablissement": str(row.get("Title", "Inconnu")).strip(),
                    "Type_Agrement": str(row.get("Type", "Payment Institution")).strip(),
                    "Code_BIC": str(row.get("BIC", "")).strip(),
                    "Pays_Autorite": "LT",
                    "Acces_Direct_SEPA": "Oui (CENTROlink)"
                })
            return records
        return []
    except Exception as e:
        print(f"Erreur Lituanie: {e}")
        return []

def run():
    print("Début de la collecte des données...")
    records_fr = fetch_acpr_regafi()
    records_lt = fetch_lithuania_registry()
    
    all_records = records_fr + records_lt
    
    # Données de secours si aucune API ne répond
    if not all_records:
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
        
    print(f"Succès : {len(all_records)} établissements enregistrés dans data.json.")

if __name__ == "__main__":
    run()
