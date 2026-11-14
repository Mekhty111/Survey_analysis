# Sabaha saxlayaq? Tələbələr arasında prokrastinasiya sorğusu (demo)

Universitet dərsi üçün demo layihə: Azərbaycan dilində sorğu, 82 sintetik (mock) cavab və analiz olunan statik sayt.

## Struktur

| Yol | İçində nə var |
|---|---|
| `survey/sorgu.md` | Sorğunun 24 sualı (AZ), Google Forms-a köçürməyə hazırdır |
| `scripts/generate_data.py` | Real görünən mock cavabların generatoru (seed 2026, cavablar gizli "prokrastinasiya meyli" ilə bağlıdır) |
| `data/responses.csv`, `data/responses.json` | Yaradılmış cavablar |
| `scripts/analyze.py` | Paylanmaları, çarpaz cədvəlləri və korrelyasiyaları hesablayır və `site/data.js` faylına yazır |
| `site/` | Sayt: `index.html`, `style.css`, `app.js` (Chart.js 4.4.1), `data.js` |

## Məlumatları yenidən yaratmaq

```bash
python scripts/generate_data.py
python scripts/analyze.py
cp data/responses.csv survey/sorgu.md site/
```

## Lokal baxış

```bash
python -m http.server 5510 --directory site
```

## Deploy

```bash
cd site
vercel --prod
```
"# Survey_analysis" 
