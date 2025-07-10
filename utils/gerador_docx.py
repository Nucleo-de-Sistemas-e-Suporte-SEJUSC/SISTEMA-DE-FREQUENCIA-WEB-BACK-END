def preencher_documento(doc, mapeamento_dados):
    """
    Substitui múltiplos placeholders em um documento (.docx) com base em um dicionário de mapeamento.
    Esta função funciona de forma robusta tanto em parágrafos simples quanto em tabelas,
    preservando a formatação original.
    
    :param doc: O objeto do documento python-docx.
    :param mapeamento_dados: Um dicionário onde as chaves são os placeholders (ex: "CAMPO_NOME")
                              e os valores são os dados para substituição.
    """
    # Lista de todos os parágrafos (incluindo os que estão dentro das tabelas)
    all_paragraphs = list(doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    all_paragraphs.append(paragraph)

    # Itera sobre o mapeamento e substitui em todos os parágrafos
    for key, value in mapeamento_dados.items():
        for p in all_paragraphs:
            # A substituição precisa ser feita nos 'runs' para preservar a formatação
            if key in p.text:
                inline = p.runs
                # Substitui o texto preservando a formatação do primeiro 'run'
                for i in range(len(inline)):
                    if key in inline[i].text:
                        text = inline[i].text.replace(key, str(value) if value is not None else "")
                        inline[i].text = text