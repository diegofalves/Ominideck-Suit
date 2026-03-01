#!/bin/bash

echo "🚀 Iniciando build do OmniDeck Suite..."

# Parar em caso de erro
set -e

PROJECT_NAME="OmniDeck Suite"
APP_NAME="OmniDeck Suite.app"
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "🧭 Registrando PROJECT_ROOT para app desktop..."
mkdir -p "$HOME/.omnideck"
echo "$PROJECT_ROOT" > "$HOME/.omnideck/project_root.txt"
echo "📌 PROJECT_ROOT: $PROJECT_ROOT"

echo "🧹 Limpando builds anteriores..."
cd "$PROJECT_ROOT"
rm -rf build dist

cd "$PROJECT_ROOT"
echo "📦 Gerando novo bundle..."
pyinstaller omni_launcher.spec --clean

echo "🧽 Removendo atributos estendidos..."
xattr -cr "dist/$APP_NAME"

echo "🔐 Assinando app (ad-hoc)..."
codesign --force --deep --sign - "dist/$APP_NAME"

echo "📂 Substituindo versão em /Applications..."
rm -rf "/Applications/$APP_NAME"
mv "dist/$APP_NAME" /Applications/

echo "✅ Build concluído com sucesso!"
echo "📍 App instalado em /Applications/$APP_NAME"