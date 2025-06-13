# controlador.py - Controlador del patrón MVC
# Maneja la comunicación entre el modelo y la vista

class DescargadorControlador:
    """
    Controlador que coordina la comunicación entre el modelo y la vista
    """
    
    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista
        
        # Establece la referencia del controlador en la vista
        self.vista.establecer_controlador(self)
        
        # Configura los callbacks del modelo
        self.modelo.establecer_callbacks(
            progreso=self._callback_progreso,
            completado=self._callback_completado,
            error=self._callback_error
        )
        
        # Establece el directorio inicial en la vista
        self.vista.establecer_directorio_inicial(self.modelo.directorio_descarga)
        
    def obtener_informacion_video(self, url):
        """
        Solicita información del video al modelo y la envía a la vista
        """
        # Primero valida la URL
        if not self.modelo.validar_url(url):
            self.vista.mostrar_error("La URL no es válida o no es compatible")
            return
            
        # Obtiene la información del video
        info = self.modelo.obtener_informacion_video(url)
        
        # Envía la información a la vista
        self.vista.mostrar_informacion_video(info)
        
        if not info:
            self.vista.mostrar_error("No se pudo obtener información del video")
            
    def cambiar_directorio_descarga(self, directorio):
        """
        Cambia el directorio de descarga en el modelo
        """
        self.modelo.establecer_directorio_descarga(directorio)
        
    def descargar_video(self, url, formato, calidad):
        """
        Inicia la descarga de video
        """
        # Valida la URL antes de descargar
        if not self.modelo.validar_url(url):
            self.vista.mostrar_error("La URL no es válida o no es compatible")
            return
            
        # Inicia el progreso en la vista
        self.vista.iniciar_progreso()
        
        # Solicita la descarga al modelo
        self.modelo.descargar_video(url, formato, calidad)
        
    def descargar_audio(self, url, formato_audio):
        """
        Inicia la descarga de audio
        """
        # Valida la URL antes de descargar
        if not self.modelo.validar_url(url):
            self.vista.mostrar_error("La URL no es válida o no es compatible")
            return
            
        # Inicia el progreso en la vista
        self.vista.iniciar_progreso()
        
        # Solicita la descarga al modelo
        self.modelo.descargar_audio(url, formato_audio)
        
    # === CALLBACKS DEL MODELO ===
    
    def _callback_progreso(self, porcentaje, velocidad, tiempo_restante):
        """
        Callback que recibe actualizaciones de progreso del modelo
        """
        self.vista.actualizar_progreso(porcentaje, velocidad, tiempo_restante)
        
    def _callback_completado(self, archivo):
        """
        Callback que recibe notificación cuando la descarga se completa
        """
        self.vista.mostrar_completado(archivo)
        
    def _callback_error(self, mensaje_error):
        """
        Callback que recibe notificaciones de error del modelo
        """
        self.vista.mostrar_error(mensaje_error)