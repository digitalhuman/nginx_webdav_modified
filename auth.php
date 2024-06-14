<?php
header('Content-Type: text/plain');

$dsn = 'mysql:host=localhost;dbname=webdav_auth';
$username = 'your_db_username';
$password = 'your_db_password';

try {
    $dbh = new PDO($dsn, $username, $password);
    $dbh->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    if (!isset($_SERVER['PHP_AUTH_USER'])) {
        header('WWW-Authenticate: Basic realm="Restricted"');
        header('HTTP/1.0 401 Unauthorized');
        echo 'Authentication required';
        exit;
    }

    $stmt = $dbh->prepare("SELECT password FROM users WHERE username = :username");
    $stmt->bindParam(':username', $_SERVER['PHP_AUTH_USER']);
    $stmt->execute();
    $row = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($row && password_verify($_SERVER['PHP_AUTH_PW'], $row['password'])) {
        echo 'Authenticated';
    } else {
        header('WWW-Authenticate: Basic realm="Restricted"');
        header('HTTP/1.0 401 Unauthorized');
        echo 'Authentication failed';
        exit;
    }
} catch (PDOException $e) {
    echo 'Connection failed: ' . $e->getMessage();
}

header('WWW-Authenticate: Basic realm="Restricted"');
header('HTTP/1.0 401 Unauthorized');
echo 'Authentication failed';
exit;