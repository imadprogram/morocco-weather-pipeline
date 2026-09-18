-- Quelles villes auront les températures les plus élevées 
SELECT 
    c.city_name,
    c.admin_name,
    w.forecast_date,
    w.temp_max
FROM weather_forecasts w
JOIN cities c ON w.city_id = c.id
ORDER BY w.temp_max DESC
LIMIT 10;





-- Quelles villes auront les plus fortes précipitations 
SELECT 
    c.city_name,
    c.admin_name,
    ROUND(SUM(w.precipitation)::numeric, 2) AS total_precipitation
FROM weather_forecasts w
JOIN cities c ON w.city_id = c.id
GROUP BY c.city_name, c.admin_name
ORDER BY total_precipitation DESC
LIMIT 10;





-- Quelles villes présentent le risque moyen le plus élevé 
SELECT 
    c.city_name,
    c.admin_name,
    ROUND(AVG(w.risk_score)::numeric, 2) AS avg_risk_score
FROM weather_forecasts w
JOIN cities c ON w.city_id = c.id
GROUP BY c.city_name, c.admin_name
ORDER BY avg_risk_score DESC
LIMIT 10;





-- Quelles périodes (dates) présentent le risque maximal 
SELECT 
    w.forecast_date,
    ROUND(AVG(w.risk_score)::numeric, 2) AS avg_daily_risk,
    MAX(w.risk_score) AS max_daily_risk,
    COUNT(*) FILTER (WHERE w.risk_level IN ('High', 'Critical')) AS high_critical_count
FROM weather_forecasts w
GROUP BY w.forecast_date
ORDER BY max_daily_risk DESC, avg_daily_risk DESC;






-- Pour chaque ville, quelle période (date) présente le plus grand risque 
SELECT DISTINCT ON (c.id)
    c.city_name,
    c.admin_name,
    w.forecast_date AS highest_risk_date,
    w.risk_score,
    w.risk_level
FROM weather_forecasts w
JOIN cities c ON w.city_id = c.id
ORDER BY c.id, w.risk_score DESC, w.forecast_date ASC;