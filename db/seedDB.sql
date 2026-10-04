BEGIN;

INSERT INTO plantas (id, nombre, especie, kc_ini, kc_mid, kc_end, raiz_m, agotamiento) VALUES
('tomate', 'Tomate', 'Solanum lycopersicum', 0.60, 1.15, 0.80, 0.70, 0.40),
('lechuga', 'Lechuga', 'Lactuca sativa', 0.70, 1.00, 0.95, 0.40, 0.30),
('papa', 'Papa', 'Solanum tuberosum', 0.50, 1.15, 0.75, 0.50, 0.35),
('maiz', 'Maíz', 'Zea mays', 0.30, 1.20, 0.60, 1.00, 0.55),
('pimenton', 'Pimentón', 'Capsicum annuum', 0.60, 1.05, 0.90, 0.60, 0.30),
('zanahoria', 'Zanahoria', 'Daucus carota', 0.70, 1.05, 0.95, 0.50, 0.35)
ON CONFLICT (id) DO NOTHING;

COMMIT;