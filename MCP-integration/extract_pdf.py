import pdfplumber

pdf_path = r'C:\onedirve\OneDrive\Desktop\Azure\AI-103\Lab\Custom\MCP-integration\Extend agents with Model Context Protocol (MCP) tools _ Develop AI Agents in Azure.pdf'

with pdfplumber.open(pdf_path) as pdf:
    with open(r'C:\onedirve\OneDrive\Desktop\Azure\AI-103\Lab\Custom\MCP-integration\pdf_output.txt', 'w', encoding='utf-8') as out:
        out.write(f'Total pages: {len(pdf.pages)}\n')
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            out.write(f'--- PAGE {i+1} ---\n')
            if text:
                out.write(text)
                out.write('\n')
            else:
                out.write('(no text extracted)\n')
            out.write('\n')
print('Done')