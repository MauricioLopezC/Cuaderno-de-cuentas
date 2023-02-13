from tkinter import ttk
from tkinter import *

import sqlite3

class libro:
    def __init__(self, window):
        self.wind = window
        self.wind.title("libro de cuentas")
        #creando un frame container
        frame = LabelFrame(self.wind, text="Agregar una cuenta")

        frame.grid(row = 0, column=0, columnspan=3, pady = 20)

        #Nombre de entrada de dato (cliente)
        Label(frame, text="Cliente: ").grid(row=1, column=0)
        self.cliente = Entry(frame)
        self.cliente.focus()
        self.cliente.grid(row=1, column=1)
        #Nombre de entrada de dato (producto)
        Label(frame, text= "Producto: ").grid(row=2, column=0)
        self.producto = Entry(frame)
        self.producto.grid(row=2,column=1)
        #Nombre de entrada de dato(precio)
        Label(frame, text="Precio: ").grid(row=3, column = 0)
        self.precio = Entry(frame)
        self.precio.grid(row=3, column=1)
        #boton de añadir datos
        boton = ttk.Button(frame, text="guardar datos", command=self.insertar_productos)
        boton.grid(row=4, columnspan= 2, sticky=W + E)
        #botones de borrar producto y editar producto
        boton_borrar = ttk.Button(text="Borrar Producto", command=self.borrar_producto)
        boton_borrar.grid(row=5, column=0, sticky=W+E)
        boton_editar = ttk.Button(text="Editar Producto", command=self.editar_producto)
        boton_editar.grid(row=5, column=1, sticky=W+E)
        #botones para agregar un cobro
        boton_cobrar = ttk.Button(text="Consultar Cuenta", command=self.consulta_cuenta)
        boton_cobrar.grid(row=6, columnspan=2, sticky=W+E)
        #mensajes
        self.mensaje=Label(text="", fg="blue")
        self.mensaje.grid(row=3, column=0, columnspan=2, sticky=W+E)

        #Tabla de visualización de datos insertados
        columns = ("cliente", "producto", "precio")
        self.tabla = ttk.Treeview(height=10, columns=columns, show="headings")
        self.tabla.grid(row=4,columnspan=2, column=0)
        self.tabla.heading("#1", text="CLIENTE", anchor = CENTER)
        self.tabla.heading("#2", text="PRODUCTO", anchor = CENTER)
        self.tabla.heading("#3", text="PRECIO", anchor = CENTER)

        self.get_product()

    #conexión a la base de datos
    nombre_db = "database.db"
    def run_query(self, query, parametros = ()):
        con = sqlite3.connect(self.nombre_db)
        cur = con.cursor()
        resultado = cur.execute(query, parametros)
        con.commit()
        return resultado

    def get_product(self):
        #obtener todos los datos de la tabla (no la database, sino la tabla treeview)
        datos = self.tabla.get_children()
        #eliminamos los que ya esten cargados
        for element in datos:
            self.tabla.delete(element)

        #consultando datos de la base de datos
        query = "SELECT * FROM productos"
        db_filas = self.run_query(query)
        #insertamos datos de la database en la treeview
        for fila in db_filas:
            self.tabla.insert("", index=0, values = (fila[1], fila[2], fila[3]))

    def insertar_productos(self):
        if self.validacion():
            query = "INSERT INTO productos VALUES(NULL, ?, ?, ?)"
            parametros = (self.cliente.get().upper(), self.producto.get(), self.precio.get())
            self.run_query(query, parametros)
            #modificamos el atributo text del objeto mensaje de la clase Label
            self.mensaje["text"] = (f"El producto {self.producto.get()}" +
            " ha sido añadido correctamente")
            self.cliente.delete(0, END)
            self.producto.delete(0, END)
            self.precio.delete(0, END)
        else:
            self.mensaje["text"] = "Ingresá todos los datos"
        self.get_product()
    def validacion(self):
        return (len(self.cliente.get()) !=0 and
                len(self.producto.get()) != 0 and
                len(self.precio.get()) != 0)

    def borrar_producto(self):
        try:
            prod = self.tabla.item(self.tabla.selection())["values"][1]
        except IndexError:
            self.mensaje["text"] = "Debes seleccionar un producto"
            return
        self.mensaje["text"] = ""
        prod = self.tabla.item(self.tabla.selection())["values"][1]
        cliente = self.tabla.item(self.tabla.selection())["values"][0]
        precio = self.tabla.item(self.tabla.selection())["values"][2]
        query = "DELETE FROM productos WHERE producto = ? and cliente = ? AND precio = ?"
        self.run_query(query, (prod, cliente, precio))
        self.mensaje["text"] = (f"Producto {prod} del cliente {cliente}" +
                        " ha sido eliminado correctamente")
        self.get_product()

    def editar_producto(self):
        self.mensaje["text"] = ""
        try:
            self.tabla.item(self.tabla.selection())["values"][1]
        except IndexError:
            self.mensaje["text"] = "Debes seleccionar un producto"
            return
        #nueva ventana de edición de producto
        ventana_edicion = Toplevel()
        ventana_edicion.title = "editar el producto".upper()
        Label(ventana_edicion, text="Nuevo Cliente").grid(row=0, column=1)
        entrada_cliente = Entry(ventana_edicion)
        entrada_cliente.grid(row=0, column=2)
        Label(ventana_edicion, text="Nuevo producto").grid(row = 2, column=1)
        entrada_producto = Entry(ventana_edicion)
        entrada_producto.grid(row = 2, column=2)
        Label(ventana_edicion, text="Nuevo precio").grid(row=3, column=1)
        entrada_precio = Entry(ventana_edicion)
        entrada_precio.grid(row=3, column=2)
        #boton para guardar los datos
        boton_guardar = Button(ventana_edicion, text="Guardar", command= lambda: self.guardar(
            ventana_edicion,
            entrada_cliente.get(),
            entrada_producto.get(),
            entrada_precio.get()
        ))
        boton_guardar.grid(row=5, column=2, sticky=W+E)

    def guardar(self, ventana_edicion, entrada_cliente, entrada_producto, entrada_precio):
        cliente_anterior = self.tabla.item(self.tabla.selection())["values"][0]
        producto_anterior = self.tabla.item(self.tabla.selection())["values"][1]
        precio_anterior = self.tabla.item(self.tabla.selection())["values"][2]
        query = ("UPDATE productos SET cliente=?, producto=?, precio=?" +
                 "WHERE cliente = ? AND producto = ? AND precio = ?")
        parametros = (entrada_cliente,
                      entrada_producto,
                      entrada_precio,
                      cliente_anterior,
                      producto_anterior,
                      precio_anterior)
        self.run_query(query, parametros)
        ventana_edicion.destroy()
        self.mensaje["text"] = "producto editado correctamente"
        self.get_product()

