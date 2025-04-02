from datetime import datetime, date
import calendar
import re

def data_atual(mes_informado_pelo_usuario=None):
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    try:
        # Se receber formato YYYY-MM
        if mes_informado_pelo_usuario and re.match(r'^\d{4}-\d{2}$', mes_informado_pelo_usuario):
            ano_str, mes_str = mes_informado_pelo_usuario.split('-')
            ano = int(ano_str)
            mes_numerico = int(mes_str)
            
            if not 1 <= mes_numerico <= 12:
                raise ValueError
                
            mes_por_extenso = meses[mes_numerico - 1]
            
        # Se não receber mês ou formato inválido
        else:
            data_atual = datetime.now()
            ano = data_atual.year
            mes_numerico = data_atual.month
            mes_por_extenso = meses[mes_numerico - 1]
            
    except (ValueError, AttributeError, IndexError):
        data_atual = datetime.now()
        ano = data_atual.year
        mes_numerico = data_atual.month
        mes_por_extenso = meses[mes_numerico - 1]

    return {
        "ano": ano,
        "mes": mes_por_extenso,
        "mes_numerico": mes_numerico
    }

def pega_quantidade_dias_mes(ano, mes):
    _, numero_dias = calendar.monthrange(ano, mes)
    return numero_dias

def pega_final_de_semana(ano, mes, dia):
    return date(ano, mes, dia).weekday()  # 0=segunda, 5=sábado, 6=domingo
