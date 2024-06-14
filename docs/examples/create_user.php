<?php
//Username
if(stristr($argv[1], "=") === false){
    $username = $argv[1];
}else {
    list($key, $value) = explode('=', $argv[1]);
    $username = $value;
}

if(stristr($argv[2], "=") === false){
    $password = $argv[2];
}else {
    list($key, $value) = explode('=', $argv[2]);
    $password = $value;
}

echo $password."\r\n";
$password = password_hash($password, PASSWORD_BCRYPT);

echo "INSERT INTO users (username, password) VALUES ('{$username}', '{$password}');\r\n";