#    def cobro_cliente(self):
#        print("----.----")

    def consulta_cuenta(self):
        ventana_consulta = Toplevel()
        ventana_consulta.title = "Consulta de Cuenta"
        Label(ventana_consulta, text="Nombre del cliente").grid(row=0, column=0)
        entrada_cliente = Entry(ventana_consulta)
        entrada_cliente.grid(row=0, column=1)
        boton_buscar = ttk.Button(ventana_consulta,
                                  text="Buscar",
                                  command=lambda: self.buscar(
                                      entrada_cliente.get(),
                                      tabla_cliente,
                                      ventana_consulta
                                  ))
        boton_buscar.grid(row=1, columnspan=2, sticky=W+E)
        columns = ("producto", "precio")
        tabla_cliente = ttk.Treeview(ventana_consulta, height=10,columns=columns, show="headings")
        tabla_cliente.grid(row=3, column=0, columnspan=2)
        tabla_cliente.heading("#1", text="Producto", anchor=CENTER)
        tabla_cliente.heading("#2", text="Precio", anchor=CENTER)

    def buscar(self, cliente, tabla_cliente, ventana_consulta):
        msg = Label(ventana_consulta, text="", fg="blue")
        msg.grid(row=8, column = 0, columnspan = 2, sticky=W+E)
        #comprobamos si el cliente existe en la database
        validacion = self.run_query(
            """
            SELECT EXISTS(
             SELECT cliente
             FROM productos
             WHERE cliente=?)
            """,
            parametros=(cliente,)
        ).fetchone()
        if validacion[0] == 0:
            msg["text"] = "Cliente no encontrado"
            return
        msg["text"] = ""
        #si el usuario existe se procede a lenar la tabla
        #primero borramos los datos ya escritos de la tabla
        datos = tabla_cliente.get_children()
        for element in datos:
            tabla_cliente.delete(element)

        #Rellenando la tabla con el historial del ciente en particular
        query = "SELECT * FROM productos WHERE cliente = ?"
        parametros = (cliente,)
        db_filas = self.run_query(query, parametros)
        #insertamos datos de la databa21se en la treeview
        for fila in db_filas:
            tabla_cliente.insert("", index=0, values = (fila[2], fila[3]))
        #total de productos
        query = "SELECT SUM(precio) FROM productos WHERE cliente = ?"
        suma = self.run_query(query, parametros).fetchone()
        suma = suma[0]
        Label(ventana_consulta,
              text=f"Total: {suma:,}").grid(row=4, column=1, columnspan = 2)






if __name__ == "__main__":
    wind = Tk()
    application = libro(wind)
    wind.mainloop()
