### README.md

```markdown
# Custom Nginx RPM with WebDAV, HTTP/2, SSL, and PHP-FPM Authentication

This repository provides a custom build of Nginx with WebDAV, HTTP/2, SSL support, and PHP-FPM for authentication using MySQL. This build removes the Lua and LuaJIT dependencies and adds necessary modules for the specified functionalities.

## Included Modules

The following modules are included in this custom Nginx build:

- **HTTP SSL Module**: Provides support for SSL/TLS.
- **HTTP DAV Module**: Adds support for WebDAV.
- **HTTP/2 Module**: Enables HTTP/2 support.
- **Threads**: Allows threading support.
- **Stream Module**: Adds support for TCP/UDP proxying and load balancing.
- **Stream SSL Module**: Provides SSL/TLS support for the stream module.
- **File AIO**: Enables asynchronous I/O.
- **HTTP Perl Module**: Allows the use of Perl scripts within Nginx.

## Building the RPM

### Prerequisites

Ensure you have the necessary build tools and dependencies installed:

```sh
sudo dnf install -y gcc pcre-devel zlib-devel openssl-devel make systemd libxslt-devel gd-devel GeoIP-devel perl-devel perl-ExtUtils-Embed mariadb-devel php-fpm php-mysqlnd
```

### Directory Structure

Create the required directory structure for building the RPM:

```sh
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
```

### Sources

Place the following files in the `~/rpmbuild/SOURCES/` directory:

- `nginx-1.27.0.tar.gz`: [Download Nginx Source](http://nginx.org/download/nginx-1.27.0.tar.gz)
- `nginx.service`: Systemd service file
- `auth.php`: PHP script for authentication

### Spec File

Place the following SPEC file in the `~/rpmbuild/SPECS/` directory as `nginx.spec`:

```specfile
Name:           nginx
Version:        1.27.0
Release:        1%{?dist}
Summary:        High-performance web server and reverse proxy server

License:        BSD
URL:            http://nginx.org/
Source0:        http://nginx.org/download/nginx-%{version}.tar.gz
Source1:        nginx.service
Source2:        auth.php

BuildRequires:  gcc
BuildRequires:  pcre-devel
BuildRequires:  zlib-devel
BuildRequires:  openssl-devel
BuildRequires:  make
BuildRequires:  systemd
BuildRequires:  libxslt-devel
BuildRequires:  gd-devel
BuildRequires:  GeoIP-devel
BuildRequires:  perl-devel
BuildRequires:  perl-ExtUtils-Embed
BuildRequires:  mariadb-devel

Requires:       pcre
Requires:       zlib
Requires:       openssl
Requires:       systemd
Requires:       php-fpm
Requires:       php-mysqlnd
Requires:       mysql-server
Requires:       mysql

%description
Nginx is a high-performance web server and reverse proxy server.

%prep
%setup -q

%build
CFLAGS="$CFLAGS -fPIE -fPIC" \
LDFLAGS="$LDFLAGS -pie" \
./configure --prefix=%{_prefix} \
            --sbin-path=%{_sbindir}/nginx \
            --conf-path=%{_sysconfdir}/nginx/nginx.conf \
            --pid-path=%{_localstatedir}/run/nginx.pid \
            --lock-path=%{_localstatedir}/lock/nginx.lock \
            --http-log-path=%{_localstatedir}/log/nginx/access.log \
            --error-log-path=%{_localstatedir}/log/nginx/error.log \
            --with-http_ssl_module \
            --with-http_dav_module \
            --with-http_v2_module \
            --with-threads \
            --with-stream \
            --with-stream_ssl_module \
            --with-file-aio \
            --with-http_perl_module \
            --with-perl_modules_path=%{_libdir}/perl5/vendor_perl \
            --with-perl=%{_bindir}/perl \
            --with-cc-opt="-I/usr/include" \
            --with-ld-opt="-L/usr/lib64"

make

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

