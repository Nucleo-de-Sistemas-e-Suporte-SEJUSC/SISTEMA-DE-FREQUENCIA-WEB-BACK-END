import subprocess
import os
import uuid

def convert_to_pdf(input_path, output_folder):
    """
    Converte um arquivo (como .xlsx ou .docx) para PDF usando o LibreOffice.

    :param input_path: Caminho completo para o arquivo de entrada.
    :param output_folder: Pasta onde o PDF será salvo.
    :return: O caminho completo para o PDF gerado ou None em caso de falha.
    """
    if not os.path.exists(input_path):
        print(f"Erro de conversão: Arquivo de entrada não encontrado em '{input_path}'")
        return None

    # Comando para executar a conversão via LibreOffice em modo "headless" (sem interface gráfica)
    command = [
        'soffice',
        '--headless',
        '--convert-to',
        'pdf',
        '--outdir',
        output_folder,
        input_path
    ]

    print(f"Executando comando de conversão: {' '.join(command)}")

    try:
        # Executa o comando e espera ele terminar
        process = subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)
        
        # Log de sucesso
        print("Saída do LibreOffice (stdout):", process.stdout)
        
        # Descobre o nome do arquivo PDF gerado
        input_filename = os.path.basename(input_path)
        pdf_filename = os.path.splitext(input_filename)[0] + '.pdf'
        pdf_filepath = os.path.join(output_folder, pdf_filename)

        if os.path.exists(pdf_filepath):
            # Renomeia para um nome único para evitar conflitos
            unique_filename = f"{uuid.uuid4()}.pdf"
            unique_filepath = os.path.join(output_folder, unique_filename)
            os.rename(pdf_filepath, unique_filepath)
            
            print(f"Conversão para PDF bem-sucedida! Arquivo salvo em: {unique_filepath}")
            return unique_filepath
        else:
            print("Erro de conversão: O arquivo PDF não foi encontrado após a execução do comando.")
            print("Saída de erro do LibreOffice (stderr):", process.stderr)
            return None

    except FileNotFoundError:
        print("Erro de conversão: O comando 'soffice' não foi encontrado.")
        print("Verifique se o LibreOffice está instalado e no PATH do sistema.")
        return None
    except subprocess.CalledProcessError as e:
        print("Erro durante a execução do comando de conversão do LibreOffice.")
        print(f"Comando: {e.cmd}")
        print(f"Código de retorno: {e.returncode}")
        print(f"Saída (stdout): {e.stdout}")
        print(f"Erro (stderr): {e.stderr}")
        return None
    except subprocess.TimeoutExpired:
        print("Erro de conversão: O processo do LibreOffice demorou demais e foi finalizado (timeout).")
        return None
    except Exception as e:
        print(f"Um erro inesperado ocorreu durante a conversão para PDF: {e}")
        return None