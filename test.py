import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                           QPushButton, QHBoxLayout, QFileDialog)
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtCore import Qt

class ScalableImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(1, 1)
        self.original_pixmap = None
        self.current_rotation = 0
        self.setScaledContents(False)
        self.setText("Aucune image chargée. Cliquez sur 'Importer une image'.")
        self.setAlignment(Qt.AlignCenter)
        
    def setPixmap(self, pixmap):
        self.original_pixmap = pixmap
        super().setPixmap(pixmap)
        
    def resizeEvent(self, event):
        if self.original_pixmap:
            self.updatePixmap()
            
    def updatePixmap(self):
        if self.original_pixmap:
            # Appliquer la rotation à l'image originale
            transform = QTransform().rotate(self.current_rotation)
            rotated_pixmap = self.original_pixmap.transformed(transform, Qt.SmoothTransformation)
            
            # Redimensionner l'image rotative
            scaled_pixmap = rotated_pixmap.scaled(
                self.width(), self.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            super().setPixmap(scaled_pixmap)
            
    def rotateImage(self, angle):
        if self.original_pixmap:
            self.current_rotation = (self.current_rotation + angle) % 360
            self.updatePixmap()
        
class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Créer le layout principal
        main_layout = QVBoxLayout()
        
        # Créer notre QLabel personnalisé qui redimensionne automatiquement l'image
        self.label = ScalableImageLabel(self)
        
        # Centrer l'image dans le QLabel
        self.label.setAlignment(Qt.AlignCenter)
        
        # Créer un layout horizontal pour les boutons
        button_layout = QHBoxLayout()
        
        # Créer les boutons
        self.import_button = QPushButton("Importer une image")
        self.rotate_left_button = QPushButton("Rotation Gauche (-90°)")
        self.rotate_right_button = QPushButton("Rotation Droite (+90°)")
        
        # Désactiver les boutons de rotation tant qu'aucune image n'est chargée
        self.rotate_left_button.setEnabled(False)
        self.rotate_right_button.setEnabled(False)
        
        # Connecter les boutons aux fonctions
        self.import_button.clicked.connect(self.importImage)
        self.rotate_left_button.clicked.connect(self.rotateLeft)
        self.rotate_right_button.clicked.connect(self.rotateRight)
        
        # Ajouter les boutons au layout horizontal
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.rotate_left_button)
        button_layout.addWidget(self.rotate_right_button)
        
        # Ajouter les widgets au layout principal
        main_layout.addWidget(self.label)
        main_layout.addLayout(button_layout)
        
        # Définir le layout pour le widget
        self.setLayout(main_layout)
        
        # Définir le titre et la taille de la fenêtre
        self.setWindowTitle('Visualiseur d\'images - PyQt5')
        self.resize(800, 600)
        
        # Afficher la fenêtre
        self.show()
        
    def importImage(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Importer une image", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;Tous les fichiers (*)",
            options=options
        )
        
        if file_path:
            try:
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    self.label.current_rotation = 0  # Réinitialiser la rotation
                    self.label.setPixmap(pixmap)
                    # Activer les boutons de rotation
                    self.rotate_left_button.setEnabled(True)
                    self.rotate_right_button.setEnabled(True)
                else:
                    self.label.setText("Erreur: Impossible de charger l'image")
            except Exception as e:
                self.label.setText(f"Erreur: {str(e)}")
        
    def rotateLeft(self):
        self.label.rotateImage(-90)
        
    def rotateRight(self):
        self.label.rotateImage(90)

# Exécuter l'application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageViewer()
    sys.exit(app.exec_())