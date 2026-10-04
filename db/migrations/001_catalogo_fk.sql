-- Ejecutar después del primer arranque del backend actualizado, que carga el catálogo.
-- Migración para la tabla plantaciones del backend anterior (user_id, planta, etc.).
-- No ejecutar initDB.sql sobre una base existente: ese archivo elimina tablas.
BEGIN;

DO $$
DECLARE
    fk RECORD;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'plantaciones'::regclass AND contype = 'f'
          AND confrelid = 'plantas'::regclass
          AND conkey = ARRAY[(SELECT attnum FROM pg_attribute
                             WHERE attrelid = 'plantaciones'::regclass AND attname = 'planta')]
    ) THEN
        ALTER TABLE plantaciones ADD CONSTRAINT plantaciones_planta_fkey
            FOREIGN KEY (planta) REFERENCES plantas(id) NOT VALID;
    END IF;
    -- Validar también una FK existente con otro nombre o creada como NOT VALID.
    FOR fk IN
        SELECT conname FROM pg_constraint
        WHERE conrelid = 'plantaciones'::regclass AND contype = 'f'
          AND confrelid = 'plantas'::regclass AND NOT convalidated
          AND conkey = ARRAY[(SELECT attnum FROM pg_attribute
                             WHERE attrelid = 'plantaciones'::regclass AND attname = 'planta')]
    LOOP
        -- Si hay referencias desconocidas, revierte sin borrar datos.
        EXECUTE format('ALTER TABLE plantaciones VALIDATE CONSTRAINT %I', fk.conname);
    END LOOP;
END $$;

COMMIT;
