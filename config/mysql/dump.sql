CREATE DATABASE usuaris;
USE usuaris;
CREATE TABLE usuaris (  id INT AUTO_INCREMENT,  nom VARCHAR(60) NOT NULL,  cognom VARCHAR(200),     PRIMARY KEY(id)     );
INSERT INTO usuaris (nom, cognom) values ("Pere", "Pi");
INSERT INTO usuaris (nom, cognom) values ("Pepito", "Palotes");