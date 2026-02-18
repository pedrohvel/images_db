#!/bin/bash
# AURA-SYS: Monitoramento Contínuo de Ingestão de Dados

DIR="images/"

echo "STATUS: O olho sintético está monitorando a pasta [$DIR]..."

while true; do
  # O sistema entra em suspensão até que um arquivo seja criado ou movido para a pasta
  inotifywait -qq -e create -e moved_to "$DIR"
  
  echo "EVENTO: Novo asset detectado. Aguardando estabilização de I/O (5s)..."
  sleep 5
  
  # Orquestração automática
  git add "$DIR"
  git commit -m "sys-auto: ingestão neural de novos assets"
  git push origin main
  
  echo "STATUS: Pipeline concluído. Voltando ao estado de vigília."
done