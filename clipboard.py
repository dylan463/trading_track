import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                             QPushButton, QHBoxLayout, QFileDialog, QShortcut, 
                             QFrame, QSplitter)
from PyQt5.QtGui import QPixmap, QTransform, QKeySequence
from PyQt5.QtCore import Qt, pyqtSignal, QEvent

# def saveImage(self):
#     """Enregistre l'image affichée sous forme de fichier JPG."""
#     if self.original_pixmap:
#         options = QFileDialog.Options()
#         file_path, _ = QFileDialog.getSaveFileName(
#             self, "Enregistrer l'image", "", "Images JPG (*.jpg);;Tous les fichiers (*)", options=options
#         )
#         if file_path:
#             self.original_pixmap.save(file_path, "JPG")


class ScalableImageLabel(QLabel):
    selected = pyqtSignal(object)  # Signal pour indiquer quand le label est sélectionné
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 200)
        self.original_pixmap = None
        self.current_rotation = 0
        self.setScaledContents(False)
        self.setText("Glissez une image ici, utilisez Ctrl+V ou cliquez sur 'Importer une image'")
        self.setAlignment(Qt.AlignCenter)
        self.setFrameShape(QFrame.StyledPanel)
        
        # Variable pour savoir si cette zone est sélectionnée
        self.is_selected = False
        
        # Activer le drag and drop
        self.setAcceptDrops(True)
        
    def setPixmap(self, pixmap):
        self.original_pixmap = pixmap
        self.updatePixmap()
        
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
    
    def mousePressEvent(self, event):
        # Émettre un signal que ce label a été cliqué
        self.selected.emit(self)
        super().mousePressEvent(event)
            
    # Événements de drag and drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        # Émettre un signal que ce label a été sélectionné
        self.selected.emit(self)
        
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.load_image_from_file(file_path)
            
    def load_image_from_file(self, file_path):
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            self.current_rotation = 0  # Réinitialiser la rotation
            self.setPixmap(pixmap)
            return True
        return False

    def removeImage(self):
        """Supprime l'image actuellement affichée."""
        self.original_pixmap = None
        self.current_rotation = 0
        self.clear()  # Efface l'affichage de QLabel
        self.setText("Glissez une image ici, utilisez Ctrl+V ou cliquez sur 'Importer une image'")

    def setSelected(self, selected):
        self.is_selected = selected
        
        # Changer l'apparence en fonction de la sélection
        if selected:
            # Bordure bleue quand sélectionné
            self.setStyleSheet("border: 2px solid blue;")
        else:
            # Pas de bordure quand non sélectionné
            self.setStyleSheet("border: 1px solid gray;")