# Install systemd service file
install -m 644 %{SOURCE1} $RPM_BUILD_ROOT/usr/lib/systemd/system/nginx.service

# Install PHP auth file
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT/var/www/html/auth.php

%files
%{_sbindir}/nginx
%{_sysconfdir}/nginx/nginx.conf
%{_localstatedir}/run/nginx.pid
%{_localstatedir}/lock/nginx.lock
%{_localstatedir}/log/nginx/access.log
%{_localstatedir}/log/nginx/error.log
/usr/lib/systemd/system/nginx.service
/var/www/html/auth.php

%changelog
* Fri Jun 14 2024 Your Name <your.email@example.com> - 1.27.0-1
- Custom build of Nginx with WebDAV, HTTP/2, SSL, and PHP-FPM support for authentication.
```

### Auth.php

```php
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
?>
```

### Example MySQL Database Setup

1. **Create a new database:**

   ```sql
   CREATE DATABASE webdav_auth;
   ```

2. **Create a new user and grant privileges:**

   ```sql
   CREATE USER 'your_db_username'@'localhost' IDENTIFIED BY 'your_db_password';
   GRANT ALL PRIVILEGES ON webdav_auth.* TO 'your_db_username'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Create the users table:**

   ```sql
   USE webdav_auth;

   CREATE TABLE users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       username VARCHAR(255) NOT NULL UNIQUE,
       password VARCHAR(255) NOT NULL
   );
   ```

4. **Insert a sample user:**

   Use PHP to hash the password and then insert it into the database:

   ```php
   <?php
   $password = password_hash('user_password', PASSWORD_BCRYPT);
   echo $password;
   ?>
   ```

   Copy the output and use it in the following SQL command:

   ```sql
   INSERT INTO users (username, password) VALUES ('example_user', '$2y$10$abcdefghijklmnopqrstuv');
   ```

### Building the RPM

Build the RPM with the following command:

```sh
rpmbuild -ba ~/rpmbuild/SPECS/nginx.spec
```

### Installing the RPM

Install the newly built RPM:

```sh
sudo dnf localinstall ~/rpmbuild/RPMS/x86_64/nginx-1.27.0-1.el9.x86_64.rpm
```

### Configuring and Starting Nginx

Check the configuration and start Nginx:

```sh
sudo nginx -t
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Nginx Configuration

#### nginx.conf

```nginx
# For more information on configuration, see:
#   * Official English Documentation: http://nginx.org/en/docs/
#   * Official Russian Documentation: http://nginx.org/ru/docs/

user nginx;
worker_processes auto;
worker_rlimit_nofile 10000;
error_log /var/log/nginx/error.log;
pid /var/run/nginx.pid;

# Load dynamic modules. See /usr/share/nginx/README.fedora.
include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 4096;
    multi_accept on;
    use epoll;
}

