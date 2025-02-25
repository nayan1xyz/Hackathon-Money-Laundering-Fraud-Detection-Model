from flask import Flask, request, jsonify
import joblib
import numpy as np
import xml.etree.ElementTree as ET  # NEW: Import for XML parsing
import tensorflow as tf  # NEW: Import TensorFlow for loading the Keras model

# Load the deep learning model using TensorFlow's Keras API.
model = tf.keras.models.load_model("deep_fraud_model.h5")
scaler = joblib.load("scaler.pkl")

app = Flask(__name__)

def extract_features(transaction):
    transaction_amount = float(transaction["PmtInf"]["CdtTrfTxInf"]["Amt"]["InstdAmt"])
    high_risk_country = 1 if transaction["PmtInf"]["DbtrAcct"]["Id"]["IBAN"].startswith(("NG", "IR", "SY")) else 0
    sanctioned_entity = 1 if transaction["PmtInf"]["Dbtr"]["Id"] in ["BlacklistedID1", "BlacklistedID2"] else 0
    regulatory_code = 1 if transaction["PmtInf"]["CdtTrfTxInf"]["RgltryRptg"]["Cd"] == "AML" else 0
    amount_risk = 1 if transaction_amount > 5000 else 0

    features = np.array([
        transaction_amount,
        high_risk_country,
        sanctioned_entity,
        regulatory_code,
        amount_risk
    ]).reshape(1, -1)
    
    features_scaled = scaler.transform(features)
    return features_scaled

def parse_iso20022_xml(xml_string):
    root = ET.fromstring(xml_string)
    transaction = {}
    grp_hdr = root.find('.//GrpHdr')
    transaction["GrpHdr"] = {
        "MsgId": grp_hdr.findtext("MsgId"),
        "CreDtTm": grp_hdr.findtext("CreDtTm"),
        "NbOfTxs": grp_hdr.findtext("NbOfTxs")
    }
    
    pmt_inf = root.find('.//PmtInf')
    debtor = pmt_inf.find('.//Dbtr')
    debtor_name = debtor.findtext("Nm")
    debtor_id = debtor.findtext("Id")
    
    debtor_acct = pmt_inf.find('.//DbtrAcct')
    debtor_iban = debtor_acct.find('.//IBAN').text if debtor_acct.find('.//IBAN') is not None else ""
    
    cdt_trf_tx_inf = pmt_inf.find('.//CdtTrfTxInf')
    amt_node = cdt_trf_tx_inf.find('.//Amt')
    instd_amt = amt_node.findtext("InstdAmt")
    currency = amt_node.attrib.get("Ccy", "")
    
    creditor = pmt_inf.find('.//Cdtr')
    creditor_name = creditor.findtext("Nm")
    creditor_id = creditor.findtext("Id")
    
    creditor_acct = pmt_inf.find('.//CdtrAcct')
    creditor_iban = creditor_acct.find('.//IBAN').text if creditor_acct.find('.//IBAN') is not None else ""
    
    rgltry_rptg = cdt_trf_tx_inf.find('.//RgltryRptg')
    regulatory_code = rgltry_rptg.findtext("Cd") if rgltry_rptg is not None else ""
    
    transaction["PmtInf"] = {
        "PmtMtd": pmt_inf.findtext("PmtMtd"),
        "Dbtr": {
            "Nm": debtor_name,
            "Id": debtor_id
        },
        "DbtrAcct": {
            "Id": {
                "IBAN": debtor_iban
            }
        },
        "CdtTrfTxInf": {
            "Amt": {
                "InstdAmt": instd_amt,
                "Ccy": currency
            },
            "Cdtr": {
                "Nm": creditor_name,
                "Id": creditor_id
            },
            "CdtrAcct": {
                "Id": {
                    "IBAN": creditor_iban
                }
            },
            "RgltryRptg": {
                "Cd": regulatory_code
            }
        }
    }
    transaction["fraud"] = 0  # Default label if not provided.
    return transaction

@app.route("/predict", methods=["POST"])
def predict():
    try:
        content_type = request.headers.get('Content-Type')
        if content_type and 'application/xml' in content_type:
            xml_data = request.data.decode('utf-8')
            transaction_data = parse_iso20022_xml(xml_data)
        else:
            transaction_data = request.get_json()
        
        features = extract_features(transaction_data)
        
        # Use model.predict() to get the probability for fraud.
        probabilities = model.predict(features)
        # For a sigmoid output, model.predict returns probability of fraud.
        risk_score = probabilities[0][0] * 100  # Convert probability to percentage
        
        # Binary prediction: 1 if probability >= 0.5 else 0.
        prediction = 1 if probabilities[0][0] >= 0.5 else 0
        
        response = {
            "fraud_detected": bool(prediction),
            "risk_score": f"{risk_score:.1f}%",
            "message": "⚠️ Suspicious transaction detected!" if prediction else "✅ Transaction is safe"
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)
