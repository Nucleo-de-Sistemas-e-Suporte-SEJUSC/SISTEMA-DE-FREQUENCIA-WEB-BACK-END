from datetime import datetime, date
import calendar

def data_atual(mes_informado_pelo_usuario=None):
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    ano = date.today().year

    if mes_informado_pelo_usuario:
        mes_por_extenso = mes_informado_pelo_usuario
        mes_numerico = meses.index(mes_por_extenso) + 1
    else:
        mes_numerico = date.today().month
        mes_por_extenso = meses[mes_numerico-1]

    return {
        "ano": ano,
        "mes": mes_por_extenso,
        "mes_numerico": mes_numerico
    }

def pega_quantidade_dias_mes(ano, mes):
    _, numero_dias = calendar.monthrange(ano, mes)
    return numero_dias

def pega_final_de_semana(ano, mes, dia):
    dia_semana = date(ano, mes, dia).weekday()
    return dia_semana
