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
| BA-1 | | | | | |

---

## Hotel Manager

Überwacht den Hotelbetrieb und die Performance.

| ID | Pain Point | Kontext / Zitat | Quelle | Datum | Schweregrad |
|---|---|---|---|---|---|
| HM-1 | MEWS weist Zimmer ohne Slot-Optimierung zu — freie Einzeltage werden verschwendet | MEWS nimmt bei eingehender Buchung immer das erste verfügbare Zimmer, das die Anforderungen erfüllt, ohne benachbarte Belegungslücken zu berücksichtigen. Beispiel: Ein Gast bucht 1 Nacht — MEWS weist das Zimmer mit 5 zusammenhängend freien Wochen zu statt das Zimmer mit nur 1 freien Tag. Damit blockiert eine 1-Nacht-Buchung einen langen zusammenhängenden Block und verhindert eine potenzielle Mehrwochen-Buchung. | Rezeptionist, Santé Royale Rügen Resort (Gespräch) | 25.04.2026 | Hoch |

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
| ÜG-1 | Stornierung ohne Rechnung führt zu nicht zuordenbarem Zahlungseingang in MEWS | Bei Stornierung löschen Mitarbeiter die Rechnungsstellung in MEWS und schicken stattdessen eine manuelle Zahlungsaufforderung. Da keine Rechnung erstellt wurde, wird auch kein Gast-Buchhaltungskonto in MEWS angelegt. Zahlt der Gast trotzdem, bucht MEWS den Eingang auf ein anonymes Konto — ohne Zuordnung zum Gast. | Maximiliane, Santé Royale Rügen Resort (Interview) | 25.04.2026 | Hoch |
