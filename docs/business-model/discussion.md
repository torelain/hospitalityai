# Business Model Discussion

## Hotel Tech Stack

Typischer Tech Stack eines Hotels — basierend auf Marktrecherche.

```mermaid
flowchart TD

    subgraph Channels["1 — Buchungskanäle"]
        OTA["🌐 OTAs\nBooking.com · Expedia · HRS"]
        GDS["🔗 GDS\nAmadeus · Sabre · Galileo"]
        Direct["🏨 Direktbuchung\nHotel-Website"]
        Corporate["🏢 Firmenkunden & Gruppen\nDirekt / E-Mail"]
    end

    subgraph Distribution["2 — Distribution"]
        BE["Booking Engine\nDirektbuchungs-Tool auf der Website"]
        CM["Channel Manager\nRaten & Verfügbarkeit zentral verwalten\nz.B. SiteMinder, Dirs21"]
        CRS["CRS\nCentral Reservation System"]
    end

    subgraph Revenue["3 — Revenue Management"]
        RMS["RMS\nDynamische Preisgestaltung\nz.B. RoomPriceGenie, IDeaS"]
    end

    subgraph Core["4 — Kernsystem"]
        PMS["PMS — Property Management System\nReservierungen · Zimmer · Gästeprofil\nHousekeeping · Check-in/out\nz.B. MEWS, Oracle Opera, Apaleo"]
    end

    subgraph GuestExp["5 — Gasterlebnis"]
        MSG["Gästekommunikation\nE-Mail · Chat · Messaging"]
        Checkin["Digitaler Check-in\nKiosk / Mobile"]
    end

    subgraph Finance["6 — Finance & Back-Office"]
        PAY["Zahlungsabwicklung\nKreditkarte · Online-Payment"]
        ERP["ERP / Buchhaltung\nRechnungen · Reporting"]
    end

    OTA --> CM
    GDS --> CRS
    Direct --> BE
    Corporate --> PMS

    BE --> PMS
    CM --> PMS
    CRS --> PMS
    RMS <--> PMS

    PMS --> MSG
    PMS --> Checkin
    PMS --> PAY
    PAY --> ERP
    PMS --> ERP
```

**Quellen:** [SiteMinder](https://www.siteminder.com/r/hotel-tech-stack/) · [Mews](https://www.mews.com/en/blog/hotel-tech-stack) · [Cloudbeds](https://www.cloudbeds.com/articles/hotel-tech-stack/) · [RoomPriceGenie](https://roompricegenie.com/essential-tech-trio-pms-channel-manager-rms/)
