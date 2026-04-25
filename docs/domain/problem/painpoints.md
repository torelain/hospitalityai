# Pain Points — Kundengespräche

Dieses Dokument sammelt Insights aus Kundengesprächen, Beobachtungen und Workshops.

---

## Hotels

| Hotel | Größe | Segment | PMS | Notizen |
|---|---|---|---|---|
| Santé Royale | ~400–500 Zimmer, 4 Standorte | Wellness & Gesundheit | MEWS | Interviewdatum: 25.04.2026 |
| Hotel Restaurant Fischer | ~50 Zimmer | — | Oracle | Hotel möchte Kontrolle behalten; nutzt Channel Manager; Interviewdatum: 25.04.2026 |

---

## Pain Points

| # | Pain Point | Kontext / Zitat | Hotel | Datum | Schweregrad |
|---|---|---|---|---|---|
| 1 | Einarbeitung dauert bis zu 3 Wochen; Fehler durch große Anzahl an Sonderregeln | Neue Mitarbeiter brauchen wochenlang bis zur Produktivität. Sonderregeln sind nicht zentral dokumentiert — Wissen steckt bei einzelnen Personen. | Santé Royale | 25.04.2026 | Hoch |
| 2 | MEWS weist Zimmer ohne Slot-Optimierung zu — freie Einzeltage werden verschwendet | MEWS nimmt bei eingehender Buchung immer das erste verfügbare Zimmer, das die Anforderungen erfüllt, ohne benachbarte Belegungslücken zu berücksichtigen. Beispiel: Ein Gast bucht 1 Nacht — MEWS weist das Zimmer mit 5 zusammenhängend freien Wochen zu statt das Zimmer mit nur 1 freien Tag. Damit blockiert eine 1-Nacht-Buchung einen langen zusammenhängenden Block und verhindert eine potenzielle Mehrwochen-Buchung. | Santé Royale | 25.04.2026 | Hoch |
| 3 | Keine Konsistenz beim Rechnungsversand an Reiseveranstalter | Manchmal werden Rechnungen über das System an Reiseveranstalter versendet, manchmal nicht. Es gibt keinen einheitlichen Prozess — abhängig von Mitarbeiter oder Situation. | Santé Royale | 25.04.2026 | Mittel |
| 4 | Manuelle Prüfung der AKON-Extranetseite auf neue oder geänderte Buchungen | Der Hotelmanager muss die Extranetseite von AKON manuell aufrufen und eigenständig prüfen, ob es neue Buchungen oder Änderungen gibt, und diese dann manuell ins PMS eintragen. Kein automatischer Datenabgleich. | Santé Royale | 25.04.2026 | Hoch |
| 5 | Stornierung ohne Rechnung führt zu nicht zuordenbarem Zahlungseingang in MEWS | Bei Stornierung löschen Mitarbeiter die Rechnungsstellung in MEWS und schicken stattdessen eine manuelle Zahlungsaufforderung. Da keine Rechnung erstellt wurde, wird auch kein Gast-Buchhaltungskonto in MEWS angelegt. Zahlt der Gast trotzdem, bucht MEWS den Eingang auf ein anonymes Konto — ohne Zuordnung zum Gast. | Santé Royale | 25.04.2026 | Hoch |
| 6 | Reiseveranstalter buchen teilweise direkt über einen persönlichen Link in MEWS | Manche Reiseveranstalter erhalten einen direkten Buchungslink (über Maxi) und buchen so direkt ins MEWS — außerhalb des normalen Prozesses. Schafft einen unkontrollierten Kanal ohne einheitliche Datenqualität oder Nachvollziehbarkeit. | Santé Royale | 25.04.2026 | Mittel |
| 7 | Channel Manager überträgt Buchungen mit 20–30 Minuten Verzögerung ins PMS — Überbuchungsrisiko | Der Channel Manager hat einen Timelag von 20–30 Minuten bis eine eingehende Buchung im PMS landet. In dieser Lücke kann dasselbe Zimmer ein zweites Mal gebucht werden, was zu Überbuchungen führt. | Hotel Restaurant Fischer | 25.04.2026 | Hoch |
| 8 | Zeitdruck bei E-Mail-Anfragen — Antwortfenster von 30–60 Minuten | Große Gruppenanfragen gehen verloren, wenn nicht innerhalb von 30–60 Minuten geantwortet wird. Manuelle Bearbeitung kann dieses Fenster nicht zuverlässig einhalten. | Hotel Restaurant Fischer | 25.04.2026 | Hoch |
| 9 | Inkonsistente Rahmenverträge mit Firmensekretärinnen — hoher manueller Drafting-Aufwand | Sekretärinnen aus umliegenden Betrieben buchen im Auftrag ihrer Unternehmen und erwarten schnelle Rückmeldung. Liegt ein Rahmenvertrag vor, muss die Antwort diesem entsprechen. Liegt keiner vor, wird ein individuelles Angebot erwartet. In beiden Fällen muss manuell gedraftet werden — kein standardisierter Prozess möglich. | Hotel Restaurant Fischer | 25.04.2026 | Mittel |
| 10 | Gäste erwarten 24/7-Service und Check-in — Hotel hat keine durchgehende Besetzung | Gäste erwarten rund um die Uhr Erreichbarkeit und Check-in-Möglichkeit. Das Hotel löst das aktuell mit einem externen Call-Center-Partner, nicht systematisch. | Hotel Restaurant Fischer | 25.04.2026 | Mittel |
| 11 | Channel Manager reagiert rein mechanisch auf Buchungen und Stornierungen — keine Intelligenz oder Erfahrungswerte | Der Channel Manager bucht ein Zimmer weg wenn eine Buchung eingeht und gibt es frei wenn storniert wird — ohne zu hinterfragen ob die Stornierung z.B. versehentlich passiert ist. Es werden auch keine Kapazitäten auf Basis von Erfahrungswerten vorgehalten (z.B. erfahrungsgemäß hohe Last-Minute-Nachfrage). | Hotel Restaurant Fischer | 25.04.2026 | Mittel |
