CREATE EXTENSION postgres_fdw;
CREATE SERVER IF NOT EXISTS sambilaccesos
	FOREIGN DATA WRAPPER postgres_fdw 
	OPTIONS(host 'localhost', port '5432', dbname 'sambilproyectoaccesos');
CREATE USER MAPPING IF NOT EXISTS FOR CURRENT_USER
	SERVER sambilaccesos
	OPTIONS(user 'postgres', password '1234');
IMPORT FOREIGN SCHEMA public LIMIT TO (estadia)
	FROM SERVER sambilaccesos
	INTO public;
				
CREATE OR REPLACE FUNCTION verificarsmartphoneincc()
	RETURNS TRIGGER AS $$
		BEGIN
			IF(
				NOT EXISTS(SELECT idsmartphone 
					FROM estadia
				WHERE fechasalida IS NULL AND
				idsmartphone = NEW.idsmartphone)
			)THEN
				RAISE EXCEPTION 'El smartphone % no se encuentra en el cc', NEW.idsmartphone;
			END IF;
			RETURN NEW;
		END;
	$$
LANGUAGE plpgsql;

CREATE TRIGGER verificarsmartphoneincc_trigg 
BEFORE INSERT ON factura
FOR EACH ROW EXECUTE PROCEDURE verificarsmartphoneincc();