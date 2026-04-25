# Pain Points — Kundengespräche

Dieses Dokument sammelt Insights aus Kundengesprächen, Beobachtungen und Workshops. Jeder Eintrag ist einer Persona zugeordnet. Neue Einträge kommen ans Ende der jeweiligen Tabelle.

**Spalten:**
- **ID** — fortlaufend je Persona (BA-1, HM-1, HG-1)
- **Pain Point** — kurze Beschreibung des Problems
- **Kontext / Zitat** — was genau gesagt oder beobachtet wurde
- **Quelle** — z.B. Name, Rolle oder Gesprächsformat (Interview, Workshop, Hackathon)
- **Datum** — wann der Insight erhoben wurde
- **Schweregrad** — Hoch / Mittel / Niedrig

---

## Booking Assistant

Mitarbeiter, der eingehende Buchungen verarbeitet und ins System einträgt.

| ID | Pain Point | Kontext / Zitat | Quelle | Datum | Schweregrad |
|---|---|---|---|---|---|
| BA-1 | Einarbeitung dauert bis zu 3 Wochen; Fehler durch große Anzahl an Sonderregeln | Neue Mitarbeiter brauchen wochenlang bis zur Produktivität. Sonderregeln sind nicht zentral dokumentiert — Wissen steckt bei einzelnen Personen. | Hotels | 25.04.2026 | Hoch |

---

## Hotel Manager

Überwacht den Hotelbetrieb und die Performance.

| ID | Pain Point | Kontext / Zitat | Quelle | Datum | Schweregrad |
|---|---|---|---|---|---|
| HM-1 | MEWS weist Zimmer ohne Slot-Optimierung zu — freie Einzeltage werden verschwendet | MEWS nimmt bei eingehender Buchung immer das erste verfügbare Zimmer, das die Anforderungen erfüllt, ohne benachbarte Belegungslücken zu berücksichtigen. Beispiel: Ein Gast bucht 1 Nacht — MEWS weist das Zimmer mit 5 zusammenhängend freien Wochen zu statt das Zimmer mit nur 1 freien Tag. Damit blockiert eine 1-Nacht-Buchung einen langen zusammenhängenden Block und verhindert eine potenzielle Mehrwochen-Buchung. | Hotels | 25.04.2026 | Hoch |
| HM-2 | Keine Konsistenz beim Rechnungsversand an Reiseveranstalter | Manchmal werden Rechnungen über das System an Reiseveranstalter versendet, manchmal nicht. Es gibt keinen einheitlichen Prozess — abhängig von Mitarbeiter oder Situation. | Hotels | 25.04.2026 | Mittel |
| HM-3 | Manuelle Prüfung der AKON-Extranetseite auf neue oder geänderte Buchungen | Der Hotelmanager muss die Extranetseite von AKON manuell aufrufen und eigenständig prüfen, ob es neue Buchungen oder Änderungen gibt, und diese dann manuell ins PMS eintragen. Kein automatischer Datenabgleich. | Hotels | 25.04.2026 | Hoch |

---

## Hotel Guest

Bucht Zimmer und verwaltet seinen Aufenthalt.

| ID | Pain Point | Kontext / Zitat | Quelle | Datum | Schweregrad |
|---|---|---|---|---|---|
| HG-1 | | | | | |

---

## Übergreifend

Pain Points, die mehrere Personas oder das System als Ganzes betreffen.

| ID | Pain Point | Betroffene Personas | Kontext / Zitat | Quelle | Datum | Schweregrad |
|---|---|---|---|---|---|---|
| ÜG-1 | Stornierung ohne Rechnung führt zu nicht zuordenbarem Zahlungseingang in MEWS | Bei Stornierung löschen Mitarbeiter die Rechnungsstellung in MEWS und schicken stattdessen eine manuelle Zahlungsaufforderung. Da keine Rechnung erstellt wurde, wird auch kein Gast-Buchhaltungskonto in MEWS angelegt. Zahlt der Gast trotzdem, bucht MEWS den Eingang auf ein anonymes Konto — ohne Zuordnung zum Gast. | Hotels | 25.04.2026 | Hoch |
| ÜG-2 | Reiseveranstalter buchen teilweise direkt über einen persönlichen Link in MEWS | Manche Reiseveranstalter erhalten einen direkten Buchungslink (über Maxi) und buchen so direkt ins MEWS — außerhalb des normalen Prozesses. Schafft einen unkontrollierten Kanal ohne einheitliche Datenqualität oder Nachvollziehbarkeit. | Hotels | 25.04.2026 | Mittel |