class ZoneContainer(QWidget):
    zone_selected = pyqtSignal(object)  # Signal pour indiquer quand cette zone est sélectionnée
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        # Créer la zone d'image
        self.image_label = ScalableImageLabel(self)
        
        # Connecter le signal du label
        self.image_label.selected.connect(self.on_label_selected)
        
        # Boutons spécifiques à la zone
        self.button_layout = QHBoxLayout()
        self.import_button = QPushButton("Importer")
        self.rotate_left_button = QPushButton("-90°")
        self.rotate_right_button = QPushButton("+90°")
        
        # Désactiver les boutons de rotation tant qu'aucune image n'est chargée
        self.rotate_left_button.setEnabled(False)
        self.rotate_right_button.setEnabled(False)
        
        # Ajouter les boutons au layout
        self.button_layout.addWidget(self.import_button)
        self.button_layout.addWidget(self.rotate_left_button)
        self.button_layout.addWidget(self.rotate_right_button)
        
        # Ajouter les widgets au layout principal
        self.layout.addWidget(self.image_label)
        self.layout.addLayout(self.button_layout)
        
        # Connecter les boutons aux fonctions
        self.import_button.clicked.connect(self.importImage)
        self.rotate_left_button.clicked.connect(self.rotateLeft)
        self.rotate_right_button.clicked.connect(self.rotateRight)
        
        # Variable pour stocker l'état de sélection
        self.is_selected = False
    
    def on_label_selected(self, label):
        # Émettre un signal que cette zone est sélectionnée ou désélectionnée
        self.zone_selected.emit(self)
        
    def importImage(self):
        # Émettre un signal que cette zone est sélectionnée
        self.zone_selected.emit(self)
        
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Importer une image", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;Tous les fichiers (*)",
            options=options
        )
        self.load_image_from_file(file_path)

    def load_image_from_file(self,file_path):
        if file_path:
            if self.image_label.load_image_from_file(file_path):
                self.rotate_left_button.setEnabled(self.is_selected)
                self.rotate_right_button.setEnabled(self.is_selected)
            else:
                self.image_label.setText("Erreur: Impossible de charger l'image")

    def rotateLeft(self):
        if self.is_selected:
            self.image_label.rotateImage(-90)
        
    def rotateRight(self):
        if self.is_selected:
            self.image_label.rotateImage(90)
    
    def paste_image_from_clipboard(self):
        if not self.is_selected:
            return False
            
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        # Vérifier si le presse-papiers contient une image
        if mime_data.hasImage():
            image = clipboard.image()
            pixmap = QPixmap.fromImage(image)
            if not pixmap.isNull():
                self.image_label.current_rotation = 0  # Réinitialiser la rotation
                self.image_label.setPixmap(pixmap)
                self.rotate_left_button.setEnabled(True)
                self.rotate_right_button.setEnabled(True)
                return True
            else:
                self.image_label.setText("Erreur: Image invalide dans le presse-papiers")
        else:
            self.image_label.setText("Aucune image dans le presse-papiers")
        return False
    
    def setSelected(self, selected):
        self.is_selected = selected
        self.image_label.setSelected(selected)
        
        # Activer/désactiver les boutons en fonction de la sélection
        self.import_button.setEnabled(selected)
        
        # Les boutons de rotation ne sont activés que si une image est chargée
        has_image = self.image_label.original_pixmap is not None
        self.rotate_left_button.setEnabled(selected and has_image)
        self.rotate_right_button.setEnabled(selected and has_image)



class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        
        # Créer un splitter horizontal pour les deux zones
        self.splitter = QSplitter(Qt.Vertical)
        
        # Créer les deux zones
        self.zone1 = ZoneContainer(self)
        self.zone2 = ZoneContainer(self)
        
        # Connecter les signaux de sélection de zone
        self.zone1.zone_selected.connect(self.toggle_zone_selection)
        self.zone2.zone_selected.connect(self.toggle_zone_selection)
        
        # Ajouter les zones au splitter
        self.splitter.addWidget(self.zone1)
        self.splitter.addWidget(self.zone2)
        
        # Définir les tailles initiales des zones
        self.splitter.setSizes([400, 400])
        
        # Garde une référence à la zone actuellement sélectionnée
        self.current_zone = None
        
        # Ajouter le splitter au layout principal
        main_layout.addWidget(self.splitter)
        
        # Raccourci clavier pour coller l'image
        paste_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_V), self)
        paste_shortcut.activated.connect(self.paste_image_from_clipboard)
        
        # Installer un filtre d'événements pour capturer les clics en dehors des zones
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        # Capturer les clics en dehors des zones
        if obj == self and event.type() == QEvent.MouseButtonPress:
            # Vérifier si le clic est en dehors des zones
            child_widget = self.childAt(event.pos())
            if child_widget is None or (child_widget != self.zone1 and child_widget != self.zone2):
                self.deselect_all_zones()
        return super().eventFilter(obj, event)
    
    def toggle_zone_selection(self, zone):
        if self.current_zone == zone:
            # Si la zone est déjà sélectionnée, la désélectionner
            zone.setSelected(False)
            self.current_zone = None
        else:
            # Désélectionner l'ancienne zone
            if self.current_zone:
                self.current_zone.setSelected(False)
                
            # Sélectionner la nouvelle zone
            zone.setSelected(True)
            self.current_zone = zone
    
    def deselect_all_zones(self):
        if self.current_zone:
            self.current_zone.setSelected(False)
            self.current_zone = None
    
    def reset_images(self):
        self.zone1.image_label.removeImage()
        self.zone2.image_label.removeImage()
        
 
    def paste_image_from_clipboard(self):
        # Coller l'image dans la zone actuellement sélectionnée
        if self.current_zone:
            self.current_zone.paste_image_from_clipboard()

# Exemple d'utilisation
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageViewer()
    ex.show()
    sys.exit(app.exec_())