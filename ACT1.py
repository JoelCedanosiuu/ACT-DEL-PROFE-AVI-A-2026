import sqlite3
import os

# ==========================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ==========================================

DB = "database/empleados_acme.db"


def conectar():
    os.makedirs("database", exist_ok=True)
    return sqlite3.connect(DB)


# ==========================================
# CREACIÓN DE LA BASE DE DATOS
# ==========================================

def crear_bd():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empleado (
            curp TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            calle TEXT,
            colonia TEXT,
            telefono TEXT,
            edad INTEGER,
            sueldo_mensual REAL
        )
    """)

    conexion.commit()
    conexion.close()


# ==========================================
# 1. ALTAS DE EMPLEADOS
# ==========================================

def alta_empleado():
    print("\n===== ALTA DE EMPLEADO =====")

    curp = input("CURP (18 caracteres): ").strip().upper()
    nombre = input("Nombre: ").strip()
    apellido = input("Apellido: ").strip()

    if not curp or not nombre or not apellido:
        print("\n[AVISO] El CURP, el nombre y el apellido son obligatorios.")
        return

    calle = input("Calle: ").strip()
    colonia = input("Colonia: ").strip()
    telefono = input("Teléfono: ").strip()
    
    edad_str = input("Edad: ").strip()
    try:
        edad = int(edad_str) if edad_str else 0
    except ValueError:
        edad = 0

    sueldo_str = input("Sueldo mensual: ").strip()
    try:
        sueldo_mensual = float(sueldo_str) if sueldo_str else 0.0
    except ValueError:
        sueldo_mensual = 0.0

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO empleado (
                curp, nombre, apellido, calle,
                colonia, telefono, edad, sueldo_mensual
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            curp, nombre, apellido, calle,
            colonia, telefono, edad, sueldo_mensual
        ))

        conexion.commit()
        print("\n¡Empleado registrado correctamente!")

    except sqlite3.IntegrityError:
        print("\n[ERROR] Ya existe un empleado registrado con ese CURP.")

    except sqlite3.Error as error:
        print("\n[ERROR] Error al registrar al empleado:", error)

    finally:
        conexion.close()


# ==========================================
# 2. BAJAS DE EMPLEADOS
# ==========================================

def baja_empleado():
    print("\n===== BAJA DE EMPLEADO =====")

    curp = input("CURP del empleado a eliminar: ").strip().upper()

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT * FROM empleado
            WHERE curp = ?
        """, (curp,))

        empleado = cursor.fetchone()

        if empleado is None:
            print("No se encontró un empleado con ese CURP.")
            return

        print("\nDatos del empleado:")
        print("CURP:", empleado[0])
        print("Nombre:", empleado[1])
        print("Apellido:", empleado[2])
        print("Calle:", empleado[3] or "N/D")
        print("Colonia:", empleado[4] or "N/D")
        print("Teléfono:", empleado[5] or "N/D")
        print("Edad:", empleado[6] if empleado[6] is not None else "N/D")
        sueldo = f"${empleado[7]:.2f}" if empleado[7] is not None else "$0.00"
        print("Sueldo mensual:", sueldo)

        confirmacion = input(
            "\n¿Desea eliminar este empleado? (S/N): "
        ).strip().upper()

        if confirmacion == "S":
            cursor.execute("""
                DELETE FROM empleado
                WHERE curp = ?
            """, (curp,))

            conexion.commit()
            print("Empleado eliminado correctamente.")
        else:
            print("Operación cancelada.")

    except sqlite3.Error as error:
        print("Error al eliminar al empleado:", error)

    finally:
        conexion.close()


# ==========================================
# 3. MODIFICACIONES DE EMPLEADOS
# ==========================================

