import sys
import Conexion_UA
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem
import asyncio
from asyncua import Client
'''
Aplicación que se conecta a un servidor OPC-UA y muestra el especio de nombres
en un arbol.

El objetivo original era leer un fichero de configuración de Telegraf y
modificarlo. Y luego reiniciarlo para que los cambios se efectúen.
'''


class Ui(QtWidgets.QDialog):
    def __init__(self):
        # Call the inherited classes __init__ method
        super(Ui, self).__init__()
        uic.loadUi('prueba_ventanaui.ui', self)  # Load the .ui file
        # Entrada de texto
        self.URL = self.findChild(QtWidgets.QLineEdit, 'URL')
        # Labels
        self.Cajon_Tags = self.findChild(QtWidgets.QTreeWidget, 'Cajon_Tags')
        self.Exitoso = self.findChild(QtWidgets.QLabel, 'Exitoso')
        self.Exitoso.hide()  # Debe estar oculto por defecto
        # Checkbox
        self.CheckBox_EspacioNombres = self.findChild(
            QtWidgets.QCheckBox, 'EspacioNombresCompleto')
        # Botonoes
        self.Probar_Conexion = self.findChild(
            QtWidgets.QPushButton, 'Probar_Conexion')

        # Acciones
        self.Probar_Conexion.clicked.connect(self.Conectar)
        self.Cajon_Tags.itemExpanded.connect(self.Expandir)

        self.show()  # Show the GUI

    def Conectar(self):
        """Acciones que se ejecutan al oprimir el botón 'Probar Conexión'
        1. Obtener nodo raíz del servidor OPC-UA
        2. Hacer aparecer una imagen si la conexión se llevó a cabo
        3. Crear elemento raiz del árbol PyQt
        """
        self.Cajon_Tags.clear()
        # Entrada del usuario
        self.Server_URL = self.URL.text()
        self.CheckBox = self.CheckBox_EspacioNombres.isChecked()
        # Ejecución
        try:
            Root_Servidor = asyncio.run(
                Conexion_UA.obtener_root(self.Server_URL))

            self.Exitoso.show()

            Root_Item = QTreeWidgetItem(self.Cajon_Tags)
            Root_Item.setData(1, QtCore.Qt.UserRole, Root_Servidor)
            Root_Item.setText(0, 'Servidor')
            Root_Item.setFlags(Root_Item.flags() |
                               Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            Root_Item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)

            self.Explorar_NodoUA(Root_Servidor, Root_Item)

            Root_Item.setExpanded(True)
        except ConnectionRefusedError:
            QMessageBox.about(self, "Advertencia",
                              "No se pudo conectar con el servidor")
        except ValueError:
            QMessageBox.about(self, "Advertencia",
                              "La URL indicada no es correcta")

    def Expandir(self, item):
        """Acciones que se ejecutan al expandir un elemento del árbol PyQt
        1. Detectar el elemento que se seleccionó
        2. Borrar los hijos que pudieran estar asignados a él
        3. Recuperar el nodo OPC-UA asociado
        4. Buscar los hijos del nodo OPC-UA
        Args:
            item (PyQtWidgetItem): Objeto que se expandió en la GUI
        """
        Tree_Item = item
        Tree_Item.takeChildren()    # Impide que se repitan elementos del árbol
        Node_Servidor = Tree_Item.data(1, QtCore.Qt.UserRole)

        self.Explorar_NodoUA(Node_Servidor, Tree_Item)

    def Explorar_NodoUA(self, Root_Servidor, Root_Tree_Item):
        """Se conecta al servidor OPC-UA para explorar los hijos del
        nodo Root_Servidor

        Args:
            Root_Servidor (Node): Nodo OPC-UA a explorar
            Root_Tree_Item (QTreeWidgetItem): Versión PyQt del nodo
        """
        try:
            [Nodes, Nodes_Names, Parent_Nodes] = Conexion_UA.main(
                self.Server_URL, Root_Servidor)

            self.Expandir_Nodo(
                Root_Tree_Item, Nodes, Nodes_Names, Parent_Nodes)
        except ConnectionRefusedError:
            QMessageBox.about(self, "Advertencia",
                              "No se pudo conectar con el servidor")
        except ValueError:
            QMessageBox.about(self, "Advertencia",
                              "La URL indicada no es correcta")

    def Expandir_Nodo(self, Root_Tree_Item, Nodes, Nodes_Names, Parent_Nodes):
        """Lee la información obtenida del servidor OPC-UA y la agrega al
        arbol de PyQt.

        Args:
            Root_Tree_Item (QTreeWidget): Elemento Padre de QTreeWidget
            Nodes (Node): Nodos OPC-UA hijos de Root_Tree_Item
            Nodes_Names (list): Nombres de los nodos OPC-UA
            Parent_Nodes (list): Lista de booleanos para nodos con hijos
        """
        for i, tag in enumerate(Nodes):
            if Parent_Nodes[i] == 1:
                parent = QTreeWidgetItem(Root_Tree_Item)
                parent.setFlags(parent.flags() |
                                Qt.ItemIsTristate |
                                Qt.ItemIsUserCheckable |
                                Qt.ItemIsSelectable)
                parent.setData(1, QtCore.Qt.UserRole, tag)
                parent.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                parent.setText(0, Nodes_Names[i])
                parent.setText(1, str(Nodes[i]))
                if self.CheckBox:
                    # LLamada recursiva para explorar
                    # todo el espacio de nombres
                    self.Explorar_NodoUA(tag, parent)

            else:
                child = QTreeWidgetItem(Root_Tree_Item)
                child.setData(0, 0, tag)
                child.setText(0, Nodes_Names[i])
                child.setText(1, str(Nodes[i]))
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setCheckState(0, Qt.Unchecked)


app = QtWidgets.QApplication(sys.argv)
window = Ui()  # Create an instance of our class
app.exec_()  # Start the application
