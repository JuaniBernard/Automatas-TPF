import cmd
from datetime import datetime
import re
import warnings
warnings.simplefilter('always', UserWarning)


class Trafico:
    # Definir menú del programa
    def menu_trafico(self):
        print('\n\n\t--REGISTROS DE TRÁFICO--\n\t(28/08/2019 - 04/10/2019)')
        print('\n1. Mostrar direcciones MAC AP.')
        print('\n2. Mostrar direcciones MAC Cliente.')
        print('\n3. Mostrar usuarios.')
        print('\n4. Mostrar AP con mayor tráfico entre dos fechas.')
        print('\n   Salir (otra tecla)')
        return input('\n--> Elija una opción: ')

    # Mostrar y escribir en archivos de texto las direcciones MAC y usuarios
    def mostrar_aps(self):
        with open('aps_mac_output.txt', 'w') as outfile:
            outfile.write('-Lista de MAC AP (%d en total):\n' % len(aps_mac))
            for match in aps_mac:
                outfile.write('%s\n' % match)
        print('\n--> Lista de MAC AP (%d en total):\n' % len(aps_mac))
        col = cmd.Cmd()
        col.columnize(aps_mac, displaywidth=80)

    def mostrar_clients(self):
        with open('clients_mac_output.txt', 'w') as outfile:
            outfile.write('-Lista de MAC Cliente (%d en total):\n'
                          % len(clients_mac))
            for match in clients_mac:
                outfile.write('%s\n' % match)
        print('\n--> Lista de MAC Cliente (%d en total):\n' % len(clients_mac))
        col = cmd.Cmd()
        col.columnize(clients_mac, displaywidth=80)

    def mostrar_users(self):
        with open('users_output.txt', 'w') as outfile:
            outfile.write('-Lista de Usuarios (%d en total):\n'
                          % len(users_list))
            for match in users_list:
                outfile.write('%s\n' % match)
        print('\n--> Lista de Usuarios (%d en total):\n' % len(users_list))
        col = cmd.Cmd()
        col.columnize(users_list, displaywidth=80)

    # Determinar AP con mayor tráfico
    def sumar_trafico(self):
        # Determinar rango de fechas para seguimiento del tráfico
        regx_date = re.compile(
                    r'(?:0?[1-9]|[12][0-9]|3[01])\/(?:0?[1-9]|1[012])\/\d{4}')
        while True:
            date_init = input('\n--> Ingrese fecha de inicio en formato'
                              ' dd/mm/yyyy: ')
            if regx_date.match(date_init):
                break
            else:
                warnings.warn('La expresión ingresada no es válida.',
                              stacklevel=3)
        d_init = datetime.strptime(date_init, '%d/%m/%Y')
        while True:
            date_end = input('\n--> Ingrese fecha de finalización en formato'
                             ' dd/mm/yyyy: ')
            if regx_date.match(date_end):
                break
            else:
                warnings.warn('La expresión ingresada no es válida.',
                              stacklevel=3)
        d_end = datetime.strptime(date_end, '%d/%m/%Y')
        # Sumar tráfico correspondiente a cada AP
        regx_trafico = re.compile(r'(?<=;)\d*(?=;)')
        regx_corrupto = re.compile(r'(?<=;)\\N(?=;)')
        with open('acts-user1.txt', 'r') as infile:
            while True:
                linea = infile.readline()
                if len(linea) == 0:
                    infile.close
                    break
                if regx_corrupto.search(linea):
                    continue
                if regx_date.search(linea) is None:
                    continue
                d_mid = datetime.strptime(regx_date.findall(linea)[1],
                                          '%d/%m/%Y')
                if d_init <= d_mid <= d_end:
                    for match in aps_mac:
                        if match in linea:
                            trafico_dict[match] = trafico_dict[match] + \
                                                int(regx_trafico.findall
                                                    (linea)[1]) + \
                                                int(regx_trafico.findall
                                                    (linea)[2])
                            break
        # Guardar en un archivo de texto el tráfico de cada AP
        with open('aps_traffic_output.txt', 'w') as outfile:
            outfile.write('-Tráfico (octetos) de cada AP entre %s y %s:\n'
                          '(Orden descendente)\n' % (date_init, date_end))
            for match in dict(sorted(trafico_dict.items(), key=lambda
                                     item: item[1], reverse=True)):
                outfile.write('%s: %d\n' % (match, trafico_dict[match]))
        max_trafico = max(trafico_dict, key=trafico_dict.get)
        print('\n--> El AP de MAC %s es el que más tráfico (%s octectos) ha'
              ' tenido.' % (max_trafico, trafico_dict[max_trafico]))


if __name__ == '__main__':
    # Definir expresiones regulares para direcciones MAC y usuarios
    regx_aps = re.compile(r'(?:[A-F\d]{2}-){5}[A-F\d]{2}:UM', re.I)
    regx_clients = re.compile(r'(?:[A-F\d]{2}-){5}[A-F\d]{2}$', re.M | re.I)
    regx_users = re.compile(r'(?<=;)[A-Z-.]{1,30}(?=;)', re.I)

    # Leer archivo de texto y buscar direcciones MAC y usuarios
    with open('acts-user1.txt', 'r') as infile:
        text_file = infile.read()
        aps_mac = re.findall(regx_aps, text_file)
        clients_mac = re.findall(regx_clients, text_file)
        users_list = regx_users.findall(text_file, 121)

    # Eliminar direcciones MAC y usuarios duplicados
    aps_mac = list(set(aps_mac))
    clients_mac = list(set(clients_mac))
    users_list = list(set(users_list))

    # Crear diccionario que guardará el número de tráfico de c/AP
    trafico_dict = dict()
    for match in aps_mac:
        trafico_dict[match] = 0
    trafico = Trafico()
    # Llamar al menú para inicializar el programa
    while True:
        opcion_menu = trafico.menu_trafico()
        if opcion_menu == '1':
            trafico.mostrar_aps()
        elif opcion_menu == '2':
            trafico.mostrar_clients()
        elif opcion_menu == '3':
            trafico.mostrar_users()
        elif opcion_menu == '4':
            trafico.sumar_trafico()
        else:
            print('\nCerrando programa.\n')
            break
