def preencher_documento(doc, mapeamento_dados):
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