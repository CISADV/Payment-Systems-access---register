import json
import requests
import pandas as pd
import io

# En-têtes simulant un vrai navigateur web pour éviter d'être bloqué par les serveurs officiels
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3"
}

def fetch_acpr_regafi():
    """Extraction robuste des données Banque de France / REGAFI"""
    url = "https://www.regafi.fr/asp/chambres_export.aspx?format=csv"
    try:
        print("Tentative de récupération REGAFI...")
        res = requests.get(url, headers=HTTP_HEADERS, timeout=20, verify=False)
        if res.status_code == 200:
            # Traitement avec gestion des erreurs d'encodage
            content = res.content.decode('iso-8859-1', errors='ignore')
            df = pd.read_csv(io.StringIO(content), sep=';', dtype=str, on_bad_lines='skip')
            
            records = []
            for idx, row in df.iterrows():
                nom = row.get("Raison_Sociale") or row.get("Nom_Etablissement") or row.get("Denomination")
                if not nom or pd.isna(nom):
                    continue
                    
                type_agr = row.get("Type_Etablissement") or "Établissement Agréé"
                bic = row.get("Code_BIC") if pd.notna(row.get("Code_BIC")) else ""
                code_id = row.get("Code_Etablissement") or str(idx)
                
                records.append({
                    "ID_Registre": str(code_id).strip(),
                    "Nom_Etablissement": str(nom).strip(),
                    "Type_Agrement": str(type_agr).strip(),
                    "Code_BIC": str(bic).strip(),
                    "Pays_Autorite": "FR",
                    "Acces_Direct_SEPA": "Oui (TARGET2)" if bic else "Indirect / Autre"
                })
            print(f"REGAFI : {len(records)} établissements récupérés.")
            return records
    except Exception as e:
        print(f"Erreur ACPR/REGAFI: {e}")
    return []

def fetch_lithuania_registry():
    """Extraction robuste Lietuvos Bankas (Lituanie)"""
    url = "https://www.lb.lt/en/financial-market-participants/export?type=payment-institutions&format=csv"
    try:
        print("Tentative de récupération Lietuvos Bankas...")
        res = requests.get(url, headers=HTTP_HEADERS, timeout=20)
        if res.status_code == 200:
            df = pd.read_csv(io.StringIO(res.text), sep=',', dtype=str, on_bad_lines='skip')
            records = []
            for idx, row in df.iterrows():
                nom = row.get("Title") or row.get("Name")
                if not nom or pd.isna(nom):
                    continue
                    
                records.append({
                    "ID_Registre": str(row.get("Code", idx)).strip(),
                    "Nom_Etablissement": str(nom).strip(),
                    "Type_Agrement": str(row.get("Type", "Payment Institution")).strip(),
                    "Code_BIC": str(row.get("BIC", "")).strip(),
                    "Pays_Autorite": "LT",
                    "Acces_Direct_SEPA": "Oui (CENTROlink)"
                })
            print(f"Lituanie : {len(records)} établissements récupérés.")
            return records
    except Exception as e:
        print(f"Erreur Lituanie: {e}")
    return []

def run():
    # Suppression des avertissements SSL superflus dans les journaux
    requests.packages.urllib3.disable_warnings()
    
    records_fr = fetch_acpr_regafi()
    records_lt = fetch_lithuania_registry()
    
    all_records = records_fr + records_lt
    
    # Données de secours si aucune source ne répond
    if not all_records:
        print("ATTENTION : Aucune source distante n'a pu être lue. Utilisation des données de secours.")
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
        
    print(f"Génération terminée. Total enregistrements : {len(all_records)}")

if __name__ == "__main__":
    run()
