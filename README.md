# Modern Laboratory Analyzer LIS Integrations

Welcome to the open-source community repository dedicated to documenting undocumented, modern **Web API (HTTP/JSON)** interfaces for laboratory analyzers. 

Historically, 95% of laboratory machines (such as the Erba Chem 7, Erba H360, and Biosystems BTS) rely on legacy RS-232 serial cables or raw TCP sockets using standards like ASTM or HL7. However, newer analyzers are quietly shipping with modern, built-in web servers and JSON APIs that completely change how Laboratory Information Systems (LIS) should integrate with them.

This repository serves as a guide for LIS developers to bypass legacy serial ports and integrate directly with modern analyzer APIs.

---

## Supported Analyzers

### 1. Horiba Yumizen CA60
The Yumizen CA60 is a semi-automated clinical chemistry analyzer. While it is marketed as "LIS Ready" via its Ethernet port, the exact protocol is rarely documented.

**Integration Type:** HTTP POST (Polling)  
**Data Format:** JSON  
**Default Port:** `8080`

#### How to Fetch Data
Unlike older machines that "push" data when a test finishes, the CA60 requires the LIS agent to periodically "pull" (poll) the data using an HTTP `POST` request to `/queries`.

**Endpoint:** `http://[DEVICE_IP]:8080/queries`  
**Headers:**
```http
Content-Type: application/json
Accept: application/json
```

**Payload (Fetch Last 24 Hours):**
```json
{
  "query": {
    "type": "GetHistoricalData",
    "payload": {
      "readingType": ["Sample"],
      "sampleId": null,
      "techniqueId": null,
      "startDate": null,
      "endDate": "2026-06-17T23:59:59.999+05:30",
      "timePeriod": "ONE_DAY"
    }
  }
}
```

**Payload (Fetch Specific Sample ID):**
```json
{
  "query": {
    "type": "GetHistoricalData",
    "payload": {
      "readingType": ["Sample"],
      "sampleId": "0009",
      "techniqueId": null,
      "startDate": null,
      "endDate": "2026-06-17T23:59:59.999+05:30",
      "timePeriod": "ONE_DAY"
    }
  }
}
```

#### JSON Response Parsing
The machine returns an array inside `historicalData`. The actual clinical result is deeply nested within the replicas array.

- **Patient/Sample ID:** `record.sampleId`
- **Test Name:** `record.techniqueName`
- **Final Result:** `record.measure.replicas[0].result`
- **Units:** `record.sampleUnits`

*(See the `scripts/horiba_poller.py` file in this repository for a complete working example).*

---

## Known Analyzers Using Legacy Protocols (Non-HTTP)

While visually modern, many analyzers still rely on proprietary serial protocols. These **cannot** be polled using JSON/HTTP and require traditional middleware or COM port listening.

### Biosystems BTS Series (BTS-350 / BTS-330)
Despite having an Ethernet port and a modern touchscreen, the Biosystems BTS series **does not** use a web-based API or JSON. 
- **Integration Type:** Master-Slave Serial/TCP Framing
- **How it works:** The analyzer requires a dedicated PC middleware to act as the "Master". The Master must send specific binary or text-based command frames to request data, and the analyzer responds with raw text strings (not JSON). 
- **Recommendation:** Do not attempt HTTP integration. You must use a traditional ASTM/HL7 bridge or the manufacturer's specific LIS serial drivers.

---

*Contributions are welcome! If you discover a hidden API on a medical device, please submit a Pull Request.*
