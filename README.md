# Pocket Calculator - Altersvorsorge-Vergleich

Ein interaktives Python-Tool zum Vergleich verschiedener Altersvorsorge-Produkte in Deutschland mit Web-Interface und grafischer Darstellung.

## Features

- **Interaktives Web-Interface** mit Streamlit
- **Grafische Darstellung** der Vermögensentwicklung über die Jahre
- **Vergleichsgrafiken** für alle Produkte
- **Detaillierte Parametereinstellungen** für jedes Produkt

Vergleicht folgende Anlageformen:
- **ETF-Sparplan** (private Altersvorsorge)
- **Basisrente** (Rürup-Rente)
- **Riester-Rente**

## Berechnungsgrundlagen

### 1. ETF-Sparplan

**Prinzip:** Private Altersvorsorge mit börsengehandelten Indexfonds.

**Nettorendite:**

$$r_n = r_b - TER - s$$

**Endwert (brutto, vor Steuern):**

$$FV_b = I_M \times \frac{(1 + \frac{r_n}{12})^{12 \times t} - 1}{\frac{r_n}{12}} + I_0 \times (1 - s) \times (1 + r_n)^t - (G_o + G_a)$$

Wobei:
- $I_M$ = monatlicher Sparbeitrag
- $I_0$ = Einmaleinzahlung zu Beginn
- $r_n$ = Nettorendite p.a. (nach Kosten)
- $r_b$ = Bruttorendite p.a. (vor Kosten)
- $t$ = Laufzeit in Jahren
- $s$ = Spread (Geld-Brief-Spanne)
- $TER$ = Total Expense Ratio (Gesamtkostenquote)
- $G_o$ = Ordergebühren gesamt: $12 \times t \times$ Gebühr pro Order
- $G_a$ = Depotgebühren gesamt: $t \times$ Gebühr pro Jahr

**Besteuerung (bei Verkauf):**

$$T_{AGS} = \max(0, (FV_b - I_{gesamt}) - F) \times 0{,}26375$$

$$FV_n = FV_b - T_{AGS}$$

- $T_{AGS}$ = Abgeltungssteuer (25% + 5,5% Soli = 26,375%)
- $F$ = Freibetrag: 1.000€ (Singles) / 2.000€ (Paare) **nur im Verkaufsjahr**
- $I_{gesamt}$ = Gesamte Einzahlungen: $I_M \times 12 \times t + I_0$
- $FV_n$ = Endwert netto (nach Steuern)

**Besonderheiten:**
- ✅ Volle Flexibilität (jederzeit verkaufbar)
- ❌ Keine Förderung während Ansparphase
- ⚠️ Freibetrag verfällt jährlich (keine Ansammlung)

---

### 2. Basisrente (Rürup)

**Prinzip:** Steuerlich geförderte Altersvorsorge mit nachgelagerter Besteuerung.

**Nettorendite:**

$$r_n = r_b - K_{eff}$$

**Endwert (brutto, vor Steuern):**

$$FV_b = I_M \times \frac{(1 + \frac{r_n}{12})^{12 \times t} - 1}{\frac{r_n}{12}} + I_0 \times (1 + r_n)^t$$

Wobei:
- $I_M$ = monatlicher Sparbeitrag
- $I_0$ = Einmaleinzahlung zu Beginn
- $r_n$ = Nettorendite p.a. (nach Kosten)
- $r_b$ = Bruttorendite p.a. (vor Kosten)
- $K_{eff}$ = Effektivkosten p.a. (typisch 1,5%)
- $t$ = Laufzeit in Jahren

**Steuerersparnis während Ansparphase:**

$$S_{Anspar} = B_{gesamt} \times A \times T_a$$

- $B_{gesamt}$ = Gesamte Beiträge: $I_M \times 12 \times t + I_0$
- $A$ = Absetzbarkeit (100% ab 2025, max. 27.566€/Jahr Singles, 55.132€ Paare)
- $T_a$ = Steuersatz während Ansparphase

**Besteuerung bei Auszahlung:**

$$T_{Rente} = FV_b \times B_s \times T_r$$

**Endwert netto (gesamtes verfügbares Kapital):**

$$FV_n = FV_b - T_{Rente} + S_{Anspar}$$

💡 Die Steuerersparnis während der Ansparphase wird zum Endwert addiert, da dies Geld ist, das man zurückbekommen hat und zur Verfügung steht.

