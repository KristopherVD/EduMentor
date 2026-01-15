# Agente Tutor Inteligente basado en LLM

## Descripción general
Este proyecto implementa un agente tutor inteligente capaz de generar cursos y evaluaciones dinámicas a partir de documentos académicos en formato PDF, utilizando modelos de lenguaje de gran escala (LLMs) mediante Google Gemini y Google ADK.

La aplicación está desarrollada como un sistema web utilizando Flask y una base de datos SQLite para la gestión de usuarios y documentos.

---

## Autenticación y credenciales

Actualmente, el sistema utiliza un esquema de autenticación **simplificado**, definido de la siguiente manera:

- Todas las cuentas de usuario utilizan la contraseña por defecto: `0000`
- La contraseña **no es modificable** desde la interfaz actual

Esta decisión se tomó con fines académicos y de prototipado rápido, priorizando la funcionalidad principal del agente sobre la seguridad del sistema.

### Trabajo futuro
Como trabajo futuro, se propone:
- Implementar hash seguro de contraseñas
- Permitir cambio de contraseña por usuario
- Integrar un sistema de autenticación más robusto

---

## Requisitos
- Python 3.10 o superior
- Flask
- sqlite3
- Google ADK
- Gemini API

---

## Ejecución
```bash
python app.py
