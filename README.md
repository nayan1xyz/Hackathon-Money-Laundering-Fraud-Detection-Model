# Fraud Detection API

## Library Requirements
To install the necessary dependencies, run the following command:

```sh
pip install flask scikit-learn pandas joblib tensorflow keras_tuner

# API Testing Guide

## Overview
This guide provides instructions for testing the fraud detection API using both JSON and XML request formats.

## API Endpoint
**POST** `http://127.0.0.1:5000/predict`

## Request Headers
- `Content-Type: application/json` (for JSON requests)
- `Content-Type: application/xml` (for XML requests)

---

## JSON Request Example
Send a `POST` request with a JSON body as shown below:

```json
{
  "GrpHdr": {
    "MsgId": "TEST123",
    "CreDtTm": "2025-03-10T10:00:00Z",
    "NbOfTxs": "1"
  },
  "PmtInf": {
    "PmtMtd": "TRF",
    "Dbtr": {
      "Nm": "Fraudster Inc",
      "Id": "BlacklistedID1"
    },
    "DbtrAcct": {
      "Id": {
        "IBAN": "IR123456789012345678"
      }
    },
    "CdtTrfTxInf": {
      "Amt": {
        "InstdAmt": "10000.00",
        "Ccy": "USD"
      },
      "Cdtr": {
        "Nm": "Alice Smith",
        "Id": "654321987"
      },
      "CdtrAcct": {
        "Id": {
          "IBAN": "US987654321098765432"
        }
      },
      "RgltryRptg": {
        "Cd": "AML"
      }
    }
  },
  "fraud": 1
}

## XML Request Example
Send a `POST` request with an XML body as shown below:

```xml
<Document>
    <GrpHdr>
        <MsgId>TEST123</MsgId>
        <CreDtTm>2025-03-10T10:00:00Z</CreDtTm>
        <NbOfTxs>1</NbOfTxs>
    </GrpHdr>
    <PmtInf>
        <PmtMtd>TRF</PmtMtd>
        <Dbtr>
            <Nm>Fraudster Inc</Nm>
            <Id>BlacklistedID1</Id>
        </Dbtr>
        <DbtrAcct>
            <Id>
                <IBAN>IR123456789012345678</IBAN>
            </Id>
        </DbtrAcct>
        <CdtTrfTxInf>
            <Amt Ccy="USD">
                <InstdAmt>10000.00</InstdAmt>
            </Amt>
            <Cdtr>
                <Nm>Alice Smith</Nm>
                <Id>654321987</Id>
            </Cdtr>
            <CdtrAcct>
                <Id>
                    <IBAN>US987654321098765432</IBAN>
                </Id>
            </CdtrAcct>
            <RgltryRptg>
                <Cd>AML</Cd>
            </RgltryRptg>
        </CdtTrfTxInf>
    </PmtInf>
</Document>


## Expected Response

### Suspicious Transaction
```json
{
  "fraud_detected": true,
  "risk_score": "85.0%",
  "message": "⚠️ Suspicious transaction detected!"
}

### Safe Transaction
```json
{
  "fraud_detected": false,
  "risk_score": "12.3%",
  "message": "✅ Transaction is safe"
}

How to Test
Use Postman, cURL, or any API testing tool.
Set the request method to POST.
Provide the appropriate request header (Content-Type: application/json or Content-Type: application/xml).
Copy and paste the JSON or XML request body.
Send the request and check the response.

Notes
Ensure the API server is running at http://127.0.0.1:5000.
Modify values in the request to test different scenarios.
Use JSON format for easier readability and debugging.
