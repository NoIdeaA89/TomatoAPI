BEGIN;

DROP TABLE IF EXISTS sectores CASCADE;
DROP TABLE IF EXISTS plantas CASCADE;

CREATE TABLE plantas (
    id_planta SERIAL PRIMARY KEY,
    nombre_comun VARCHAR(100) UNIQUE NOT NULL,
    profundidad_raiz_cm INT NOT NULL,
    kc_inicial DECIMAL(3,2) NOT NULL,
    kc_medio DECIMAL(3,2) NOT NULL,
    kc_final DECIMAL(3,2) NOT NULL
);

CREATE TABLE sectores (
    id_sector SERIAL PRIMARY KEY,
    nombre_sector VARCHAR(100) NOT NULL,
    id_planta INT REFERENCES plantas(id_planta) ON DELETE RESTRICT,
    tipo_suelo VARCHAR(50) NOT NULL,
    etapa_desarrollo VARCHAR(50) NOT NULL,
    fecha_ultimo_riego TIMESTAMP,
    zona_plantacion_latitud DECIMAL(9,6) NOT NULL,
    zona_plantacion_longitud DECIMAL(9,6) NOT NULL
);

COMMIT;