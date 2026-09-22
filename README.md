# DenDen-Alert 🐌🚨

**DenDen-Alert** es un servicio local escrito en Python para monitorear mensajes de grupos específicos de Telegram, filtrarlos inteligentemente y reproducirlos en voz alta mediante el motor de síntesis de voz (TTS) nativo de tu sistema operativo (SAPI5 en Windows). 

Está diseñado específicamente para su uso en entornos SOC (Security Operations Center) donde alertas críticas (como eventos de Wazuh) deben ser escuchadas de forma inmediata por el analista, reduciendo el tiempo de reacción.

> El nombre se inspira en los *Den Den Mushi* de One Piece, caracoles utilizados para la transmisión de voz a largas distancias.

## Características

- **Autenticación Nativa de Usuario:** Utiliza MTProto (Telethon) para conectarse con tu propia cuenta de Telegram. No requiere crear bots ni agregarlos a los grupos.
- **Filtrado Avanzado (Clean Architecture):** Solo reacciona a los mensajes que cumplen con los filtros definidos (por chat, palabras clave, no-bots, etc.).
- **Procesamiento de Alertas de Wazuh:** Extrae automáticamente las partes más importantes de una alerta extensa de Wazuh y elimina emojis o relleno innecesario.
- **Cola de Reproducción con Prioridad y Deduplicación:** Evita que el sistema lea el mismo mensaje repetido y procesa múltiples alertas en orden.
- **100% Local y Privado:** No utiliza APIs de terceros (como Google o Azure) para la síntesis de voz, sino que usa las voces de Windows instaladas localmente en tu sistema a través de `pyttsx3`.

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu_usuario/DenDen-Alert.git
   cd DenDen-Alert
   ```

2. Crea y activa un entorno virtual (Python 3.12+):
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -e .
   ```

## Configuración

1. **Credenciales de Telegram:**  
   Obtén tu `API_ID` y `API_HASH` en [my.telegram.org](https://my.telegram.org).
   Renombra el archivo `.env.example` a `.env` y coloca tus credenciales:
   ```env
   TELEGRAM_API_ID=1234567
   TELEGRAM_API_HASH=abcdef123456...
   ```

2. **Configuración de Filtros (YAML):**  
   Renombra `config/config.example.yaml` a `config/config.yaml`.
   Configura el chat de origen y las palabras clave, por ejemplo:
   ```yaml
   telegram:
     chats:
       - "Alertas SOC"

   filters:
     keywords:
       - "ALERTA CRÍTICA WAZUH"
     users: []
     case_sensitive: false
   
   tts:
     rate: 1.0
     volume: 1.0
   ```

## Uso

Para iniciar el sistema de monitoreo, simplemente ejecuta:

```bash
python -m denden_alert start
```

La primera vez que lo ejecutes, Telethon te pedirá que introduzcas tu número de teléfono y el código de verificación de Telegram para autenticar el dispositivo.

## Mejorar la voz local en Windows

Por defecto, Windows incluye voces de síntesis (TTS) muy básicas. Si deseas una voz mucho más fluida, puedes instalar un nuevo paquete de voz oficial (y gratis) en Windows 10/11:

1. Ve a **Configuración** > **Hora e idioma** > **Voz**.
2. En la sección "Administrar voces", haz clic en **Agregar voces**.
3. Busca *Español (México)* o *Español (España)*, instálalo y selecciónalo como predeterminado.
4. Reinicia DenDen-Alert.

## Arquitectura y Logs

El proyecto utiliza **Clean Architecture** separando claramente la lógica de negocio (`domain`), los casos de uso (`application`) y los detalles técnicos (`infrastructure`). 

Los logs de la ejecución se muestran en la consola y se guardan automáticamente en `logs/denden.log` para futuras auditorías o debugging.