- $B_s$ = Besteuerungsanteil (100% ab 2040, stufenweise Erhöhung)
- $T_r$ = Steuersatz im Rentenalter (meist niedriger als $T_a$)
- $FV_n$ = Endwert netto (Rentenwert + Steuerersparnis)

**Netto-Eigeninvestition:**

$$I_{eigen} = B_{gesamt} - S_{Anspar}$$

Was tatsächlich aus eigener Tasche gezahlt wurde (Beiträge minus Steuererstattung).

**Effektivkosten im Detail:**

Die Effektivkosten $K_{eff}$ setzen sich zusammen aus:

1. **Bruttopolice (provisionsbasiert):**
   $$K_{eff} = K_{Abschluss} + K_{Verwaltung} + K_{Vertrieb} + K_{Garantie}$$

   - $K_{Abschluss}$ = Abschlusskosten (3-5% der Beitragssumme, verteilt über 5 Jahre)
   - $K_{Verwaltung}$ = Laufende Verwaltung (0,5-1,0% p.a.)
   - $K_{Vertrieb}$ = Vertriebsprovisionen (eingerechnet in Abschlusskosten)
   - $K_{Garantie}$ = Kosten für Verrentungsgarantie
   - **Gesamt typisch: 1,5-2,5% p.a.**

2. **Nettopolice (honorarbasiert):**
   $$K_{eff} = K_{Verwaltung} + K_{Garantie}$$
   $$\text{Zusätzlich separat: } H \text{ (Honorargebühr einmalig)}$$

   - Keine Abschluss-/Vertriebskosten im Vertrag
   - $K_{Verwaltung}$ = 0,3-0,8% p.a.
   - $H$ = Einmalige Honorargebühr: 1.500-5.000€ (an Berater)
   - **Gesamt typisch: 0,8-1,5% p.a. + Honorar**

💡 **Vorteil Nettopolice:** Niedrigere laufende Kosten, aber höhere Anfangsinvestition durch Honorar

**Beispielrechnung Effektivkosten:**
- Beitrag: 300€/Monat über 30 Jahre = 108.000€
- **Bruttopolice:** 4% Abschluss = 4.320€ + 1% p.a. Verwaltung
- **Nettopolice:** 0,5% p.a. Verwaltung + 3.000€ Honorar einmalig

**Besonderheiten:**
- ❌ Keine Kapitalentnahme möglich (nur Verrentung)
- ⚠️ Höhere Effektivkosten als bei ETFs (ca. 1,5% p.a.)
- ❌ Keine staatlichen Zulagen

---

### 3. Riester-Rente

**Prinzip:** Staatlich geförderte Altersvorsorge mit Zulagen und Steuervorteilen.

**Nettorendite:**

$$r_n = r_b - K_{eff}$$

⚠️ Konservative Rendite wegen Beitragsgarantie (typisch 3%)

Wobei:
- $r_n$ = Nettorendite p.a. (nach Kosten)
- $r_b$ = Bruttorendite p.a. (vor Kosten)
- $K_{eff}$ = Effektivkosten p.a. (typisch 2%)

**Staatliche Förderung:**

$$Z_{gesamt} = (Z_G + Z_K) \times t$$

- $Z_G$ = Grundzulage: 175€/Jahr
- $Z_K$ = Kinderzulage: 300€/Jahr pro Kind (geboren ab 2008)
- $t$ = Laufzeit in Jahren

**Günstigerprüfung (Sonderausgabenabzug):**

$$S_{Jahr} = \min(I_M \times 12, 2.100€) \times T_a$$

$$S_{zusätzlich} = \max(0, S_{Jahr} - (Z_G + Z_K)) \times t$$

💡 Das Finanzamt gewährt automatisch die günstigere Variante.

- $S_{Jahr}$ = Steuerersparnis pro Jahr
- $S_{zusätzlich}$ = Zusätzlicher Steuervorteil (über Zulagen hinaus)
- $T_a$ = Steuersatz während Ansparphase

**Endwert (brutto, vor Steuern):**

$$I_{M,gefördert} = I_M + \frac{Z_G + Z_K}{12}$$

$$FV_b = I_{M,gefördert} \times \frac{(1 + \frac{r_n}{12})^{12 \times t} - 1}{\frac{r_n}{12}}$$

- $I_{M,gefördert}$ = Monatlicher Sparbeitrag inkl. anteiliger Zulagen
- Die Jahres-Zulagen $(Z_G + Z_K)$ werden durch 12 geteilt für den monatlichen Anteil

**Besteuerung bei Auszahlung:**

$$T_{Rente} = FV_b \times T_r$$

