1. Instale o docker link:
2. Instale o Astro como adm, com o comando : winget install -e --id Astronomer.Astro
        O que é Astro?
                    O Astro é uma solução em nuvem que ajuda você a se concentrar em seus pipelines de dados 
                    e gastar menos tempo gerenciando o Apache Airflow®,
                    com recursos que permitem criar, executar e observar dados em um só lugar.
4. Clone o repositorio no editor de sua preferência: 
5. Dentro da pasta Airflow execute astro dev init
5. astro config set container.binary docker -g
6. astro dev start
7. Agora na pasta DataLake
8. execute o comando docker-compose up -d
        - Esse comando irá criar um container com a simulação de uma stack de datalake, utilizando as seguintes ferramentas:
            MinIO: Armazenamento de arquivos (S3 compatível)
            PostgreSQL: Banco de metadados do Hive
            Hive Metastore: Catálogo dos dados (como tabelas, partições etc.)
            Trino: Engine de consultas SQL distribuídas
9. Acesse o MinIO : http://localhost:9001
10. Crie os Buckest em modelo medalha: goldlayer, silverlayer e bronzelayer
11. Após criar os buckets, remova o container e crie novamente com os comandos: docker-compose down     docker-compose up -d 
         Agora todos os serviços estaram funcionando! 


         docker network connect airflow_8983c3_airflow trino
         astro dev restart      



                      




