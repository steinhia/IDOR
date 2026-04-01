#!/bin/bash

# Substitua pelo ID da sua instância EC2
## Projeto CNE
INSTANCE_ID="i-0e01caf7837c38d79"

# Função para iniciar a instância
start_instance() {
    echo "Iniciando a instância $INSTANCE_ID..."
    aws ec2 start-instances --instance-ids $INSTANCE_ID
    echo "Instância $INSTANCE_ID iniciada com sucesso."
}

# Função para parar a instância
stop_instance() {
    echo "Parando a instância $INSTANCE_ID..."
    aws ec2 stop-instances --instance-ids $INSTANCE_ID
    echo "Instância $INSTANCE_ID parada com sucesso."
}

# Função para reiniciar a instância
restart_instance() {
    echo "Reiniciando a instância $INSTANCE_ID..."
    aws ec2 reboot-instances --instance-ids $INSTANCE_ID
    echo "Instância $INSTANCE_ID reiniciada com sucesso."
}

# Exibir menu de opções
echo "Selecione uma opção:"
echo "1 - Iniciar Instância"
echo "2 - Parar Instância"
echo "3 - Reiniciar Instância"
read -p "Escolha uma opção (1/2/3): " OPTION

case $OPTION in
    1)
        start_instance
        ;;
    2)
        stop_instance
        ;;
    3)
        restart_instance
        ;;
    *)
        echo "Opção inválida!"
        ;;
esac
