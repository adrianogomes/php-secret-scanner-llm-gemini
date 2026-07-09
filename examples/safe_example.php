<?php

// Exemplo seguro.
// As credenciais são carregadas por variáveis de ambiente.

$dbUser = getenv("DB_USER");
$dbPassword = getenv("DB_PASSWORD");
$apiKey = getenv("API_KEY");

echo "Configuração carregada por variáveis de ambiente.";