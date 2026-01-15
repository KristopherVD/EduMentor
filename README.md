# Agente Tutor Inteligente basado en LLM (EduMentor)

## Descripción general

Este proyecto implementa un **agente tutor inteligente** capaz de generar cursos personalizados y evaluaciones intermedias de forma dinámica a partir de documentos académicos en formato PDF. El sistema utiliza **Modelos de Lenguaje de Gran Escala (LLMs)** mediante la **API de Google Gemini**, integrados a través del **Google Agent Development Kit (ADK)**.

La aplicación está desarrollada como un sistema web utilizando **Flask** y una base de datos **SQLite** para la gestión de usuarios y documentos. El proyecto fue desarrollado con fines **académicos y experimentales**, como parte de la materia _Agentes Inteligentes_, explorando el uso de agentes basados en LLMs en contextos educativos.

---

## Características principales

- Carga de documentos académicos en formato PDF por usuario.
- Procesamiento del contenido del documento como contexto educativo.
- Generación automática de explicaciones temáticas.
- Generación de evaluaciones intermedias dinámicas.
- Retroalimentación básica de respuestas.
- Interfaz web accesible desde navegador.

---

## Autenticación y credenciales

Actualmente, el sistema utiliza un esquema de autenticación **simplificado**, definido de la siguiente manera:

- Las contraseñas de los usuarios están configuradas por defecto como `0000`.
- La modificación de contraseñas no está implementada en esta versión.

Esta decisión se tomó con fines **académicos y de prototipado rápido**, priorizando la funcionalidad principal del agente tutor inteligente sobre los mecanismos de seguridad.

> ⚠️ **Nota**  
> Este sistema **no está diseñado para uso en producción** ni para entornos con información sensible.

---

## Versiones y dependencias

Las siguientes versiones fueron utilizadas durante el desarrollo y pruebas del proyecto:

### Lenguaje y entorno
- **Python:** 3.10+

### Backend y servidor web
- **Flask:** 3.0.x
- **Werkzeug:** 3.0.x

### Base de datos
- **SQLite:** 3.x (incluida por defecto en Python)

### Procesamiento de documentos
- **PyPDF2:** 3.0.x  
  (Extracción de texto desde archivos PDF)

### Modelos de Lenguaje y agentes
- **Google Gemini API**
- **Google Agent Development Kit (ADK)**

### Librerías estándar de Python
- `os`
- `json`
- `uuid`
- `sqlite3`

> **Nota:** El funcionamiento del sistema depende de la disponibilidad y cuota de la API de Google Gemini.

---

## Notas importantes

- El proyecto es de carácter **académico** y fue desarrollado como **prototipo funcional**.
- La seguridad (manejo de contraseñas y credenciales) **no es prioritaria** en esta versión.
- La API de Gemini puede presentar interrupciones temporales, límites de uso o cambios en sus políticas.

---

## Trabajo futuro

Como trabajo futuro, se propone:

- Implementar almacenamiento de contraseñas con **hash seguro**.
- Permitir el **cambio de contraseña** por usuario.
- Integrar un sistema de **autenticación más robusto**.
- Mejorar la evaluación automática con retroalimentación adaptativa.
- Reducir la dependencia de un único proveedor de LLM.
- Añadir personalización del contenido basada en el desempeño del estudiante.

---

## Requisitos

- Python 3.10 o superior
- Flask
- sqlite3
- Google Agent Development Kit (ADK)
- API de Google Gemini

---

## Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/KristopherVD/EduMentor.git
cd EduMentor