http {

    charset utf-8;
    server_tokens       off;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for" **$request_time/$upstream_response_time**';

    access_log  /var/log/nginx/access.log  main;

    sendfile                    on;
    tcp_nopush                  on;
    tcp_nodelay                 on;
    keepalive_timeout           24s;
    types_hash_max_size         2048;
    keepalive_requests          100000;
    reset_timedout_connection   on;

    send_timeout                2s;
    client_body_timeout         10s;
    proxy_connect_timeout       10s;
    proxy_send_timeout          10s;
    proxy_read_timeout          10s;

    client_max_body_size        8M;

    gzip                        on;
    gzip_static                 on;
    gzip_http_version           1.1;
    gzip_comp_level             6;
    gzip_min_length             1024;
    gzip_vary                   on;
    gzip_proxied                any;
    gzip_buffers                16 8k;
    gzip_types
        application/atom+xml
        application/javascript
        application/json
        application/rss+xml
        application/vnd.ms-fontobject
        application/x-font-ttf
        application/x-web-app-manifest+json
        application/xhtml+xml
        application/xml
        font/opentype
        image/png
        image/jpeg
        image/svg+xml
        image/x-icon
        text/css
        text/plain
        text/javascript
        text/x-component;
    gzip_disable "MSIE [1-6]\.(?!.*SV1)";

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    server_names_hash_bucket_size 100;

    # map the list of user agents must escape ( with \(
    map $http_user_agent $mobile_user {
        default "WPBULLET_DESKTOP";
        # Android
        "~Mozilla/5.0 \(Linux; Android" WPBULLET_MOBILE;
        # Opera
        "~Opera Mini" WPBULLET_MOBILE;
        # iOS
        "~Mozilla/5.0 \(iPhone" WPBULLET_MOBILE;
        # Windows Phone
        "~Mozilla/5.0 \(Windows Phone" WPBULLET_MOBILE;
    }

    fastcgi_cache_path          /var/nginx/cache_store levels=1:2 keys_zone=TCC:512m max_size=1000m inactive=20m;
    fastcgi_cache_key           "$scheme$request_method$host$request_uri$mobile_user";
    fastcgi_cache_valid         200 301 302 10m;
    fastcgi_cache               TCC;
    fastcgi_cache_lock          on;
    fastcgi_cache_use_stale     error timeout invalid_header updating http_500;
    fastcgi_ignore_headers      Cache-Control Expires Set-Cookie;
    #fastcgi_buffering          off;
    #fastcgi_request_buffering  off;
    fastcgi_buffer_size         128k;
    fastcgi_buffers             256 16k;
    proxy_cache_bypass          $cookie_nocache $arg_nocache;
    fastcgi_cache_methods       GET HEAD;

    #Set cache default tot false
    map $host$request_uri $no_cache {
        default 1;
    }

    map $http_upgrade $connection_upgrade {
        default upgrade;
        '' close;
    }

    add_header X-Cache          $upstream_cache_status always;

    # Load modular configuration files from the /etc/nginx/conf.d directory.
    # See http://nginx.org/en/docs/ngx_core_module.html#include
    # for more information.
    include /etc/nginx/conf.d/*.conf;
}
```

#### Virtual Host Configuration

```nginx
server {
    listen [::]:443 ssl;
    http2 on;

    server_name storage.example.com;

    # Load configuration files for the default server block.
    include /etc/nginx/ssl_params.conf;

    location = /auth {
        internal;
        index auth.php;
        fastcgi_pass unix:/run/php-fpm/www.sock;
        fastcgi_param SCRIPT_FILENAME /etc/nginx/conf.d/auth.php;
        include fastcgi_params;
    }

    location ~ \.php$ {
        index auth.php;
        fastcgi_pass unix:/run/php-fpm/www.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location / {
        root /home/storage/webdav;
        dav_methods PUT DELETE MKCOL COPY MOVE;
        dav_ext_methods OPTIONS PROPFIND;
        create_full_put_path on;
        dav_access user:rw group:rw;
        autoindex on; # Enable directory listing
        auth_request /auth;
    }

    access_log /var/log/nginx/webdav_access.log debug_log_format;
    error_log /var/log/nginx/webdav_error.log debug;

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/storage.example.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/storage.example.com/privkey.pem; # managed by Certbot
}

server {
    if ($host = storage.example.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    server_name storage.example.com;
    listen 80;
    return 404; # managed by Certbot
}
```

### Testing the Configuration

Test access to your WebDAV server and verify that authentication is working. Check the logs for any errors:

```sh
sudo tail -f /var/log/nginx/error.log
```

## Troubleshooting

If you encounter issues, check the following:

- Ensure that PHP-FPM is running: `sudo systemctl status php-fpm`
- Verify MySQL connection details in `auth.php`
- Check Nginx error logs for detailed error messages: `sudo tail -f /var/log/nginx/error.log`

Feel free to open an issue if you encounter any problems or have any questions.
```

Plaats deze `README.md` file in de root directory van je project. Deze handleiding zorgt ervoor dat alle benodigde informatie voor het bouwen, installeren en configureren van de aangepaste Nginx RPM beschikbaar is.
