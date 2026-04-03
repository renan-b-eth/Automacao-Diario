# Automação Diária - Escolas Públicas

Sistema completo de automação e monitoramento para gestão de escolas públicas.

## Desenvolvedor

**Renan Bezerra** - Programador e empreendedor

### Projetos

- **Rendey Class** - Plataforma educacional
- **EstaHub** - Hub de tecnologia educacional
- **EStaTHon** - Hackathon das Escolas Estaduais

### Contato

- Site: [site-renanbezerra.vercel.app](https://site-renanbezerra.vercel.app/)

## Stack Tecnológico

- **Backend**: Python (Flask)
- **Frontend**: HTML/CSS/JavaScript (Bootstrap 5)
- **Banco de Dados**: SQLite
- **Hospedagem**: Vercel

## Funcionalidades

- Login institucional com 3 níveis de acesso
- Dashboard personalizado
- Gerenciamento de professores
- Visualização de horários
- Monitor de processos seletivos
- Gestão de usuários (apenas GOE)

## Níveis de Acesso

1. **GOE** - Gestor de Organização Escolar (Admin total)
2. **Diretor** - Diretor da unidade
3. **Inspetor** - Inspetor de alunos

## Deploy no Vercel

1. Crie uma conta no [Vercel](https://vercel.com)
2. Importe este repositório
3. O Vercel detectará automaticamente o Flask
4. Configure as variáveis de ambiente (opcional)
5. Deploy automático!

## Credenciais de Acesso (Desenvolvimento)

- GOE: admin / admin123
- Diretor: diretor / diretor123
- Inspetor: inspetor / inspetor123

## Instalação Local

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install flask

# Executar
python app.py
```

Acesse: http://localhost:5000