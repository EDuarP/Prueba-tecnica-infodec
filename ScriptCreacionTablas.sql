CREATE SCHEMA `ventasplusdb` ;
CREATE TABLE `ventasplusdb`.`vendedores` (
  `idvendedores` INT NOT NULL,
  `nombre` VARCHAR(45) NULL,
  PRIMARY KEY (`idvendedores`));

ALTER TABLE `ventasplusdb`.`vendedores` 
CHANGE COLUMN `idvendedores` `idvendedores` INT NOT NULL AUTO_INCREMENT ;
CREATE TABLE `ventasplusdb`.`productos` (
  `nombre_producto` VARCHAR(45) NULL,
  `referencia` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`referencia`));

ALTER TABLE `ventasplusdb`.`productos` 
ADD COLUMN `valorunitario` DOUBLE NULL AFTER `referencia`;
CREATE TABLE `ventasplusdb`.`operaciones` (
  `idoperaciones` INT NOT NULL,
  `fecha` DATE NULL,
  `idvendedor` INT NULL,
  `referencia` VARCHAR(45) NULL,
  `cantidad` INT NULL,
  `valorvendido` DOUBLE NULL,
  `impuesto` DOUBLE NULL,
  `tipooperacion` VARCHAR(45) NULL,
  `motivo` VARCHAR(45) NULL,
  PRIMARY KEY (`idoperaciones`));

ALTER TABLE `ventasplusdb`.`operaciones` 
CHANGE COLUMN `idoperaciones` `idoperaciones` INT NOT NULL AUTO_INCREMENT ,
DROP INDEX `idvendedor_idx` ;
;
ALTER TABLE `ventasplusdb`.`operaciones` 
ADD INDEX `idvendedor_idx` (`idvendedor` ASC) VISIBLE,
ADD INDEX `referencia_idx` (`referencia` ASC) VISIBLE;
;
ALTER TABLE `ventasplusdb`.`operaciones` 
ADD CONSTRAINT `idvendedor`
  FOREIGN KEY (`idvendedor`)
  REFERENCES `ventasplusdb`.`vendedores` (`idvendedores`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION,
ADD CONSTRAINT `referencia`
  FOREIGN KEY (`referencia`)
  REFERENCES `ventasplusdb`.`productos` (`referencia`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;
