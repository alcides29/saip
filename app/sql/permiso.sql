INSERT INTO app_permiso(nombre, categoria)
    VALUES ('Ver roles', 1),
	('Crear rol', 1),
	('Modificar rol', 1),
	('Eliminar rol', 1),
	('Asignar rol', 1),
	('Ver proyectos', 1),
	('Crear proyecto', 1),
	('Modificar proyecto', 1),
	('Eliminar proyecto', 1),
	('Ver usuarios', 1),
	('Crear usuario', 1),
	('Modificar usuario', 1),
	('Eliminar usuario', 1),
	('Ver tipos-artefacto', 1),
	('Crear tipo-artefacto', 1),
	('Modificar tipo-artefacto', 1),
	('Eliminar tipo-artefacto', 1),
	('Ver artefactos', 2),
	('Ver miembros', 2),
	('ABM miembros', 2),
	('ABM artefactos', 2),
	('Asignar roles', 2),
	('Generar LB', 2),
	('Revisar artefactos', 2),
	('Asignar tipo-artefacto fase', 2);
	
INSERT INTO app_rolpermiso(rol_id, permiso_id)
    VALUES (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9),
    (1, 10), (1, 11), (1, 12), (1, 13), (1, 14), (1, 15), (1, 16), (1, 17);

INSERT INTO app_rolpermiso(rol_id, permiso_id, fase_id)
    VALUES(2, 18, 1), (2, 18, 2), (2, 18, 3), (2, 19, 1), (2, 19, 2), (2, 19, 3), (2, 20, 1), (2, 20, 2), (2, 20, 3), (2, 21, 1), (2, 21, 2), (2, 21, 3), (2, 22, 1), (2, 22, 2), (2, 22, 3), (2, 23, 1), (2, 23, 2), (2, 23, 3), (2, 24, 1), (2, 24, 2), (2, 24, 3), (2, 25, 1), (2, 25, 2), (2, 25, 3);
