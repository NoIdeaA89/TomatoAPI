-- Conserva el esquema SQL original en un namespace separado.
-- Después, el backend crea las tablas actuales y carga su catálogo.
-- Los registros antiguos se conservan, pero no se importan a la aplicación actual.
BEGIN;
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'plantas' AND column_name = 'id_planta'
    ) THEN
        CREATE SCHEMA IF NOT EXISTS tomato_legacy_v1;
        ALTER TABLE public.plantas SET SCHEMA tomato_legacy_v1;
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'plantaciones' AND column_name = 'agronomo_id'
        ) THEN
            ALTER TABLE public.plantaciones SET SCHEMA tomato_legacy_v1;
        END IF;
        IF to_regclass('public.sectores') IS NOT NULL THEN
            ALTER TABLE public.sectores SET SCHEMA tomato_legacy_v1;
        END IF;
        IF to_regclass('public.agronomos') IS NOT NULL THEN
            ALTER TABLE public.agronomos SET SCHEMA tomato_legacy_v1;
        END IF;
    END IF;
END $$;
COMMIT;
