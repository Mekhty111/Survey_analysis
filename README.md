# Sabaha saxlayaq? — опрос о прокрастинации студентов (демо)

Демо-проект для пары: опрос на азербайджанском, 82 синтетических (mock) ответа и статичный сайт с анализом.

## Структура

| Путь | Что внутри |
|---|---|
| `survey/sorgu.md` | 20 вопросов опроса (AZ), готово к переносу в Google Forms |
| `scripts/generate_data.py` | Генератор реалистичных mock-ответов (seed 2026, ответы связаны скрытой «склонностью к прокрастинации») |
| `data/responses.csv`, `data/responses.json` | Сгенерированные ответы |
| `scripts/analyze.py` | Считает распределения, кросс-таблицы и корреляции и пишет их в `site/data.js` |
| `site/` | Сайт: `index.html`, `style.css`, `app.js` (Chart.js 4.4.1), `data.js` |

## Пересобрать данные

```bash
python scripts/generate_data.py
python scripts/analyze.py
cp data/responses.csv survey/sorgu.md site/
```

## Локальный просмотр

```bash
python -m http.server 5510 --directory site
```

## Деплой

```bash
cd site
vercel --prod
```
"# Survey_analysis" 
