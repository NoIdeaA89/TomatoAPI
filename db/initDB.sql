BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

DROP TABLE IF EXISTS plantaciones CASCADE;
DROP TABLE IF EXISTS sectores CASCADE;
DROP TABLE IF EXISTS plantas CASCADE;
DROP TABLE IF EXISTS agronomos CASCADE;

CREATE TABLE plantas (
    id_planta SERIAL PRIMARY KEY,
    nombre_comun VARCHAR(100) UNIQUE NOT NULL,
    profundidad_raiz_cm INT NOT NULL,
    kc_inicial DECIMAL(3,2) NOT NULL,
    kc_medio DECIMAL(3,2) NOT NULL,
    kc_final DECIMAL(3,2) NOT NULL
);

CREATE TABLE agronomos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE plantaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agronomo_id UUID NOT NULL,
    planta_externa_id VARCHAR(50),
    zona_ubicacion VARCHAR(150) NOT NULL,
    tipo_tierra VARCHAR(50) NOT NULL,
    etapa_desarrollo VARCHAR(50) NOT NULL,
    ultimo_riego TIMESTAMP,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_plantaciones_agronomo
        FOREIGN KEY (agronomo_id) REFERENCES agronomos(id)
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