#!/bin/bash

#1. otorgar permisos: chmod +x parahacertag.sh
#2. ejecutar el archivo: ./parahacertag.sh


# Obtén el último mensaje de commit
mensaje=$(git log -1 --pretty=%B)

# Crea una nueva etiqueta con el mensaje de commit como descripción
git tag -a v0.0.1 -m "$mensaje"

# Empuja la etiqueta al repositorio remoto
git push origin v0.0.1