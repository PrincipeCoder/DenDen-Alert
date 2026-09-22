# Implementación de Piper TTS (Local y Fluido)

Este plan detalla los pasos para reemplazar `pyttsx3` con `piper-tts`, manteniendo la aplicación 100% local y offline, pero con una voz neuronal muy superior.

## User Review Required

> [!WARNING]
> **Sobre el Hardware de Audio (Linux):** Al usar Piper TTS, el programa generará un archivo de audio WAV y usará `aplay` para reproducirlo en Fedora. Si sigues recibiendo el error `aplay: audio open error: El host no está operativo`, significa que tu servidor Fedora no tiene tarjeta de sonido (o tu usuario `root` no tiene permisos). Piper **no arreglará la falta de hardware de sonido**, pero sí te dará una voz fluida si solucionas el tema de los parlantes o si ejecutas esto en un servidor que sí tenga salida de audio física.

## Proposed Changes

### Dependencias
#### [MODIFY] pyproject.toml
- Reemplazar `pyttsx3>=2.90` con `piper-tts>=1.2.0`.

### Infraestructura (TTS y Audio)
#### [NEW] src/denden_alert/infrastructure/tts/piper_tts.py
- Crear `PiperTTSEngine` que implemente `TTSEnginePort`.
- Lógica para verificar si existe el modelo de voz `.onnx` localmente. Si no existe, lo descargará automáticamente de HuggingFace en el primer inicio (solo ~30MB) y luego trabajará 100% offline.

#### [MODIFY] src/denden_alert/infrastructure/audio/player.py
- Modificar `LocalAudioPlayer` para que sea multiplataforma:
  - En Windows: usará la librería estándar `winsound` (que reproduce WAV nativamente).
  - En Linux: usará un `subprocess` para llamar al comando `aplay` nativo de ALSA.

### Interfaces
#### [MODIFY] src/denden_alert/interfaces/cli.py
- Importar y usar `PiperTTSEngine` en el bloque de inyección de dependencias.

## Verification Plan
1. Ejecutar en Windows o Linux para asegurar que el modelo se descargue correctamente si no existe.
2. Confirmar que Piper genere el audio y el `LocalAudioPlayer` lo reproduzca correctamente (si el hardware lo permite).
