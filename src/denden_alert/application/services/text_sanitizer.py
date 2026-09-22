import re
import logging

logger = logging.getLogger("denden_alert.sanitizer")

class TextSanitizer:
    def __init__(self):
        # Expresiones regulares comunes
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)
        
    def _extract_wazuh_fields(self, text: str) -> str | None:
        """Intenta extraer solo los campos clave de una alerta de Wazuh."""
        if "ALERTA CRÍTICA WAZUH" not in text and "Regla:" not in text:
            return None
            
        try:
            regla = re.search(r'Regla:\s*(.*)', text)
            agente = re.search(r'Agente:\s*(.*)', text)
            ip = re.search(r'IP Atacante:\s*(.*)', text)
            rule_level = re.search(r'Rule Level:\s*(.*)', text)
            event_type = re.search(r'Event Type:\s*(.*)', text)
            
            parts = []
            parts.append("Alerta de seguridad detectada.")
            if regla: parts.append(f"Regla: {regla.group(1)}.")
            if agente: parts.append(f"Agente: {agente.group(1)}.")
            if ip: parts.append(f"IP Atacante: {ip.group(1)}.")
            if rule_level: parts.append(f"Nivel de regla: {rule_level.group(1)}.")
            if event_type: parts.append(f"Tipo de evento: {event_type.group(1)}.")
            
            if len(parts) > 1:
                return " ".join(parts)
        except Exception as e:
            logger.error(f"Error parseando alerta Wazuh: {e}")
        return None

    def sanitize(self, text: str) -> str:
        """Limpia el texto para que el motor TTS lo lea de forma más natural."""
        if not text:
            return ""
            
        # 1. Intentar extracción específica si es Wazuh
        wazuh_summary = self._extract_wazuh_fields(text)
        if wazuh_summary:
            text = wazuh_summary
            
        # 2. Eliminar emojis
        text = self.emoji_pattern.sub('', text)
            
        # 3. Reemplazar URLs por "enlace"
        text = self.url_pattern.sub(' enlace ', text)
        
        # 4. Eliminar menciones y hashtags
        text = text.replace('@', '')
        text = text.replace('#', '')
        
        # 5. Eliminar caracteres repetidos
        text = re.sub(r'(.)\1{3,}', r'\1\1', text)
        
        # 6. Reemplazar saltos de línea con puntos
        text = text.replace('\n', '. ')
        
        # 7. Limpieza de espacios
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
