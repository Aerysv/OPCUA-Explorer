# OPCUA-Explorer

Una GUI simple que, de momento, sirve para explorar el espacio de nombres de un servidor OPC-UA.

Por implementar:
1. Leer fichero de configuración de Telegraf. Verficar si el servidor OPC indicado está configurado.
2. Detectar que Elementos fueron seleccionados en QTreeWidget.
```
  def vrfs_selected(self):
    iterator = QtGui.QTreeWidgetItemIterator(self.tree, QtGui.QTreeWidgetItemIterator.Checked)
    while iterator.value():
        item = iterator.value()
        print (item.text(0))    
        iterator += 1
```
3. Construir una sección configuración de Telegraf a partir de (2.).
4. Editar el fichero de configuración de Telegraf y reiniciar el servicio
