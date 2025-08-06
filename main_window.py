import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QDockWidget, QLabel, 
                             QFrame, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QFont
import random

class HMI_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUI()
        self.create_menus()
        self.create_status_bar()
        self.setup_data_simulation()  # Simulador temporal
        
    def setupUI(self):
        """Configuración básica de la ventana"""
        self.setWindowTitle("Banco de Pruebas Turbojet - HMI v1.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # DASHBOARD CENTRAL (en lugar del widget simple)
        self.create_central_dashboard()
        
        # Crear paneles acoplables
        self.create_dock_panels()
        
    def create_central_dashboard(self):
        """Crear el dashboard principal con los 4 parámetros críticos"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal del dashboard
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # TÍTULO DEL DASHBOARD
        title = QLabel("PARÁMETROS PRINCIPALES DEL MOTOR")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title)
        
        # LAYOUT GRID PARA LOS 4 PARÁMETROS
        parameters_layout = QGridLayout()
        parameters_layout.setSpacing(15)
        
        # 1. TEMPERATURA EGT (Posición 0,0 - Grande, Crítico)
        self.temp_widget = self.create_parameter_widget(
            "TEMPERATURA EGT", "0°C", "#e74c3c", "72px"
        )
        
        # 2. RPM (Posición 0,1 - Grande)
        self.rpm_widget = self.create_parameter_widget(
            "RPM", "0", "#3498db", "72px"
        )
        
        # 3. PRESIÓN (Posición 1,0 - Mediano)
        self.pressure_widget = self.create_parameter_widget(
            "PRESIÓN", "0.0 Bar", "#27ae60", "48px"
        )
        
        # 4. ESTADO GENERAL (Posición 1,1 - Estado)
        self.status_widget = self.create_status_widget()
        
        # Agregar widgets al grid
        parameters_layout.addWidget(self.temp_widget, 0, 0)
        parameters_layout.addWidget(self.rpm_widget, 0, 1)
        parameters_layout.addWidget(self.pressure_widget, 1, 0)
        parameters_layout.addWidget(self.status_widget, 1, 1)
        
        # Configurar tamaños relativos
        parameters_layout.setRowStretch(0, 2)  # Fila superior más grande
        parameters_layout.setRowStretch(1, 1)  # Fila inferior más pequeña
        
        main_layout.addLayout(parameters_layout)
        
        # BARRA DE INFORMACIÓN ADICIONAL
        info_bar = QLabel("Sistema iniciado - Esperando datos del STM32")
        info_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_bar.setStyleSheet("""
            QLabel {
                background-color: #f39c12;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(info_bar)
        
    def create_parameter_widget(self, title, initial_value, color, font_size):
        """Crear widget para un parámetro individual"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.Box)
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 3px solid {color};
                border-radius: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Título del parámetro
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
        """)
        
        # Valor del parámetro
        value_label = QLabel(initial_value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {font_size};
                font-weight: bold;
                font-family: 'Consolas', 'Monaco', monospace;
            }}
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        # Guardar referencia al label del valor para actualizarlo
        widget.value_label = value_label
        
        return widget
        
    def create_status_widget(self):
        """Crear widget de estado general"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.Box)
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 3px solid #95a5a6;
                border-radius: 15px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Título
        title_label = QLabel("ESTADO DEL SISTEMA")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 15px;
            }
        """)
        
        # Estados individuales
        self.motor_status = QLabel("MOTOR: DETENIDO")
        self.motor_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.motor_status.setStyleSheet("""
            QLabel {
                background-color: #e74c3c;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
                margin: 2px;
            }
        """)
        
        self.fuel_status = QLabel("COMBUSTIBLE: OK")
        self.fuel_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fuel_status.setStyleSheet("""
            QLabel {
                background-color: #27ae60;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 6px;
                border-radius: 5px;
                margin: 2px;
            }
        """)
        
        self.emergency_status = QLabel("EMERGENCIA: INACTIVA")
        self.emergency_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emergency_status.setStyleSheet("""
            QLabel {
                background-color: #95a5a6;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 6px;
                border-radius: 5px;
                margin: 2px;
            }
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(self.motor_status)
        layout.addWidget(self.fuel_status)
        layout.addWidget(self.emergency_status)
        
        return widget
    
    def create_dock_panels(self):
        """Crear paneles acoplables (mismo código anterior)"""
        # PANEL 1: Gráficas en Tiempo Real
        self.dock_graficas = QDockWidget("Gráficas en Tiempo Real", self)
        graficas_content = QWidget()
        graficas_layout = QVBoxLayout(graficas_content)
        graficas_layout.addWidget(QLabel("Aquí irán las gráficas de:\n• Temperatura vs Tiempo\n• Presión vs Tiempo\n• RPM vs Tiempo\n• Flujo de combustible"))
        self.dock_graficas.setWidget(graficas_content)
        
        # PANEL 2: Controles de Operación
        self.dock_controles = QDockWidget("Controles de Operación", self)
        controles_content = QWidget()
        controles_layout = QVBoxLayout(controles_content)
        controles_layout.addWidget(QLabel("Aquí irán:\n• Botón Start/Stop\n• Control de potencia\n• Configuraciones\n• Botón de emergencia"))
        self.dock_controles.setWidget(controles_content)
        
        # PANEL 3: Datos Detallados
        self.dock_datos = QDockWidget("Datos Detallados", self)
        datos_content = QWidget()
        datos_layout = QVBoxLayout(datos_content)
        datos_layout.addWidget(QLabel("Aquí irán:\n• Temperatura de admisión\n• Temperatura de gases\n• Presión diferencial\n• Vibración\n• Flujo másico"))
        self.dock_datos.setWidget(datos_content)
        
        # PANEL 4: Alarmas y Logs
        self.dock_alarmas = QDockWidget("Alarmas y Logs", self)
        alarmas_content = QWidget()
        alarmas_layout = QVBoxLayout(alarmas_content)
        alarmas_layout.addWidget(QLabel("Aquí irán:\n• Alarmas activas\n• Historial de eventos\n• Registro de operación\n• Alertas de mantenimiento"))
        self.dock_alarmas.setWidget(alarmas_content)
        
        # Configurar posiciones
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_graficas)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_controles)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_datos)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_alarmas)
        
        # Configurar propiedades
        for dock in [self.dock_graficas, self.dock_controles, self.dock_datos, self.dock_alarmas]:
            dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | 
                            QDockWidget.DockWidgetFeature.DockWidgetFloatable | 
                            QDockWidget.DockWidgetFeature.DockWidgetClosable)
            dock.setStyleSheet("""
                QDockWidget::title {
                    background-color: #34495e;
                    color: white;
                    padding: 8px;
                    font-weight: bold;
                    border-radius: 5px;
                }
            """)
    
    def setup_data_simulation(self):
        """Configurar simulación temporal de datos"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard_values)
        self.timer.start(1000)  # Actualizar cada segundo
        
        # Variables para simulación
        self.sim_temp = 20
        self.sim_rpm = 0
        self.sim_pressure = 1.0
        self.sim_motor_running = False
        
    def update_dashboard_values(self):
        """Actualizar valores del dashboard (simulación temporal)"""
        # Simular datos variables
        if self.sim_motor_running:
            self.sim_temp += random.uniform(-5, 10)
            self.sim_temp = max(200, min(450, self.sim_temp))
            
            self.sim_rpm += random.uniform(-200, 300)
            self.sim_rpm = max(5000, min(15000, self.sim_rpm))
            
            self.sim_pressure += random.uniform(-0.1, 0.2)
            self.sim_pressure = max(1.0, min(3.0, self.sim_pressure))
        else:
            # Motor parado - valores bajos
            self.sim_temp = max(20, self.sim_temp - 2)
            self.sim_rpm = max(0, self.sim_rpm - 100)
            self.sim_pressure = max(1.0, self.sim_pressure - 0.05)
        
        # Actualizar displays
        self.temp_widget.value_label.setText(f"{self.sim_temp:.0f}°C")
        self.rpm_widget.value_label.setText(f"{self.sim_rpm:.0f}")
        self.pressure_widget.value_label.setText(f"{self.sim_pressure:.2f} Bar")
        
        # Cambiar colores según valores críticos
        if self.sim_temp > 400:
            self.temp_widget.value_label.setStyleSheet(self.temp_widget.value_label.styleSheet() + "color: #c0392b;")
        
        # Simular cambio de estado del motor cada 10 segundos
        if random.randint(1, 10) == 1:
            self.sim_motor_running = not self.sim_motor_running
            if self.sim_motor_running:
                self.motor_status.setText("MOTOR: FUNCIONANDO")
                self.motor_status.setStyleSheet(self.motor_status.styleSheet().replace("#e74c3c", "#27ae60"))
            else:
                self.motor_status.setText("MOTOR: DETENIDO")
                self.motor_status.setStyleSheet(self.motor_status.styleSheet().replace("#27ae60", "#e74c3c"))
    
    def create_menus(self):
        """Crear menús (código anterior simplificado)"""
        menubar = self.menuBar()
        
        # Menú Ver
        ver_menu = menubar.addMenu("Ver")
        
        reset_action = QAction("Resetear Dashboard", self)
        reset_action.triggered.connect(self.reset_dashboard_values)
        ver_menu.addAction(reset_action)
    
    def create_status_bar(self):
        """Crear barra de estado"""
        status_bar = self.statusBar()
        status_bar.showMessage("Dashboard iniciado - Modo simulación activo")
        
        # Indicador de conexión
        connection_label = QLabel("● SIM")
        connection_label.setStyleSheet("color: orange; font-size: 16px; font-weight: bold;")
        status_bar.addPermanentWidget(connection_label)
    
    def reset_dashboard_values(self):
        """Resetear valores del dashboard"""
        self.sim_temp = 20
        self.sim_rpm = 0
        self.sim_pressure = 1.0
        self.sim_motor_running = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = HMI_MainWindow()
    ventana.show()
    sys.exit(app.exec())