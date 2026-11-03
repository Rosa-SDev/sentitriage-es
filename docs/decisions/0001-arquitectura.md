# ADR 0001 — Arquitectura del prototipo de Fase II

- Estado: aceptada (2 de noviembre de 2026)
- Autores: Rosa Peña, Daniel Guzmán

## Contexto

El artículo de Fase I propone un agente que clasifica reseñas en español, calibra su
confianza y se abstiene cuando no está seguro, y que en el futuro se integrará en
Kandela (gateway + servicios Spring Boot, Admin en Angular, POS/KDS en React). Kandela
no tiene módulo de reseñas. El objeto de estudio de Sistemas Inteligentes es el agente
y su evaluación, no la plataforma.

Restricciones: cómputo gratuito (Google Colab para transformers), 1.839 tuits de
entrenamiento, demostración en vivo el 4 de noviembre y continuidad hasta la entrega
final de noviembre.

## Opciones evaluadas

| Opción | Ventaja | Problema |
|---|---|---|
| A. Motor/librería sola | Simple, reproducible | No demuestra uso práctico |
| B. API HTTP | Consumible por cualquier sistema | Sin interfaz no se ve en una sustentación |
| C. Aplicación web aparte | Visual | Un segundo proceso y otra tecnología que mantener |
| D. Dentro de Kandela | Contexto real | Acopla el modelo a Java/Angular y mezcla dos materias |
| E. Bot de Telegram / nube | Llamativo | No responde la pregunta de investigación; token, hosting y costo |

## Decisión

**A + B + C en un solo repositorio y un solo proceso:**

1. `src/sentitriage/`: librería con datos, percepción, modelos, calibración, política y
   evaluación. Es lo que se investiga y se evalúa offline.
2. `service/app.py`: microservicio FastAPI (`POST /classify`) que envuelve la librería.
3. `service/static/index.html`: demo web servida por el mismo servicio.

Kandela (D) se integra después como **consumidor** del servicio: una ruta en el API
gateway hacia `sentitriage:8000` y un módulo de reseñas que llama a `/classify` después
de guardar la reseña. No se modifica Kandela en esta fase.

Telegram y la nube (E) quedan fuera de la Fase II. Si sobra tiempo en la entrega
final, un despliegue gratuito del mismo contenedor (p. ej. Hugging Face Spaces) cuesta
poco porque el servicio ya es independiente.

## Consecuencias

- El backend de clasificación es intercambiable: `sentitriage.json` declara el tipo
  (`sklearn` o `transformers`), T y τ. Pasar del baseline a BETO no cambia el servicio.
- BETO y XLM-R se entrenan en Colab con `notebooks/02_finetune_transformers_colab.ipynb`
  porque el entorno local no tiene GPU ni acceso a Hugging Face.
- Todos los modelos se evalúan con el mismo `evaluate.py`, así las cifras son comparables.
