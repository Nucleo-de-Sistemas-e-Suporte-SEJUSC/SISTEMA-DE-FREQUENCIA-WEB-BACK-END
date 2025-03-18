def muda_texto_documento(doc, texto_antigo, novo_texto):
    for paragraph in doc.paragraphs:
        if texto_antigo in paragraph.text:
            paragraph.text = paragraph.text.replace(texto_antigo, novo_texto)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if texto_antigo in cell.text:
                    cell.text = cell.text.replace(texto_antigo, novo_texto)