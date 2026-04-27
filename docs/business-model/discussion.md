# Business Model Discussion

## Hotel Tech Stack

```mermaid
flowchart TD

    subgraph Channels["Buchungskanäle"]
        OTA["🌐 Buchungsportale\nBooking.com · Expedia · HRS"]
        Agency["📧 Reiseveranstalter\nDERTOUR · HTH · Wörlitz Tourist"]
        Direct["🏨 Direktbuchung\nWebsite · Telefon · Walk-in"]
        Corporate["🏢 Firmenkunden\nSekretärinnen mit/ohne Rahmenvertrag"]
        Extranet["📋 Extranet-Portale\nAKON u.a. (manuell geprüft)"]
    end

    subgraph Middleware["Middleware"]
        CM["Channel Manager\nVerfügbarkeit & Raten-Sync"]
        Email["📬 E-Mail-Postfach\n(manuell bearbeitet)"]
    end

    subgraph Core["Kernsystem"]
        PMS["PMS\nMEWS · Oracle Opera\nReservierungen · Zimmer · Gäste"]
        ERP["ERP / Buchhaltung\nRechnungen · Zahlungen"]
    end

    OTA -->|API| CM
    CM -->|API| PMS
    Agency -->|E-Mail| Email
    Corporate -->|E-Mail / Telefon| Email
    Direct -->|API / manuell| PMS
    Extranet -->|manuell übertragen| PMS
    Email -->|manuell eingetragen| PMS
    PMS --- ERP
```

**Beobachtungen aus Interviews:**
- Der Channel Manager hat einen Timelag von 20–30 min → Überbuchungsrisiko
- Alles was nicht über den Channel Manager läuft, landet manuell im PMS
- Extranet-Portale (z.B. AKON) haben keine API — rein manueller Abgleich
- E-Mail ist der größte manuelle Kanal: Agenturen, Firmenkunden, Gästekommunikation
