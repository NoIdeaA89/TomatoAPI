BEGIN;

INSERT INTO plantas (nombre_comun, profundidad_raiz_cm, kc_inicial, kc_medio, kc_final) VALUES
('Alfalfa', 150, 0.40, 0.95, 0.90),
('Lechuga', 20, 0.70, 1.05, 0.95),
('Tomate', 60, 0.60, 1.15, 0.80);

INSERT INTO sectores (nombre_sector, id_planta, tipo_suelo, etapa_desarrollo, fecha_ultimo_riego, zona_plantacion_latitud, zona_plantacion_longitud) VALUES
('Lote A1 - Altovalsol', 1, 'Franco', 'Medio', CURRENT_TIMESTAMP - INTERVAL '3 days', -29.96, -71.34),
('Huerto B2', 2, 'Arenoso', 'Inicial', CURRENT_TIMESTAMP - INTERVAL '1 day', -29.95, -71.33);

COMMIT;