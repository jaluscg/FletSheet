# fletsheet

## Introducción

"fletsheet" es una aplicación que simula una hoja de cálculo, permitiendo a los usuarios introducir y manipular datos en una matriz de celdas. El proyecto está construido sobre el módulo "flet" y permite navegación entre diferentes vistas, la interacción con celdas mediante el teclado, y la evaluación de fórmulas simples.

## Características

1. **Navegación de páginas**: El proyecto permite la navegación entre diferentes vistas a través de la barra lateral.
2. **Interacción con la tabla**: Los usuarios pueden seleccionar celdas, desplazarse entre ellas con las teclas de flechas y introducir datos.
3. **Evaluación de fórmulas**: Las celdas admiten fórmulas básicas como `=SUM(A1,A2,...)` y `=ADD(A1,5,A2,...)`. Las referencias a otras celdas en las fórmulas se actualizan automáticamente al cambiar el valor de la celda referenciada o al pulsar enter.

## Cómo instalar

1. Clona el repositorio desde [este enlace](https://github.com/jaluscg/FletSheet).
2. Asegúrate de tener todas las dependencias necesarias instaladas.
3. Abre tu terminal y ejecuta `python main.py` para iniciar la aplicación.

## Ejemplo de cómo usar

A continuación, se presenta un GIF que muestra cómo interactuar con "fletsheet":

![Ejemplo de uso de fletsheet]()