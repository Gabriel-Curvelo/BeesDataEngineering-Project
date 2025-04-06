1. Pré requisitos: Instale o docker link: https://www.docker.com
                   Instale Python 3.9 ou superior
                   Dbeaver ou outra ferramente compatível com Duckdb: https://dbeaver.io
2. Instale o Astro como adm, no PowerShell(para sistema windows), com o comando : winget install -e --id Astronomer.Astro
        O que é Astro?
                    O Astro é uma solução em nuvem que ajuda você a gastar menos tempo gerenciando o Apache Airflow®,
                    com recursos que permitem criar, executar e observar dados em um só lugar.

3. Clone o repositorio github, no editor de sua preferência: https://github.com/Gabriel-Curvelo/BeesDataEngineering-Project 
4. No terminal, se direcione a pasta Airflow e execute: astro dev start
        - Esse comando irá criar um container com: 
                Airflow: Paltaforma de gerenciamento de fluxos de trabalho.
                Duckdb: Sistema de gerenciamento de banco de dados orientado a coluna.

5. Acesse o Airflow: http://localhost:8080 user: admin senha: admin 
obs: Chave exposta por se tratar de um ambiente localhost de desenvolvimento, essas senhas são fornecidas na própria documentação do Astro.
6. Agora no terminal, se direcione a pasta DataLake e execute: docker-compose up -d
        - Esse comando irá criar um container com o MinIO: Paltaforma de armazenamento de arquivos (S3 compatível)
9. Acesse o MinIO : http://localhost:9001
10. Crie os Buckest em modelo medalha, com os nomes: goldlayer, silverlayer e bronzelayer
11. No airflow, execute a dag brewery.
12. Ao termino da execução, os dados estarão carregados em suas devidas camadas.

Extra: Para permitir a vizualização dos dados de forma prática, na camada gold, foi utilizado o Duckdb.
Nessa aplicação, o Duckdb gera um arquivo ao final da execução, no caminho \BeesDataEngineering-Project\Airflow\include\minio.duckdb
Copie esse arquivo em uma pasta de sua preferencia, e use o path no DBeaver, usando conexão direta do Duckdb, 
para visualização dos dados e gerar consultas SQl como preferir.
E possível também configurar o acesso S3 dentro do DuckDB, assim como é feito em um cliente como boto3,
para vizualizar os dados do Dbeaver diretamente da camada gold, no MinIO.

A stack completa é Docker, Airflow, MinIO, Duckdb e Dbeaver

Importante:
Os scripts com os ETLs, estão no caminho: \BeesDataEngineering-Project\Airflow\include\scripts
Os scripts com as DAGs, estão no caminho: \BeesDataEngineering-Project\Airflow\dags
     



                      




