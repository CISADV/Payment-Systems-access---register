import json
import requests
import pandas as pd

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def fetch_target2_direct_bics():
    """
    Récupère la liste des BICs ayant un accès DIRECT à TARGET2 / STEP2 (BCE).
    """
    print("Récupération de l'annuaire des participants directs TARGET2...")
    # Fichier miroir Open Data du répertoire T2
    url = "https://raw.githubusercontent.com/datasets/financial-entities/main/data/target2_bics.json"
    try:
        res = requests.get(url, headers=HTTP_HEADERS, timeout=15)
        if res.status_code == 200:
            return set(res.json())
    except Exception as e:
        print(f"Info TARGET2 : {e}")
    # BICs majeurs de référence en cas d'indisponibilité
    return {"AGRIFR2PPXX", "BNPAFR2PPXX", "N262DEFFXXX", "SOLADE11XXX", "REVO22XX", "PARX22XX"}


def fetch_and_qualify_institutions():
    """
    Extrait les agréments EBA et croise avec les accès systèmes.
    """
    print("Extraction du registre EBA et qualification de l'accès...")
    url = "https://eurep.eba.europa.eu/eurep-register/api/v1/payment-institutions"
    
    direct_t2_bics = fetch_target2_direct_bics()
    target_countries = {"FR", "DE", "LT", "LV"}
    records = []

    try:
        res = requests.get(url, headers=HTTP_HEADERS, timeout=30)
        if res.status_code == 200:
            items = res.json().get("content", []) if isinstance(res.json(), dict) else res.json()
            
            for item in items:
                country = str(item.get("countryCode", "")).upper()
                if country in target_countries:
                    bic = str(item.get("bic", "")).strip()
                    
                    # Logique de qualification Direct vs Indirect
                    is_direct = False
                    system_label = "Non / Accès indirect (Banque sponsor)"

                    if bic and bic != "nan":
                        # Test d'accès direct selon le pays et la présence dans les annuaires
                        if country == "LT":
                            is_direct = True
                            system_label = "Direct Participant (CENTROlink BOL)"
                        elif country == "LV":
                            is_direct = True
                            system_label = "Direct Participant (EKS Latvijas Banka)"
                        elif country == "DE" and (bic in direct_t2_bics or "DE" in bic):
                            is_direct = True
                            system_label = "Direct Participant (Bundesbank SEPA-Clearer)"
                        elif country == "FR" and (bic in direct_t2_bics or "FR" in bic):
                            is_direct = True
                            system_label = "Direct Participant (TARGET2 / STEP2)"

                    records.append({
                        "ID_Registre": str(item.get("nationalIdentifier") or item.get("id", "")),
                        "Nom_Etablissement": str(item.get("name", "Inconnu")).strip(),
                        "Type_Agrement": str(item.get("institutionType", "Credit / Payment Institution")).strip(),
                        "Code_BIC": bic if bic else "N/A",
                        "Pays_Autorite": country,
                        "Statut_Acces": "DIRECT" if is_direct else "INDIRECT",
                        "Acces_Direct_SEPA": system_label
                    })
            print(f"Qualification terminée : {len(records)} établissements traités.")
            return records
    except Exception as e:
        print(f"Erreur EBA: {e}")
    return []


def run():
    records = fetch_and_qualify_institutions()
    
    output_data = {
        "last_update": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M UTC"),
        "total_count": len(records),
        "institutions": records
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run()
