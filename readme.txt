### 🔍 Projeto de Pipeline de Dados com Arquitetura Medallion
Este projeto tem como objetivo construir uma pipeline de dados que consome informações de uma API pública, realiza transformações e persiste os dados em um data lake, seguindo o padrão arquitetura Medallion, com três camadas:

Bronze (bronzelayer): armazenamento dos dados brutos coletados diretamente da fonte.

Silver (silverlayer): dados curados, colunar, particionados por localização.

Gold (goldlayer): camada analítica agregada, com dados prontos para consumo por ferramentas de BI ou análises mais complexas.

### ⚙️ Ferramentas Utilizadas
Todo o ecossistema foi construído com ferramentas open source e escaláveis, permitindo fácil adaptação a ambientes maiores e produtivos:

Docker

Apache Airflow

MinIO (Data Lake)

DuckDB

DBeaver (client SQL)

Python + PySpark

### 📈 Monitoramento e Qualidade dos Dados
Para garantir a confiabilidade do pipeline, seria possível implementar um sistema de monitoramento composto por:

Alertas automáticas via Email ou outros canais, integrados ao Airflow, em caso de falhas de execução.

Validações de schema e integridade dos dados nas etapas de transformação.

Controle de logs salvos em arquivos e visualização dos dashboards de execução no Airflow UI.

Dashboards de qualidade de dados dependendo da criticidade do pipeline.

### 🔐 Sobre as Credenciais
As credenciais de acesso estão expostas no repositório com o único propósito de facilitar testes locais. Em produção, recomenda-se utilizar:

Gerenciadores de segredo (como HashiCorp Vault, AWS Secrets Manager, Databricks Secrets, GCP Secret Manager)

Variáveis de ambiente seguras

Criptografia de arquivos de configuração

### ▶️ Passo a passo para execução

1. **Pré-requisitos**:
   - Instale o [Docker](https://www.docker.com)
   - Instale o Python 3.9 ou superior
   - Instale o DBeaver ou outra ferramenta compatível com DuckDB: [https://dbeaver.io]

2. **Instale o Astro no PowerShell (Windows)** com o comando:
   ```
   winget install -e --id Astronomer.Astro
   ```
   **O que é Astro?**
   > O Astro é uma solução em nuvem que ajuda você a gastar menos tempo gerenciando o Apache Airflow®, com recursos que permitem criar, executar e observar dados em um só lugar.

3. **Clone o repositório GitHub** no editor de sua preferência:
   [https://github.com/Gabriel-Curvelo/BeesDataEngineering-Project]

4. **No terminal, vá até a pasta `Airflow` e execute:**
   ```
   astro dev start
   ```
   Esse comando criará um container com:
   - Airflow: plataforma de gerenciamento de fluxos de trabalho.
   - DuckDB: sistema de banco de dados colunar embutido.

5. **Acesse o Airflow** via:
   http://localhost:8080
   Usuário: `admin` | Senha: `admin`
   > ⚠️ Credenciais expostas propositalmente para ambiente de desenvolvimento local. Essas senhas são fornecidas pela própria documentação do Astro.

6. **Agora vá até a pasta `DataLake` e execute:**
   ```bash
   docker-compose up -d
   ```
   Esse comando criará um container com o **MinIO**: plataforma de armazenamento de arquivos compatível com S3.

7. **Acesse o MinIO** via:
   http://localhost:9001
   Usuário: `datalake` | Senha: `datalake`

8. **Crie os buckets no modelo Medallion** com os nomes:
   - `bronzelayer`
   - `silverlayer`
   - `goldlayer`

9. **No Airflow, execute a DAG `brewery`.**

10. **Ao término da execução, os dados estarão carregados nas respectivas camadas.**

### 📊 Extra: Visualização dos Dados

Para facilitar a visualização dos dados na camada Gold, foi utilizado o DuckDB. Ao final da execução da DAG, será gerado um arquivo no caminho:

```
\BeesDataEngineering-Project\Airflow\include\minio.duckdb
```

Você pode:

- Copiar esse arquivo para uma pasta de sua preferência
- Abrir o DBeaver e criar uma conexão direta com DuckDB
- Utilizar o caminho copiado como path do banco de dados DuckDB
- Visualizar os dados e gerar consultas SQL como desejar

**Alternativamente**, é possível configurar o acesso S3 diretamente no DuckDB (sem baixar o arquivo), assim como é feito com o boto3, para acessar os dados diretamente da camada Gold no MinIO.

---

### 📂 Organização dos Scripts

- **Scripts dos ETLs**: `\BeesDataEngineering-Project\Airflow\include\scripts`
- **Scripts das DAGs**: `\BeesDataEngineering-Project\Airflow\dags`

                      




