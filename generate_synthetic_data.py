import random
import json
import datetime
import uuid

def generate_random_transaction(is_fraud):
    if is_fraud:
        debtor_id = random.choice(["BlacklistedID1", "BlacklistedID2"])
        iban_prefix = random.choice(["NG", "IR", "SY"])
    else:
        debtor_id = str(random.randint(100000000, 999999999))
        iban_prefix = random.choice(["DE", "FR", "US", "GB", "NL"])
    
    debtor_iban = iban_prefix + "".join([str(random.randint(0, 9)) for _ in range(18)])
    creditor_id = str(random.randint(100000000, 999999999))
    creditor_iban = random.choice(["DE", "FR", "US", "GB", "NL"]) + "".join([str(random.randint(0, 9)) for _ in range(18)])
    
    if is_fraud:
        amount = round(random.uniform(5000, 1000000), 2)
    else:
        amount = round(random.uniform(10, 5000), 2)
    
    currency = random.choice(["USD", "EUR", "GBP"])
    regulatory_code = "AML" if is_fraud else "NML"
    
    transaction = {
        "GrpHdr": {
            "MsgId": str(uuid.uuid4()),
            "CreDtTm": datetime.datetime.now().isoformat() + "Z",
            "NbOfTxs": "1"
        },
        "PmtInf": {
            "PmtMtd": "TRF",
            "Dbtr": {
                "Nm": "John Doe" if not is_fraud else "Fraudster Inc",
                "Id": debtor_id
            },
            "DbtrAcct": {
                "Id": {
                    "IBAN": debtor_iban
                }
            },
            "CdtTrfTxInf": {
                "Amt": {
                    "InstdAmt": str(amount),
                    "Ccy": currency
                },
                "Cdtr": {
                    "Nm": "Alice Smith",
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
        },
        "fraud": 1 if is_fraud else 0
    }
    return transaction

transactions = []
num_transactions = 100

for _ in range(num_transactions):
    is_fraud = random.random() < 0.3
    transactions.append(generate_random_transaction(is_fraud))

with open("transactions.json", "w") as file:
    json.dump(transactions, file, indent=2)

print("✅ Generated synthetic transactions in transactions.json")