**Endwert netto (gesamtes verfügbares Kapital):**

$$FV_n = FV_b - T_{Rente} + S_{zusätzlich}$$

💡 Die zusätzliche Steuerersparnis wird zum Endwert addiert, da dies Geld ist, das man zurückbekommen hat und zur Verfügung steht. Die Zulagen sind bereits in $FV_b$ enthalten (wurden mitangelegt).

- $T_r$ = Steuersatz im Rentenalter
- $FV_n$ = Endwert netto (Rentenwert + Steuerersparnis)
- Volle nachgelagerte Besteuerung des Kapitals oder der Rente

**Netto-Eigeninvestition:**

$$I_{eigen} = I_M \times 12 \times t - S_{zusätzlich}$$

Was tatsächlich aus eigener Tasche gezahlt wurde (Beiträge minus Steuererstattung). Die Zulagen haben damit nichts zu tun!

**Effektivkosten im Detail:**

Die Effektivkosten $K_{eff}$ bei Riester sind höher als bei Basisrente wegen der Beitragsgarantie:

1. **Bruttopolice (klassisch):**
   $$K_{eff} = K_{Abschluss} + K_{Verwaltung} + K_{Vertrieb} + K_{Garantie} + K_{Beitragsgarantie}$$

   - $K_{Abschluss}$ = Abschlusskosten (4-6% der Beitragssumme)
   - $K_{Verwaltung}$ = Laufende Verwaltung (0,5-1,2% p.a.)
   - $K_{Garantie}$ = Verrentungsgarantie
   - $K_{Beitragsgarantie}$ = Kosten für gesetzliche 100% Kapitalgarantie (0,5-1,0% p.a.)
   - **Gesamt typisch: 2,0-3,0% p.a.**

2. **Riester-Fondssparplan (niedrigere Kosten):**
   $$K_{eff} = K_{Verwaltung} + K_{Depotgebühr} + K_{Beitragsgarantie}$$

   - $K_{Verwaltung}$ = 0,5-1,0% p.a.
   - $K_{Depotgebühr}$ = 10-30€/Jahr
   - $K_{Beitragsgarantie}$ = Kosten für Garantie (durch konservative Anlage)
   - **Gesamt typisch: 1,5-2,0% p.a.**

3. **Riester-ETF (z.B. Fairr/Sutor):**
   - Niedrigste Kosten: 0,5-1,0% p.a.
   - Aber: Höhere Garantiekosten in letzten Jahren (Lifecycle-Modell)

💡 **Problem Beitragsgarantie:** Zwingt zu konservativer Anlage, reduziert Rendite zusätzlich zu Kosten

**Beispielrechnung Effektivkosten:**
- Beitrag: 200€/Monat über 30 Jahre = 72.000€
- **Klassische Riester:** 5% Abschluss = 3.600€ + 1,5% p.a.
- **Fondssparplan:** 1% p.a. + 20€/Jahr Depot
- **Riester-ETF:** 0,8% p.a. (aber höhere Garantiekosten am Ende)

**Besonderheiten:**
- 🛡️ Beitragsgarantie reduziert Rendite erheblich
- ⚠️ Höchste Kosten aller drei Produkte (ca. 2% p.a.)
- 💰 Bis 30% Einmalauszahlung möglich
- 👶 Besonders vorteilhaft mit Kindern (wegen Zulagen)

---

## Vergleich der Faktoren

| Faktor | ETF-Sparplan | Basisrente | Riester |
|--------|--------------|------------|---------|
| **Förderung** | ❌ Keine | ✅ Steuerabzug | ✅ Zulagen + Steuer |
| **Flexibilität** | ✅ Voll | ❌ Keine | ⚠️ Eingeschränkt |
| **Kosten (p.a.)** | 0,2% - 0,5% | 1,0% - 2,0% | 1,5% - 2,5% |
| **Rendite** | ⭐ Hoch (7%) | ⭐ Mittel-Hoch (5-7%) | ⚠️ Niedrig (3%) |
| **Besteuerung** | Abgeltungssteuer | Nachgelagert | Nachgelagert |
| **Garantie** | ❌ Keine | ❌ Keine | ✅ Beitragsgarantie |

## Installation