def modificar_empleado():
    print("\n===== MODIFICACIÓN DE EMPLEADO =====")

    curp = input("CURP del empleado a modificar: ").strip().upper()

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT nombre, apellido, calle, colonia,
                   telefono, edad, sueldo_mensual
            FROM empleado
            WHERE curp = ?
        """, (curp,))

        empleado = cursor.fetchone()

        if empleado is None:
            print("No se encontró un empleado con ese CURP.")
            return

        print("\nIngrese los nuevos datos.")
        print("Presione ENTER para conservar el dato actual.")

        nombre = input(f"Nombre [{empleado[0]}]: ").strip()
        apellido = input(f"Apellido [{empleado[1]}]: ").strip()
        calle = input(f"Calle [{empleado[2] or ''}]: ").strip()
        colonia = input(f"Colonia [{empleado[3] or ''}]: ").strip()
        telefono = input(f"Teléfono [{empleado[4] or ''}]: ").strip()
        
        edad_str = input(f"Edad [{empleado[5]}]: ").strip()
        sueldo_str = input(f"Sueldo mensual [{empleado[6]}]: ").strip()

        nombre = nombre or empleado[0]
        apellido = apellido or empleado[1]
        calle = calle or empleado[2] or ""
        colonia = colonia or empleado[3] or ""
        telefono = telefono or empleado[4] or ""
        
        try:
            edad = int(edad_str) if edad_str else empleado[5]
        except ValueError:
            edad = empleado[5]

        try:
            sueldo_mensual = float(sueldo_str) if sueldo_str else empleado[6]
        except ValueError:
            sueldo_mensual = empleado[6]

        cursor.execute("""
            UPDATE empleado
            SET nombre = ?,
                apellido = ?,
                calle = ?,
                colonia = ?,
                telefono = ?,
                edad = ?,
                sueldo_mensual = ?
            WHERE curp = ?
        """, (
            nombre, apellido, calle, colonia,
            telefono, edad, sueldo_mensual, curp
        ))

        conexion.commit()
        print("\n¡Empleado modificado correctamente!")

    except sqlite3.Error as error:
        conexion.rollback()
        print("Error al modificar al empleado:", error)

    finally:
        conexion.close()


# ==========================================
# 4. CONSULTA DE TODA LA TABLA
# ==========================================

def consultar_todos():
    print("\n===== LISTADO DE EMPLEADOS (ACME) =====")

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT curp, nombre, apellido, calle,
                   colonia, telefono, edad, sueldo_mensual
            FROM empleado
            ORDER BY apellido, nombre
        """)

        empleados = cursor.fetchall()

        if not empleados:
            print("No hay empleados registrados en la base de datos.")
            return

        for emp in empleados:
            print("-" * 50)
            print("CURP:", emp[0])
            print("Nombre:", emp[1])
            print("Apellido:", emp[2])
            print("Calle:", emp[3] or "N/D")
            print("Colonia:", emp[4] or "N/D")
            print("Teléfono:", emp[5] or "N/D")
            print("Edad:", emp[6] if emp[6] is not None else "N/D")
            sueldo = f"${emp[7]:.2f}" if emp[7] is not None else "$0.00"
            print("Sueldo mensual:", sueldo)

        print("-" * 50)
        print("Total de empleados:", len(empleados))

    except sqlite3.Error as error:
        print("Error al consultar los empleados:", error)

    finally:
        conexion.close()


# ==========================================
# 5. CONSULTA POR CURP
# ==========================================

def consultar_curp():
    print("\n===== CONSULTA POR CURP =====")

    curp = input("Ingrese el CURP a buscar: ").strip().upper()

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT curp, nombre, apellido, calle,
                   colonia, telefono, edad, sueldo_mensual
            FROM empleado
            WHERE curp = ?
        """, (curp,))

        emp = cursor.fetchone()

        if emp:
            print("\n===== DATOS DEL EMPLEADO =====")
            print("CURP:", emp[0])
            print("Nombre:", emp[1])
            print("Apellido:", emp[2])
            print("Calle:", emp[3] or "N/D")
            print("Colonia:", emp[4] or "N/D")
            print("Teléfono:", emp[5] or "N/D")
            print("Edad:", emp[6] if emp[6] is not None else "N/D")
            sueldo = f"${emp[7]:.2f}" if emp[7] is not None else "$0.00"
            print("Sueldo mensual:", sueldo)
        else:
            print("No se encontró ningún empleado con ese CURP.")

    except sqlite3.Error as error:
        print("Error al consultar al empleado:", error)

    finally:
        conexion.close()


# ==========================================
# 6. MENÚ PRINCIPAL
# ==========================================

def menu():
    while True:
        print("\n" + "=" * 45)
        print("    SISTEMA DE CONTROL DE EMPLEADOS ACME")
        print("=" * 45)
        print("1. Alta de empleados")
        print("2. Baja de empleados")
        print("3. Modificación de empleados")
        print("4. Consulta de toda la tabla")
        print("5. Consulta por CURP")
        print("6. Salir del sistema")
        print("=" * 45)

        opcion = input("Seleccione una opción (1-6): ").strip()

        if opcion == "1":
            alta_empleado()

        elif opcion == "2":
            baja_empleado()

        elif opcion == "3":
            modificar_empleado()

        elif opcion == "4":
            consultar_todos()

        elif opcion == "5":
            consultar_curp()

        elif opcion == "6":
            print("\nSaliendo del sistema...")
            print("Gracias por utilizar el sistema.")
            break

        else:
            print("\nOpción inválida. Seleccione un número del 1 al 6.")


# ==========================================
# INICIO DEL PROGRAMA
# ==========================================

if __name__ == "__main__":
    crear_bd()
    menu()