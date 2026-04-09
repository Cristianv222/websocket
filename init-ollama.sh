#!/bin/bash

echo "Esperando a que Ollama inicie..."
while ! curl -s http://ollama:11434/api/tags > /dev/null; do
  sleep 2
done

echo "Descargando el modelo Mistral (esto puede tardar unos minutos)..."
curl -X POST http://ollama:11434/api/pull -d '{"name": "mistral"}'

echo "Modelo descargado con éxito."