```bash
# Virtual Environment erstellen (falls noch nicht geschehen)
python3 -m venv venv

# Virtual Environment aktivieren
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## Verwendung

### Web-Interface (empfohlen)

#### Einfache Version:
```bash
streamlit run app.py
```

#### ⭐ Erweiterte Version (NEU!):
```bash
streamlit run app_extended.py
```

**Neue Features der erweiterten Version:**
- 💰 Detaillierte Kostenanalyse (Ordergebühren, Depotgebühren, Spread, etc.)
- 📚 Hilfetexte mit realen Beispielen (Trade Republic, flatex, etc.)
- 🧮 Rentensteuer-Berechnung basierend auf Gesamteinkommen
- 📊 Erweiterte Ergebnistabelle mit Netto-Renten
- 🔧 Kostenrechner für Abschlusskosten
- 🎯 Übersichtlichere Oberfläche mit ausklappbaren Optionen

Siehe [FEATURES.md](FEATURES.md) für Details.

Die App öffnet sich automatisch im Browser unter http://localhost:8501

Um die App zu stoppen, drücken Sie `Ctrl+C` im Terminal.

#### Features der Web-App:
- Eingabe aller Parameter über intuitive Formulare
- Interaktive Grafiken mit Plotly (Zoom, Pan, Hover-Informationen)
- Vermögensentwicklung über die Jahre
- Balkendiagramme für Endwert-Vergleich
- Detaillierte Tabellen mit allen Kennzahlen
- Export-Möglichkeiten

### Command-Line Interface (Alternative)

#### Basis-Vergleich
```bash
python3 main.py
```

#### Mit eigenen Parametern
```bash
python3 main.py -m 500 -y 30 -t 0.42 -r 0.07
```

#### Alle Optionen
```bash
python3 main.py --help
```

#### CLI Parameter:
- `-m, --monthly`: Monatlicher Sparbeitrag in Euro (Standard: 500)
- `-y, --years`: Anlagedauer in Jahren (Standard: 30)
- `-t, --tax-rate`: Persönlicher Steuersatz als Dezimalzahl (Standard: 0.42)
- `-r, --return`: Erwartete jährliche ETF-Rendite (Standard: 0.07)
- `--riester-children`: Anzahl Kinder für Riester-Zulage (Standard: 0)
- `--yearly`: Zeige jahresweise Entwicklung
- `--products`: Welche Produkte vergleichen (etf, basisrente, riester, all)

#### CLI Beispiele

**Vergleich mit 2 Kindern (Riester-Vorteil):**
```bash
python3 main.py -m 500 -y 30 --riester-children 2
```

**Nur ETF vs. Basisrente:**
```bash
python3 main.py --products etf basisrente
```

**Mit jahresweiser Entwicklung:**
```bash
python3 main.py --yearly
```

**Höheres Einkommen (höherer Steuersatz):**
```bash
python3 main.py -m 1000 -t 0.45 -y 35
```

## Screenshots & Ausgabe

### Web-Interface
Die Web-App bietet:
1. **Interaktive Eingabeformulare** für alle Parameter
2. **Vermögensübersicht** mit Kennzahlen für jedes Produkt
3. **Detaillierte Vergleichstabelle** mit allen Werten
4. **Interaktiver Linien-Chart** zeigt Vermögensentwicklung über Jahre
5. **Balkendiagramm** für Endwert-Vergleich
6. **Empfehlung** basierend auf Ihren Eingaben

### CLI-Ausgabe
Das CLI-Tool zeigt:
1. Zusammenfassung aller Produkte mit:
   - Eigene Einzahlungen
   - Steuervorteile/Zulagen
   - Endwert nach Steuern
   - Gewinn und Rendite
2. Vergleich zum besten Produkt
3. Optional: Jahresweise Entwicklung
4. Empfehlung mit wichtigen Hinweisen

## Wichtige Hinweise

Diese Berechnungen sind **Vereinfachungen** und ersetzen keine professionelle Finanzberatung!

**Nicht berücksichtigt:**
- Inflation
- Individuelle Vertragsbedingungen
- Änderungen in der Gesetzgebung
- Persönliche Flexibilitätsbedürfnisse
- Konkrete Produkt-Kosten einzelner Anbieter

**Weitere Faktoren:**
- ETFs bieten höchste Flexibilität (jederzeit verkaufbar)
- Riester/Rürup sind bis zur Rente gebunden
- Riester hat Beitragsgarantie (Sicherheit vs. Rendite)
- Steuervorteile sind individuell unterschiedlich

---

## Glossar

### Variablen in den Formeln

| Variable | Bedeutung | Einheit |
|----------|-----------|---------|
| $FV_b$ | Future Value brutto (Endwert vor Steuern) | € |
| $FV_n$ | Future Value netto (Endwert nach Steuern) | € |
| $I_M$ | Monatlicher Sparbeitrag (Investment Monthly) | €/Monat |
| $I_0$ | Einmaleinzahlung zu Beginn | € |
| $I_{gesamt}$ | Gesamte Einzahlungen | € |
| $I_{eigen}$ | Netto-Eigeninvestition | € |
| $r_b$ | Bruttorendite p.a. (vor Kosten) | Dezimal (z.B. 0,07 = 7%) |
| $r_n$ | Nettorendite p.a. (nach Kosten) | Dezimal |
| $t$ | Laufzeit | Jahre |

### Kosten & Gebühren

| Variable | Bedeutung | Kontext |
|----------|-----------|---------|
| $TER$ | Total Expense Ratio (Gesamtkostenquote) | ETF |
| $s$ | Spread (Geld-Brief-Spanne) | ETF |
| $G_o$ | Ordergebühren gesamt | ETF |
| $G_a$ | Depotgebühren (annual) gesamt | ETF |
| $K_{eff}$ | Effektivkosten p.a. | Basisrente, Riester |
| $H$ | Honorargebühr (einmalig) | Basisrente |

### Steuern & Förderung

| Variable | Bedeutung | Kontext |
|----------|-----------|---------|
| $T_{AGS}$ | Abgeltungssteuer (25% + 5,5% Soli = 26,375%) | ETF |
| $F$ | Freibetrag (Sparerpauschbetrag) | ETF |
| $T_a$ | Steuersatz während Ansparphase | Basisrente, Riester |
| $T_r$ | Steuersatz im Rentenalter | Basisrente, Riester |
| $T_{Rente}$ | Steuerlast bei Rentenauszahlung | Basisrente, Riester |
| $A$ | Absetzbarkeit (Deductibility) | Basisrente |
| $B_s$ | Besteuerungsanteil | Basisrente |
| $S_{Anspar}$ | Steuerersparnis während Ansparphase | Basisrente |
| $Z_G$ | Grundzulage (Riester) | Riester |
| $Z_K$ | Kinderzulage (Riester) | Riester |
| $Z_{gesamt}$ | Gesamte Zulagen | Riester |
| $S_{Jahr}$ | Steuerersparnis pro Jahr | Riester |
| $S_{zusätzlich}$ | Zusätzlicher Steuervorteil | Riester |

### Fachbegriffe

**TER (Total Expense Ratio)**
- Gesamtkostenquote eines ETFs
- Beinhaltet: Verwaltungsgebühren, Depotbankgebühren, Wirtschaftsprüfungskosten
- Typisch: 0,1% - 0,5% p.a. bei ETFs
- Wird automatisch vom Fondsvermögen abgezogen

**Spread (Geld-Brief-Spanne)**
- Differenz zwischen Kauf- und Verkaufspreis
- Entsteht beim Handel an der Börse
- Typisch: 0,05% - 0,2% bei liquiden ETFs
- Wird beim Kauf/Verkauf fällig

**Abgeltungssteuer**
- Pauschalsteuer auf Kapitalerträge
- 25% Steuer + 5,5% Solidaritätszuschlag = **26,375%**
- Gilt für Zinsen, Dividenden und Kursgewinne
- Wird automatisch von der Bank einbehalten

**Sparerpauschbetrag**
- Freibetrag für Kapitalerträge
- 1.000€/Jahr (Singles), 2.000€/Jahr (Paare)
- Verfällt jährlich (keine Ansammlung möglich)
- Kann über Freistellungsauftrag genutzt werden

**Effektivkosten**
- Alle Kosten einer Versicherung/Anlage zusammengefasst
- Beinhaltet: Abschlusskosten, Verwaltungsgebühren, Vertriebskosten
- Typisch Basisrente: 1,0% - 2,0% p.a.
- Typisch Riester: 1,5% - 2,5% p.a.

**Nachgelagerte Besteuerung**
- Steuervorteile während Ansparphase
- Besteuerung erst bei Rentenauszahlung
- Vorteil: Meist niedrigerer Steuersatz im Alter
- Gilt für: Basisrente, Riester, gesetzliche Rente

**Günstigerprüfung (Riester)**
- Finanzamt vergleicht automatisch: Zulage vs. Steuerersparnis
- Gewährt wird die vorteilhaftere Variante
- Bei hohem Einkommen: Meist Steuerersparnis günstiger
- Bei niedrigem Einkommen: Meist Zulage günstiger

---

## Lizenz

MIT License
